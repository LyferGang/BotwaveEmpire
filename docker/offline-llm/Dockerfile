# Botwave Offline LLM Server
# Runs local AI model - no API costs
# Based on Ollama for easy model management

FROM ollama/ollama:latest

LABEL description="Botwave Offline LLM Server"
LABEL maintainer="Al Gringo <botwave@empire.local>"

# Pre-download models
COPY <<EOF /tmp/pull_models.sh
#!/bin/bash
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
EOF

RUN chmod +x /tmp/pull_models.sh && /tmp/pull_models.sh

# Expose Ollama API
EXPOSE 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

CMD ["ollama", "serve"]
