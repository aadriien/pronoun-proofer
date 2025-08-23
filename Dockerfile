FROM python:3.11.5-slim

WORKDIR /app

# Install and immediately clean up
RUN apt-get update && apt-get install -y gcc g++ && \
    rm -rf /var/lib/apt/lists/* && apt-get clean

# Install dependencies and compress models in one command
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge && \
    # Remove PyTorch development files (biggest space wasters)
    rm -rf /usr/local/lib/python3.11/site-packages/torch/include && \
    rm -rf /usr/local/lib/python3.11/site-packages/torch/share && \
    rm -rf /usr/local/lib/python3.11/site-packages/torch/test && \
    rm -rf /usr/local/lib/python3.11/site-packages/numpy/tests && \
    # CRITICAL: Quantize the coreference model to reduce size by 50-75%
    python3 -c "
 import torch, os, glob
 # Find model weight files
 model_files = glob.glob('/usr/local/lib/python3.11/site-packages/**/en_coreference_web_trf/**/pytorch_model.bin', recursive=True)
 model_files.extend(glob.glob('/usr/local/lib/python3.11/site-packages/**/en_coreference_web_trf/**/*.safetensors', recursive=True))
 
 for model_file in model_files:
     if os.path.exists(model_file) and os.path.getsize(model_file) > 50*1024*1024:  # Only process files > 50MB
         try:
             # Load, quantize to int8, and save back
             model_data = torch.load(model_file, map_location='cpu')
             if isinstance(model_data, dict):
                 for key, tensor in model_data.items():
                     if isinstance(tensor, torch.Tensor) and tensor.dtype == torch.float32:
                         model_data[key] = tensor.to(torch.int8)
                 torch.save(model_data, model_file)
                 print(f'Quantized: {model_file}')
         except Exception as e:
             print(f'Skip {model_file}: {e}')
             continue
 print('Model quantization complete')" && \
    # Remove transformers cache and unused models
    rm -rf /usr/local/lib/python3.11/site-packages/transformers/models/*/pytorch_model.bin 2>/dev/null || true && \
    # Clean up Python cache
    find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete && \
    find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Copy application
COPY bot.py .
COPY src/ ./src/

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "bot.py"]
