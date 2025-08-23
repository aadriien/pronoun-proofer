FROM python:3.11.5-slim

WORKDIR /app

# Install dependencies and clean up in one layer
RUN apt-get update && apt-get install -y gcc g++ && \
    rm -rf /var/lib/apt/lists/* && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge && \
    # Remove the largest space wasters
    rm -rf /usr/local/lib/python3.11/site-packages/torch/include && \
    rm -rf /usr/local/lib/python3.11/site-packages/torch/share && \
    rm -rf /usr/local/lib/python3.11/site-packages/torch/test && \
    rm -rf /usr/local/lib/python3.11/site-packages/torch/bin && \
    rm -rf /usr/local/lib/python3.11/site-packages/numpy/tests && \
    rm -rf /usr/local/lib/python3.11/site-packages/transformers/models && \
    find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete && \
    find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true

COPY bot.py .
COPY src/ ./src/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "bot.py"]
