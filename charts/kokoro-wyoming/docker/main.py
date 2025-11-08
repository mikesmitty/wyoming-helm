#!/usr/bin/env python3
#
# Original source:
# https://github.com/nordwestt/kokoro-wyoming/raw/d0ad1a99e7bf8cd9bf09ade2dc44cd4c55e6d43f/src/main.py 

import argparse
import asyncio
import logging
import signal
from functools import partial
from typing import Optional

import kokoro_onnx.config
from wyoming.error import Error
from wyoming.server import AsyncEventHandler
from kokoro_onnx import Kokoro
from kokoro_onnx.log import log
import numpy as np

from wyoming.info import Attribution, TtsProgram, TtsVoice, TtsVoiceSpeaker, Describe, Info
from wyoming.server import AsyncServer
from wyoming.tts import Synthesize, SynthesizeStart, SynthesizeChunk, SynthesizeStop, SynthesizeStopped
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
import re

_LOGGER = log.getChild(__name__)
VERSION = "0.6.4" # x-release-please-version


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences using punctuation boundaries.
    
    Args:
        text: Input text to split
        
    Returns:
        List of sentences
        
    Example:
        >>> text = "Hello world! How are you? I'm doing great."
        >>> split_into_sentences(text)
        ['Hello world!', 'How are you?', "I'm doing great."]
    """
    # First normalize whitespace and clean the text
    text = ' '.join(text.strip().split())

    # Split on sentence boundaries
    pattern = r'(?<=[.!?])\s+'
    sentences = re.split(pattern, text)

    # Filter out empty strings and strip whitespace
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences


def get_model_voices(model: Kokoro) -> list[TtsVoice]:
    return [
        TtsVoice(
            name=voice_id,
            description=voice_id,
            attribution=Attribution(
                name="", url=""
            ),
            installed=True,
            version=None,
            languages=[
                "en" if voice_id.startswith("a") else
                "it" if voice_id.startswith("i") else
                "jp" if voice_id.startswith('j') else
                "cn" if voice_id.startswith('z') else
                "es" if voice_id.startswith('e') else
                "fr" if voice_id.startswith('f') else
                "hi" if voice_id.startswith("h") else "en"
            ],
            speakers=[
                TtsVoiceSpeaker(name=voice_id.split("_")[1])
            ]
        )
        for voice_id in model.voices.keys()
    ]


class KokoroEventHandler(AsyncEventHandler):
    def __init__(self, wyoming_info: Info, kokoro_instance,
                 cli_args,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.kokoro = kokoro_instance
        self.cli_args = cli_args
        self.args = args
        self.wyoming_info_event = wyoming_info.event()

        # Streaming state
        self.streaming_text_chunks = []
        self.streaming_voice = None
        self.streaming_speed = None
        self.streaming_lang = None
        self.streaming_audio_started = False

    def _parse_voice_settings(self, voice_obj):
        """
        Parse voice settings from Wyoming voice object.

        Returns:
            tuple: (voice_name, speed, lang)

        Speed can be specified via speaker parameter, e.g.:
        - speaker="speed_1.5" -> 1.5x speed
        - speaker="1.2" -> 1.2x speed
        - speaker=None -> default speed from CLI args
        """
        voice_name = "af_heart"  # default voice
        speed = self.cli_args.speed if hasattr(self.cli_args, 'speed') else 1.0

        if voice_obj:
            if voice_obj.name:
                voice_name = voice_obj.name

            # Check if speaker parameter contains speed override
            if hasattr(voice_obj, 'speaker') and voice_obj.speaker:
                speaker = voice_obj.speaker
                # Try to extract speed from speaker parameter
                # Supports formats: "speed_1.5", "1.5", "speed:1.5"
                try:
                    if speaker.startswith("speed_") or speaker.startswith("speed:"):
                        speed_str = speaker.split("_")[-1].split(":")[-1]
                        speed = float(speed_str)
                    else:
                        # Try direct float parsing
                        speed = float(speaker)
                except (ValueError, AttributeError):
                    # If parsing fails, use default speed
                    pass

        # Determine language from voice name
        lang = "en-us" if voice_name.startswith("a") else "en-gb"

        return voice_name, speed, lang

    async def handle_event(self, event: Event) -> bool:
        """Handle Wyoming protocol events."""
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        # Handle streaming TTS events (Wyoming 1.7.0+)
        if SynthesizeStart.is_type(event.type):
            try:
                return await self._handle_synthesize_start(event)
            except Exception as err:
                await self.write_event(
                    Error(text=str(err), code=err.__class__.__name__).event()
                )
                raise err

        if SynthesizeChunk.is_type(event.type):
            try:
                return await self._handle_synthesize_chunk(event)
            except Exception as err:
                await self.write_event(
                    Error(text=str(err), code=err.__class__.__name__).event()
                )
                raise err

        if SynthesizeStop.is_type(event.type):
            try:
                return await self._handle_synthesize_stop(event)
            except Exception as err:
                await self.write_event(
                    Error(text=str(err), code=err.__class__.__name__).event()
                )
                raise err

        # Handle legacy non-streaming synthesis (backward compatibility)
        if Synthesize.is_type(event.type):
            try:
                return await self._handle_synthesize(event)
            except Exception as err:
                await self.write_event(
                    Error(text=str(err), code=err.__class__.__name__).event()
                )
                raise err

        _LOGGER.warning("Unexpected event: %s", event)
        return True

    """Handle text to speech synthesis request."""

    async def _handle_synthesize(self, event: Event) -> Optional[bool]:
        try:
            synthesize = Synthesize.from_event(event)

            # Get voice settings with speed adjustment
            voice_name, speed, lang = self._parse_voice_settings(synthesize.voice)

            sentences = split_into_sentences(synthesize.text)

            i = 0
            t_bytes = 0
            for sentence in sentences:
                # Create audio stream with adjustable speed
                stream = self.kokoro.create_stream(
                    sentence,
                    voice=voice_name,
                    speed=speed,
                    lang=lang
                )

                if i == 0:
                    # Send audio start
                    await self.write_event(
                        AudioStart(
                            rate=kokoro_onnx.config.SAMPLE_RATE,
                            width=2,
                            channels=1,
                        ).event()
                    )
                    i += 1

                # Process each chunk from the stream
                async for audio, sample_rate in stream:
                    # Convert float32 to int16
                    audio_int16 = (audio * 32767).astype(np.int16)
                    audio_bytes = audio_int16.tobytes()

                    t_bytes += len(audio_bytes)

                    # Send audio chunk
                    await self.write_event(
                        AudioChunk(
                            audio=audio_bytes,
                            rate=kokoro_onnx.config.SAMPLE_RATE,
                            width=2,
                            channels=1,
                        ).event()
                    )

            # Send audio stop
            await self.write_event(
                AudioStop().event())

            _LOGGER.debug('Synthesized %d bytes from %s', t_bytes, repr(synthesize))

            return True

        except Exception as e:
            _LOGGER.exception("Error synthesizing: %s", e)

    async def _handle_synthesize_start(self, event: Event) -> bool:
        """Handle start of streaming synthesis."""
        synthesize_start = SynthesizeStart.from_event(event)

        # Reset streaming state
        self.streaming_text_chunks = []
        self.streaming_audio_started = False

        # Parse and store voice settings with speed
        voice_name, speed, lang = self._parse_voice_settings(synthesize_start.voice)
        self.streaming_voice = voice_name
        self.streaming_speed = speed
        self.streaming_lang = lang

        _LOGGER.debug("Started streaming synthesis with voice: %s, speed: %.2f",
                     self.streaming_voice, self.streaming_speed)
        return True

    async def _handle_synthesize_chunk(self, event: Event) -> bool:
        """Handle streaming text chunk."""
        synthesize_chunk = SynthesizeChunk.from_event(event)

        # Accumulate text chunks
        self.streaming_text_chunks.append(synthesize_chunk.text)

        _LOGGER.debug("Received text chunk: %s", repr(synthesize_chunk.text))
        return True

    async def _handle_synthesize_stop(self, event: Event) -> bool:
        """Handle end of streaming synthesis and process accumulated text."""
        try:
            # Combine all text chunks
            full_text = "".join(self.streaming_text_chunks)

            if not full_text.strip():
                # No text to synthesize
                await self.write_event(SynthesizeStopped().event())
                return True

            _LOGGER.debug("Processing streaming synthesis with full text: %s", repr(full_text))

            # Split into sentences for streaming
            sentences = split_into_sentences(full_text)

            total_bytes = 0
            for i, sentence in enumerate(sentences):
                # Create audio stream with stored speed settings
                stream = self.kokoro.create_stream(
                    sentence,
                    voice=self.streaming_voice,
                    speed=self.streaming_speed,
                    lang=self.streaming_lang
                )

                if i == 0 and not self.streaming_audio_started:
                    # Send audio start on first sentence
                    await self.write_event(
                        AudioStart(
                            rate=kokoro_onnx.config.SAMPLE_RATE,
                            width=2,
                            channels=1,
                        ).event()
                    )
                    self.streaming_audio_started = True

                # Process each chunk from the stream
                async for audio, sample_rate in stream:
                    # Convert float32 to int16
                    audio_int16 = (audio * 32767).astype(np.int16)
                    audio_bytes = audio_int16.tobytes()

                    total_bytes += len(audio_bytes)

                    # Send audio chunk
                    await self.write_event(
                        AudioChunk(
                            audio=audio_bytes,
                            rate=kokoro_onnx.config.SAMPLE_RATE,
                            width=2,
                            channels=1,
                        ).event()
                    )

            # Send audio stop
            if self.streaming_audio_started:
                await self.write_event(AudioStop().event())

            # Send synthesize stopped confirmation
            await self.write_event(SynthesizeStopped().event())

            _LOGGER.debug('Streaming synthesis completed: %d bytes from %d chunks',
                          total_bytes, len(self.streaming_text_chunks))

            # Reset streaming state
            self.streaming_text_chunks = []
            self.streaming_voice = None
            self.streaming_speed = None
            self.streaming_lang = None
            self.streaming_audio_started = False

            return True

        except Exception as e:
            _LOGGER.exception("Error in streaming synthesis: %s", e)
            # Reset state on error
            self.streaming_text_chunks = []
            self.streaming_voice = None
            self.streaming_speed = None
            self.streaming_lang = None
            self.streaming_audio_started = False
            raise


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to listen on"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=10200,
        help="Port to listen on"
    )
    parser.add_argument(
        "--uri",
        default="tcp://0.0.0.0:10210",
        help="unix:// or tcp://"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Default speech speed (0.5-2.0, default: 1.0). Can be overridden per-request via voice.speaker parameter (e.g., 'speed_1.5')",
    )
    args = parser.parse_args()

    if args.debug:
        log.setLevel(level=logging.DEBUG)

    kokoro_instance = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    wyoming_voices = get_model_voices(kokoro_instance)

    wyoming_info = Info(
        tts=[TtsProgram(
            name="Kokoro",
            description="A fast, local, kokoro-based tts engine",
            attribution=Attribution(
                name="Kokoro TTS",
                url="https://huggingface.co/hexgrad/Kokoro-82M",
            ),
            installed=True,
            voices=sorted(wyoming_voices, key=lambda v: v.name),
            version=VERSION,
        )]
    )

    _LOGGER.info('Kokoro ONNX server starting on %s', args.uri)
    server = AsyncServer.from_uri(args.uri)

    # Handle OS signals
    loop = asyncio.get_event_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, lambda: asyncio.create_task(server.stop()))

    # Start server with kokoro instance and CLI args
    await server.run(partial(KokoroEventHandler, wyoming_info, kokoro_instance, args))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
