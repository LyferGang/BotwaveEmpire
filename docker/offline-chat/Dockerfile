# Botwave Offline Chat Web UI
# Claude Code-like interface running 100% local
# No external API calls - all inference via local Ollama

FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    flask \
    flask-socketio \
    requests \
    python-socketio \
    eventlet

# Copy application
COPY offline_chat_app.py /app/
COPY templates/ /app/templates/
COPY static/ /app/static/

# Environment
ENV OLLAMA_HOST=ollama:11434
ENV FLASK_ENV=production

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "offline_chat_app.py"]
