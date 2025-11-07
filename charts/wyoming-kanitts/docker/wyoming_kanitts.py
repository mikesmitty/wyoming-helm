#!/usr/bin/env python3
"""Wyoming protocol server for KaniTTS text-to-speech."""

import argparse
import asyncio
import logging
import os
import sys
import wave
from functools import partial
from pathlib import Path
from typing import Optional

import torch
import numpy as np

from wyoming.info import Attribution, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncServer
from wyoming.tts import Synthesize, SynthesizeResponse

_LOGGER = logging.getLogger(__name__)

# Will be imported after torch device is configured
KaniTTS = None


class KaniTTSEventHandler:
    """Event handler for Wyoming protocol TTS requests."""

    def __init__(
        self,
        model_name: str,
        device: str = "cpu",
        sample_rate: int = 24000,
    ):
        """Initialize the event handler.

        Args:
            model_name: Hugging Face model name (e.g., "nineninesix/kani-tts-370m")
            device: PyTorch device ("cpu", "cuda", "xpu")
            sample_rate: Audio sample rate in Hz
        """
        self.model_name = model_name
        self.device = device
        self.sample_rate = sample_rate
        self.model: Optional[object] = None

        _LOGGER.info("Initializing KaniTTS with model: %s on device: %s", model_name, device)

    async def load_model(self):
        """Load the KaniTTS model asynchronously."""
        if self.model is not None:
            return

        _LOGGER.info("Loading KaniTTS model...")

        # Import KaniTTS after device configuration
        global KaniTTS
        if KaniTTS is None:
            try:
                from kani_tts import KaniTTS as KaniTTSModel
                KaniTTS = KaniTTSModel
            except ImportError as err:
                _LOGGER.error("Failed to import KaniTTS: %s", err)
                _LOGGER.error("Make sure kani-tts is installed: pip install kani-tts")
                raise

        # Load model on the specified device
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(
            None,
            lambda: KaniTTS(self.model_name).to(self.device)
        )

        _LOGGER.info("KaniTTS model loaded successfully")

    async def handle_event(self, event) -> bool:
        """Handle a Wyoming protocol event.

        Args:
            event: Wyoming protocol event

        Returns:
            True if event was handled, False otherwise
        """
        if Synthesize.is_type(event.type):
            return await self.handle_synthesize(event)

        return True

    async def handle_synthesize(self, synthesize: Synthesize) -> bool:
        """Handle TTS synthesis request.

        Args:
            synthesize: Synthesize event containing text to speak

        Returns:
            True if synthesis succeeded
        """
        _LOGGER.debug("Synthesizing: %s", synthesize.text)

        # Ensure model is loaded
        await self.load_model()

        try:
            # Generate audio
            loop = asyncio.get_event_loop()
            audio_array = await loop.run_in_executor(
                None,
                lambda: self._generate_audio(synthesize.text)
            )

            # Convert to 16-bit PCM WAV format
            wav_data = self._create_wav(audio_array)

            # Send response
            await self.write_event(
                SynthesizeResponse(
                    rate=self.sample_rate,
                    width=2,  # 16-bit
                    channels=1,  # mono
                    audio=wav_data,
                ).event()
            )

            _LOGGER.debug("Synthesis complete")

        except Exception as err:
            _LOGGER.exception("Error during synthesis: %s", err)
            return False

        return True

    def _generate_audio(self, text: str) -> np.ndarray:
        """Generate audio from text using KaniTTS.

        Args:
            text: Text to synthesize

        Returns:
            Audio array as numpy array
        """
        with torch.no_grad():
            # KaniTTS generates audio - adjust based on actual API
            # This is a placeholder that needs to match the real KaniTTS API
            audio = self.model.generate(text, sample_rate=self.sample_rate)

            # Convert to numpy array if needed
            if isinstance(audio, torch.Tensor):
                audio = audio.cpu().numpy()

            # Ensure float32 range [-1, 1]
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # Normalize if needed
            max_val = np.abs(audio).max()
            if max_val > 1.0:
                audio = audio / max_val

        return audio

    def _create_wav(self, audio_array: np.ndarray) -> bytes:
        """Convert audio array to WAV bytes.

        Args:
            audio_array: Audio data as float32 numpy array

        Returns:
            WAV file as bytes
        """
        # Convert float32 [-1, 1] to int16
        audio_int16 = (audio_array * 32767).astype(np.int16)

        # Create WAV file in memory
        import io
        wav_io = io.BytesIO()

        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        return wav_io.getvalue()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Wyoming KaniTTS TTS Server")
    parser.add_argument(
        "--uri",
        required=True,
        help="URI to bind the server (e.g., tcp://0.0.0.0:10220)",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("KANITTS_MODEL", "nineninesix/kani-tts-370m"),
        help="KaniTTS model name from Hugging Face",
    )
    parser.add_argument(
        "--device",
        default=os.environ.get("PYTORCH_DEVICE", "cpu"),
        choices=["cpu", "cuda", "xpu"],
        help="PyTorch device to use",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=24000,
        help="Audio sample rate in Hz",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    _LOGGER.info("Starting Wyoming KaniTTS server")
    _LOGGER.info("Model: %s", args.model)
    _LOGGER.info("Device: %s", args.device)
    _LOGGER.info("URI: %s", args.uri)

    # Configure PyTorch device
    if args.device == "xpu":
        # Enable Intel XPU
        try:
            import intel_extension_for_pytorch as ipex
            _LOGGER.info("Intel Extension for PyTorch loaded")
        except ImportError:
            _LOGGER.warning("intel_extension_for_pytorch not found, XPU may not work")

        if not torch.xpu.is_available():
            _LOGGER.error("XPU device not available")
            sys.exit(1)

        _LOGGER.info("XPU devices: %d", torch.xpu.device_count())

    elif args.device == "cuda":
        if not torch.cuda.is_available():
            _LOGGER.error("CUDA device not available")
            sys.exit(1)

        _LOGGER.info("CUDA devices: %d", torch.cuda.device_count())

    # Create server info
    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="kanitts",
                description="High-quality neural TTS with KaniTTS",
                attribution=Attribution(
                    name="NineNineSix",
                    url="https://github.com/nineninesix-ai/kani-tts",
                ),
                installed=True,
                voices=[
                    TtsVoice(
                        name="default",
                        description="KaniTTS default voice",
                        attribution=Attribution(
                            name="NineNineSix",
                            url="https://github.com/nineninesix-ai/kani-tts",
                        ),
                        installed=True,
                        languages=["en"],  # Adjust based on model capabilities
                    )
                ],
            )
        ],
    )

    # Create event handler
    event_handler = KaniTTSEventHandler(
        model_name=args.model,
        device=args.device,
        sample_rate=args.sample_rate,
    )

    # Pre-load model
    await event_handler.load_model()

    # Start server
    server = AsyncServer.from_uri(args.uri)

    _LOGGER.info("Server ready")

    await server.run(partial(event_handler.handle_event))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Server stopped")
