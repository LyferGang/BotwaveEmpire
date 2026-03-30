# Botwave Media MCP Integration

This integration adds AI-powered media generation and processing capabilities to Botwave Empire by wrapping:

1. **remotion-media-mcp** - AI media generation (images, video, music, speech)
2. **no-code-architects-toolkit** - Media processing (transcription, captions, conversion)

## Setup

### 1. Configure Environment Variables

Add to your `.env` file:

```bash
# For remotion-media-mcp (kie.ai)
KIE_API_KEY=your-kie-api-key

# For no-code-architects-toolkit
NCA_API_URL=http://localhost:8080  # Or your deployed URL
NCA_API_KEY=your-nca-api-key       # If authentication is enabled
```

### 2. Get API Keys

**KIE_API_KEY**: Sign up at [kie.ai](https://kie.ai) and get your API key from the dashboard.

**NCA_API**: Deploy your own instance or use a hosted one.

## Available Tools

### Image Generation
```json
{
  "tool": "media_generate_image",
  "prompt": "A futuristic cityscape with neon lights",
  "output_name": "cityscape",
  "aspect_ratio": "16:9",
  "resolution": "2K"
}
```

### Video Generation
```json
{
  "tool": "media_generate_video",
  "prompt": "Drone shot flying over mountains at sunset",
  "output_name": "mountain_drone",
  "model": "veo3"
}
```

### Speech Generation (TTS)
```json
{
  "tool": "media_generate_speech",
  "text": "Welcome to Botwave Empire, your AI automation platform.",
  "output_name": "welcome",
  "voice": "Eric"
}
```

### Transcription
```json
{
  "tool": "media_transcribe",
  "media_url": "https://example.com/video.mp4",
  "language": "en"
}
```

### Video Captioning
```json
{
  "tool": "media_caption_video",
  "video_url": "https://example.com/video.mp4",
  "font_size": 24,
  "font_color": "white"
}
```

### Webpage Screenshots
```json
{
  "tool": "media_screenshot_webpage",
  "url": "https://example.com",
  "viewport_width": 1920,
  "viewport_height": 1080,
  "full_page": true
}
```

## Usage in Claude Code

Once the MCP server is running, you can use these tools:

```
Use media_generate_image to create an image of a modern dashboard interface
```

```
Use media_generate_speech to convert "Hello world" to speech with voice Eric
```

```
Use media_screenshot_webpage to capture https://botwave.local
```

## Standalone Usage

You can also use the Media MCP client directly:

```bash
python3 mcp/integrations/media_mcp.py status

python3 mcp/integrations/media_mcp.py generate-image \
  --prompt "A robot working on code" \
  --output robot_coding

python3 mcp/integrations/media_mcp.py generate-speech \
  --text "Hello from Botwave" \
  --output greeting \
  --voice Rachel
```

## Integration with Agent Jobs

Agents can use these tools as part of their workflow:

1. **Content Creation Agent**: Generate images, videos, and audio for marketing
2. **Documentation Agent**: Screenshot web pages, transcribe videos
3. **Media Processing Agent**: Convert formats, add captions, concatenate audio

## Architecture

```
Claude Code → Botwave MCP Server → Media MCP Client → External APIs
                                           ↓
                                    remotion-media-mcp (kie.ai)
                                    no-code-architects-toolkit
```

## Cost Considerations

**remotion-media-mcp**: Requires KIE_API_KEY (paid API based on usage)
**no-code-architects-toolkit**: Self-hosted, free to use (compute costs only)

## Troubleshooting

### "KIE_API_KEY not configured"
Add your API key to the `.env` file and restart the MCP server.

### "Connection refused" for NCA toolkit
Ensure your NCA API is running and accessible at the configured URL.

### Timeouts
Media generation can take time. Default timeouts:
- Images: 300s
- Video: 600s
- Speech: 60s
- Transcription: 300s

## References

- [remotion-media-mcp](https://github.com/stephengpope/remotion-media-mcp)
- [no-code-architects-toolkit](https://github.com/stephengpope/no-code-architects-toolkit)
