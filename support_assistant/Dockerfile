FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the embedding model into the image at build time so docker run needs
# no network access.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer(\"all-MiniLM-L6-v2\")"

COPY . ./support_assistant/

EXPOSE 7860

CMD ["sh", "-c", "python -m support_assistant.ingest && uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860"]
