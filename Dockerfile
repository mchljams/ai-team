FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY personas/ personas/
COPY sessions/ sessions/
COPY TEAM.md .
COPY bin/github-mcp-server bin/github-mcp-server
COPY scripts/start.sh scripts/start.sh
COPY scripts/diarmuid-listener.py scripts/diarmuid-listener.py

# Make binaries executable
RUN chmod +x bin/github-mcp-server scripts/start.sh

# Pre-download the ChromaDB embedding model so it's baked into the image
# (avoids a 79MB download on first message after each container start)
RUN python3 -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction; DefaultEmbeddingFunction()([\"\"])"

# DATA_DIR is mounted from Azure Files at runtime (/data)
# Palace path is set via MEMPALACE_PALACE_PATH env var
ENV DATA_DIR=/data
ENV PYTHONUNBUFFERED=1

# Ensure /data mount point exists
RUN mkdir -p /data

CMD ["scripts/start.sh"]
