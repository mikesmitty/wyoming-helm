#!/usr/bin/env python3
"""Wyoming protocol server for KaniTTS text-to-speech."""

import argparse
import asyncio
import logging
import os
import sys
from functools import partial
from pathlib import Path
from typing import Optional

import torch
import numpy as np

from wyoming.info import Attribution, Describe, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncServer, AsyncEventHandler
from wyoming.tts import Synthesize
from wyoming.audio import AudioChunk, AudioStop

_LOGGER = logging.getLogger(__name__)

VERSION = "0.2.0"  # x-release-please-version

# Will be imported after torch device is configured
KaniTTS = None

# Shared model instance across all handlers
_shared_model = None
_model_lock = asyncio.Lock()


class KaniTTSEventHandler(AsyncEventHandler):
    """Event handler for Wyoming protocol TTS requests."""

    def __init__(
        self,
        wyoming_info: Info,
        model_name: str,
        device: str = "cpu",
        sample_rate: int = 22050,
        *args,
        **kwargs
    ):
        """Initialize the event handler.

        Args:
            wyoming_info: Wyoming server info
            model_name: Hugging Face model name (e.g., "nineninesix/kani-tts-370m")
            device: PyTorch device ("cpu", "cuda", "xpu")
            sample_rate: Audio sample rate in Hz
        """
        super().__init__(*args, **kwargs)

        self.wyoming_info_event = wyoming_info.event()
        self.model_name = model_name
        self.device = device
        self.sample_rate = sample_rate
        self.model: Optional[object] = None

        _LOGGER.info("Initializing KaniTTS with model: %s on device: %s", model_name, device)

    async def load_model(self):
        """Load the KaniTTS model asynchronously (shared across all handlers)."""
        global _shared_model, KaniTTS

        async with _model_lock:
            if _shared_model is not None:
                self.model = _shared_model
                return

            _LOGGER.info("Loading KaniTTS model...")

            # Import KaniTTS after device configuration
            if KaniTTS is None:
                try:
                    from kani_tts import KaniTTS as KaniTTSModel
                    KaniTTS = KaniTTSModel
                except ImportError as err:
                    _LOGGER.error("Failed to import KaniTTS: %s", err)
                    _LOGGER.error("Make sure kani-tts is installed: pip install kani-tts")
                    raise

            # Load model - KaniTTS handles device internally
            loop = asyncio.get_event_loop()
            _shared_model = await loop.run_in_executor(
                None,
                lambda: KaniTTS(self.model_name)
            )
            self.model = _shared_model

            _LOGGER.info("KaniTTS model loaded successfully")

    async def handle_event(self, event) -> bool:
        """Handle a Wyoming protocol event.

        Args:
            event: Wyoming protocol event

        Returns:
            True if event was handled, False otherwise
        """
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        if Synthesize.is_type(event.type):
            synthesize = Synthesize.from_event(event)
            return await self.handle_synthesize(synthesize)

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
            # Use voice name as speaker (e.g., "david", "jenny")
            speaker = None
            if hasattr(synthesize, 'voice') and synthesize.voice:
                speaker = synthesize.voice.name if hasattr(synthesize.voice, 'name') else str(synthesize.voice)
            audio_array = await loop.run_in_executor(
                None,
                lambda: self._generate_audio(synthesize.text, speaker)
            )

            # Convert to 16-bit PCM
            audio_int16 = (audio_array * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()

            # Send audio chunk
            await self.write_event(
                AudioChunk(
                    rate=self.sample_rate,
                    width=2,  # 16-bit
                    channels=1,  # mono
                    audio=audio_bytes,
                ).event()
            )

            # Send stop event
            await self.write_event(AudioStop().event())

            _LOGGER.debug("Synthesis complete")

        except Exception as err:
            _LOGGER.exception("Error during synthesis: %s", err)
            return False

        return True

    def _generate_audio(self, text: str, speaker: Optional[str] = None) -> np.ndarray:
        """Generate audio from text using KaniTTS.

        Args:
            text: Text to synthesize
            speaker: Optional speaker name (e.g., "david", "jenny")

        Returns:
            Audio array as numpy array
        """
        # KaniTTS API: audio, text = model(text, speaker_id=speaker_name)
        # Returns audio as numpy array at 22kHz
        if speaker:
            audio, _ = self.model(text, speaker_id=speaker)
            _LOGGER.debug("Generated audio with speaker: %s", speaker)
        else:
            audio, _ = self.model(text)
            _LOGGER.debug("Generated audio with default speaker")

        # Ensure float32 range [-1, 1]
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Normalize if needed
        max_val = np.abs(audio).max()
        if max_val > 1.0:
            audio = audio / max_val

        return audio


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
        default=22050,
        help="Audio sample rate in Hz (KaniTTS generates 22kHz audio)",
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
        # Check for Intel XPU (native PyTorch 2.7+ support)
        if not torch.xpu.is_available():
            _LOGGER.error("XPU device not available. Ensure Intel GPU drivers and compute runtime are installed.")
            _LOGGER.error("PyTorch version: %s", torch.__version__)
            sys.exit(1)

        _LOGGER.info("XPU devices available: %d", torch.xpu.device_count())

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
                version=VERSION,
                voices=[
                    TtsVoice(
                        name="david",
                        description="David (Male, English)",
                        attribution=Attribution(
                            name="NineNineSix",
                            url="https://github.com/nineninesix-ai/kani-tts",
                        ),
                        installed=True,
                        version=None,
                        languages=["en"],
                    ),
                    TtsVoice(
                        name="jenny",
                        description="Jenny (Female, English)",
                        attribution=Attribution(
                            name="NineNineSix",
                            url="https://github.com/nineninesix-ai/kani-tts",
                        ),
                        installed=True,
                        version=None,
                        languages=["en"],
                    ),
                    TtsVoice(
                        name="katie",
                        description="Katie (Female, English)",
                        attribution=Attribution(
                            name="NineNineSix",
                            url="https://github.com/nineninesix-ai/kani-tts",
                        ),
                        installed=True,
                        version=None,
                        languages=["en"],
                    ),
                    TtsVoice(
                        name="andrew",
                        description="Andrew (Male, English)",
                        attribution=Attribution(
                            name="NineNineSix",
                            url="https://github.com/nineninesix-ai/kani-tts",
                        ),
                        installed=True,
                        version=None,
                        languages=["en"],
                    ),
                    TtsVoice(
                        name="simon",
                        description="Simon (Male, English)",
                        attribution=Attribution(
                            name="NineNineSix",
                            url="https://github.com/nineninesix-ai/kani-tts",
                        ),
                        installed=True,
                        version=None,
                        languages=["en"],
                    ),
                    TtsVoice(
                        name="puck",
                        description="Puck (Male, English)",
                        attribution=Attribution(
                            name="NineNineSix",
                            url="https://github.com/nineninesix-ai/kani-tts",
                        ),
                        installed=True,
                        version=None,
                        languages=["en"],
                    ),
                ],
            )
        ],
    )

    # Preload the model before starting the server
    _LOGGER.info("Preloading KaniTTS model...")
    global _shared_model, KaniTTS

    if KaniTTS is None:
        try:
            from kani_tts import KaniTTS as KaniTTSModel
            KaniTTS = KaniTTSModel
        except ImportError as err:
            _LOGGER.error("Failed to import KaniTTS: %s", err)
            _LOGGER.error("Make sure kani-tts is installed: pip install kani-tts")
            sys.exit(1)

    # Set PyTorch default device to XPU if requested
    if args.device == "xpu":
        torch.set_default_device("xpu")
        _LOGGER.info("Set PyTorch default device to XPU")
    elif args.device == "cuda":
        torch.set_default_device("cuda")
        _LOGGER.info("Set PyTorch default device to CUDA")

    # Load model synchronously at startup
    loop = asyncio.get_event_loop()
    _shared_model = await loop.run_in_executor(
        None,
        lambda: KaniTTS(args.model)
    )

    # Check what device the model actually ended up on
    try:
        # Try to find model parameters and check their device
        if hasattr(_shared_model, 'model'):
            # Get first parameter to check device
            first_param = next(_shared_model.model.parameters(), None)
            if first_param is not None:
                _LOGGER.info("Model weights are on device: %s", first_param.device)
            else:
                _LOGGER.info("Model has no parameters to check")
        else:
            _LOGGER.info("Cannot access internal model to check device")
    except Exception as e:
        _LOGGER.warning("Could not determine model device: %s", e)

    _LOGGER.info("Model loaded and ready")

    # Start server
    server = AsyncServer.from_uri(args.uri)

    _LOGGER.info("Server ready")

    # Start server with handler factory
    await server.run(
        partial(
            KaniTTSEventHandler,
            wyoming_info,
            args.model,
            args.device,
            args.sample_rate,
        )
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOGGER.info("Server stopped")
