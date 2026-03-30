#!/usr/bin/env python3
"""
BOTWAVE MEDIA MCP INTEGRATION
Wrapper for remotion-media-mcp and no-code-architects-toolkit

Provides media generation and processing capabilities to Botwave agents.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Optional, Dict, List

BASE_DIR = Path(__file__).parent.parent


class MediaMCPClient:
    """Client for media generation and processing MCP servers."""

    def __init__(self):
        self.kie_api_key = os.getenv("KIE_API_KEY")
        self.nca_api_url = os.getenv("NCA_API_URL", "http://localhost:8080")
        self.nca_api_key = os.getenv("NCA_API_KEY")

    # ===== REMOTION MEDIA MCP (kie.ai) =====

    def generate_image(self, prompt: str, output_name: str, aspect_ratio: str = "1:1",
                       resolution: str = "1K", image_urls: List[str] = None) -> Dict:
        """Generate AI image via Nano Banana Pro."""
        return self._call_remotion_mcp("generate_image", {
            "prompt": prompt,
            "output_name": output_name,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "image_urls": image_urls or []
        })

    def generate_video_from_text(self, prompt: str, output_name: str,
                                 model: str = "veo3_fast", aspect_ratio: str = "16:9") -> Dict:
        """Generate video from text via Veo 3.1."""
        return self._call_remotion_mcp("generate_video_from_text", {
            "prompt": prompt,
            "output_name": output_name,
            "model": model,
            "aspect_ratio": aspect_ratio
        })

    def generate_video_from_image(self, prompt: str, image_urls: List[str],
                                  output_name: str, model: str = "veo3_fast",
                                  aspect_ratio: str = "16:9") -> Dict:
        """Animate image(s) via Veo 3.1."""
        return self._call_remotion_mcp("generate_video_from_image", {
            "prompt": prompt,
            "image_urls": image_urls,
            "output_name": output_name,
            "model": model,
            "aspect_ratio": aspect_ratio
        })

    def generate_music(self, prompt: str, output_name: str,
                       instrumental: bool = False, model: str = "V5") -> Dict:
        """Generate AI music via Suno."""
        return self._call_remotion_mcp("generate_music", {
            "prompt": prompt,
            "output_name": output_name,
            "instrumental": instrumental,
            "model": model
        })

    def generate_sound_effect(self, prompt: str, output_name: str,
                              duration_seconds: float = 3.0, loop: bool = False) -> Dict:
        """Generate sound effect via ElevenLabs SFX V2."""
        return self._call_remotion_mcp("generate_sound_effect", {
            "prompt": prompt,
            "output_name": output_name,
            "duration_seconds": duration_seconds,
            "loop": loop
        })

    def generate_speech(self, text: str, output_name: str, voice: str = "Eric",
                        model: str = "turbo_v2_5", speed: float = 1.0) -> Dict:
        """Text-to-speech via ElevenLabs."""
        return self._call_remotion_mcp("generate_speech", {
            "text": text,
            "output_name": output_name,
            "voice": voice,
            "model": model,
            "speed": speed
        })

    def generate_subtitles(self, input_file: str, output_name: str = None,
                           language: str = None, model: str = "base") -> Dict:
        """Transcribe to SRT subtitles using Whisper."""
        return self._call_remotion_mcp("generate_subtitles", {
            "input_file": input_file,
            "output_name": output_name or input_file.rsplit('.', 1)[0],
            "language": language,
            "model": model
        })

    # ===== NO-CODE ARCHITECTS TOOLKIT =====

    def transcribe_media(self, media_url: str, language: str = "en",
                         webhook_url: str = None) -> Dict:
        """Transcribe media to text."""
        return self._call_nca_api("/v1/media/transcribe", {
            "media_url": media_url,
            "language": language,
            "webhook_url": webhook_url
        })

    def caption_video(self, video_url: str, srt_url: str = None,
                      font_size: int = 24, font_color: str = "white") -> Dict:
        """Add captions to video."""
        return self._call_nca_api("/v1/video/caption", {
            "video_url": video_url,
            "srt_url": srt_url,
            "font_size": font_size,
            "font_color": font_color
        })

    def convert_media(self, media_url: str, output_format: str,
                      webhook_url: str = None) -> Dict:
        """Convert media format."""
        return self._call_nca_api("/v1/media/convert", {
            "media_url": media_url,
            "output_format": output_format,
            "webhook_url": webhook_url
        })

    def screenshot_webpage(self, url: str, viewport_width: int = 1920,
                           viewport_height: int = 1080, full_page: bool = False) -> Dict:
        """Capture webpage screenshot."""
        return self._call_nca_api("/v1/image/screenshot/webpage", {
            "url": url,
            "viewport": {"width": viewport_width, "height": viewport_height},
            "full_page": full_page
        })

    def concatenate_audio(self, audio_urls: List[str], webhook_url: str = None) -> Dict:
        """Concatenate multiple audio files."""
        return self._call_nca_api("/v1/audio/concatenate", {
            "audio_urls": audio_urls,
            "webhook_url": webhook_url
        })

    def execute_python(self, code: str, timeout: int = 30) -> Dict:
        """Execute Python code remotely."""
        return self._call_nca_api("/v1/code/execute/python", {
            "code": code,
            "timeout": timeout
        })

    def upload_to_s3(self, file_url: str, bucket: str, key: str,
                     webhook_url: str = None) -> Dict:
        """Upload file to S3."""
        return self._call_nca_api("/v1/s3/upload", {
            "file_url": file_url,
            "bucket": bucket,
            "key": key,
            "webhook_url": webhook_url
        })

    # ===== INTERNAL HELPERS =====

    def _call_remotion_mcp(self, tool: str, params: Dict) -> Dict:
        """Call remotion-media-mcp tool."""
        if not self.kie_api_key:
            return {"error": "KIE_API_KEY not configured"}

        # Try to use the MCP server if available
        # Otherwise, call the API directly
        try:
            import urllib.request
            import urllib.parse

            url = "https://api.kie.ai/v1/generate"
            headers = {
                "Authorization": f"Bearer {self.kie_api_key}",
                "Content-Type": "application/json"
            }

            data = json.dumps({"tool": tool, **params}).encode()
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")

            with urllib.request.urlopen(req, timeout=300) as response:
                return json.loads(response.read().decode())

        except Exception as e:
            return {"error": str(e), "tool": tool}

    def _call_nca_api(self, endpoint: str, params: Dict) -> Dict:
        """Call No-Code Architects Toolkit API."""
        try:
            import urllib.request
            import urllib.parse

            url = f"{self.nca_api_url}{endpoint}"
            headers = {"Content-Type": "application/json"}

            if self.nca_api_key:
                headers["Authorization"] = f"Bearer {self.nca_api_key}"

            data = json.dumps(params).encode()
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")

            with urllib.request.urlopen(req, timeout=300) as response:
                return json.loads(response.read().decode())

        except Exception as e:
            return {"error": str(e), "endpoint": endpoint}

    def get_status(self) -> Dict:
        """Get integration status."""
        return {
            "remotion_mcp": {
                "configured": bool(self.kie_api_key),
                "api_key": "***" if self.kie_api_key else None
            },
            "nca_toolkit": {
                "configured": bool(self.nca_api_url),
                "url": self.nca_api_url,
                "api_key": "***" if self.nca_api_key else None
            }
        }


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Botwave Media MCP Client")
    parser.add_argument("command", choices=[
        "generate-image", "generate-video", "generate-music",
        "generate-speech", "transcribe", "caption", "status"
    ])
    parser.add_argument("--prompt", help="Generation prompt")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--url", help="Media URL")
    parser.add_argument("--text", help="Text content")
    parser.add_argument("--voice", default="Eric", help="Voice for TTS")

    args = parser.parse_args()

    client = MediaMCPClient()

    if args.command == "status":
        print(json.dumps(client.get_status(), indent=2))

    elif args.command == "generate-image":
        if args.prompt and args.output:
            result = client.generate_image(args.prompt, args.output)
            print(json.dumps(result, indent=2))
        else:
            print("Error: --prompt and --output required")

    elif args.command == "generate-video":
        if args.prompt and args.output:
            result = client.generate_video_from_text(args.prompt, args.output)
            print(json.dumps(result, indent=2))
        else:
            print("Error: --prompt and --output required")

    elif args.command == "generate-speech":
        if args.text and args.output:
            result = client.generate_speech(args.text, args.output, args.voice)
            print(json.dumps(result, indent=2))
        else:
            print("Error: --text and --output required")

    elif args.command == "transcribe":
        if args.url:
            result = client.transcribe_media(args.url)
            print(json.dumps(result, indent=2))
        else:
            print("Error: --url required")

    elif args.command == "caption":
        if args.url:
            result = client.caption_video(args.url)
            print(json.dumps(result, indent=2))
        else:
            print("Error: --url required")
