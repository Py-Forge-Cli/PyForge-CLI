# REST API Wrapper Design for CortexPy CLI

## Overview
This document outlines options for wrapping the CortexPy CLI as a REST API to enable usage in notebook environments.

## Option 1: FastAPI Wrapper (Recommended)

### Implementation
```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
from cortexpy_cli.converters.converter_factory import ConverterFactory
from cortexpy_cli.utils.file_utils import detect_file_type

app = FastAPI(title="CortexPy API", version="0.1.0")

@app.post("/convert/")
async def convert_file(
    file: UploadFile = File(...),
    output_format: str = "parquet",
    options: dict = None
):
    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Detect file type and get converter
        file_type = detect_file_type(tmp_path)
        converter = ConverterFactory.get_converter(file_type, output_format)
        
        # Convert file
        output_path = converter.convert(tmp_path, options=options)
        
        # Return converted file
        return FileResponse(
            output_path,
            media_type='application/octet-stream',
            filename=os.path.basename(output_path)
        )
    finally:
        # Cleanup
        os.unlink(tmp_path)
```

### Advantages
- Lightweight and fast
- Easy async support
- Built-in documentation (Swagger UI)
- Minimal dependencies

### Deployment
```bash
# Local development
uvicorn api:app --reload

# Production with Gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker

# Docker deployment
FROM python:3.8-slim
RUN apt-get update && apt-get install -y mdbtools
COPY . /app
WORKDIR /app
RUN pip install -e . fastapi uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Option 2: Flask + Celery for Async Processing

### Implementation
```python
from flask import Flask, request, jsonify
from celery import Celery
import tempfile

app = Flask(__name__)
celery = Celery('cortexpy', broker='redis://localhost:6379')

@celery.task
def convert_file_task(file_path, output_format, options):
    converter = ConverterFactory.get_converter(
        detect_file_type(file_path), 
        output_format
    )
    return converter.convert(file_path, options=options)

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    
    # Save file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        
    # Queue conversion
    task = convert_file_task.delay(
        tmp.name,
        request.form.get('format', 'parquet'),
        request.form.get('options', {})
    )
    
    return jsonify({'task_id': task.id})

@app.route('/status/<task_id>')
def status(task_id):
    task = convert_file_task.AsyncResult(task_id)
    return jsonify({
        'status': task.status,
        'result': task.result if task.ready() else None
    })
```

### Advantages
- Handles long-running conversions
- Scalable with worker processes
- Progress tracking capability

### Deployment
```bash
# Redis required
docker run -d -p 6379:6379 redis

# Start Celery worker
celery -A api worker --loglevel=info

# Start Flask app
flask run
```

## Option 3: Serverless Functions (AWS Lambda/Azure Functions)

### Implementation
```python
import json
import base64
from cortexpy_cli.converters.converter_factory import ConverterFactory

def lambda_handler(event, context):
    # Get file from event
    file_content = base64.b64decode(event['body'])
    file_name = event['headers'].get('filename', 'file')
    
    # Save to /tmp (Lambda writable)
    input_path = f'/tmp/{file_name}'
    with open(input_path, 'wb') as f:
        f.write(file_content)
    
    # Convert
    converter = ConverterFactory.get_converter(
        detect_file_type(input_path),
        event['queryStringParameters'].get('format', 'parquet')
    )
    output_path = converter.convert(input_path)
    
    # Return result
    with open(output_path, 'rb') as f:
        return {
            'statusCode': 200,
            'body': base64.b64encode(f.read()).decode(),
            'headers': {
                'Content-Type': 'application/octet-stream'
            }
        }
```

### Advantages
- No server management
- Auto-scaling
- Pay per use

### Limitations
- File size limits (AWS: 6MB sync, 256MB async)
- Execution time limits (15 minutes)
- System dependencies need Lambda Layer

## Option 4: Notebook-Native Integration

### Direct Python API
```python
# In notebook
from cortexpy_cli.api import CortexPyAPI

api = CortexPyAPI()

# Convert file
result = api.convert(
    input_file="data.xlsx",
    output_format="parquet",
    options={'compression': 'snappy'}
)

# Get metadata
info = api.get_info("data.xlsx")
```

### Implementation
```python
# cortexpy_cli/api.py
class CortexPyAPI:
    def __init__(self):
        self.factory = ConverterFactory()
    
    def convert(self, input_file, output_format='parquet', options=None):
        file_type = detect_file_type(input_file)
        converter = self.factory.get_converter(file_type, output_format)
        return converter.convert(input_file, options)
    
    def get_info(self, input_file):
        file_type = detect_file_type(input_file)
        converter = self.factory.get_converter(file_type, 'parquet')
        return converter.get_metadata(input_file)
```

### Advantages
- No network overhead
- Direct integration
- Full feature access

## Recommended Architecture for Notebooks

### 1. **Development Environment**
- Use Option 4 (Direct API) for local notebooks
- Simple pip install and import

### 2. **Shared Environment (Databricks/JupyterHub)**
- Deploy Option 1 (FastAPI) as a service
- Mount as a notebook-accessible endpoint

### 3. **Production Pipelines**
- Option 2 (Flask+Celery) for large files
- Option 3 (Serverless) for sporadic usage

## System Dependencies in Container

```dockerfile
# Dockerfile with all dependencies
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    mdbtools \
    && rm -rf /var/lib/apt/lists/*

# Install Python package
COPY . /app
WORKDIR /app
RUN pip install -e ".[api]"

# For FastAPI
RUN pip install fastapi uvicorn

EXPOSE 8000
CMD ["uvicorn", "cortexpy_cli.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Example Notebook Usage

```python
# Using REST API
import requests

# Upload and convert
with open('data.xlsx', 'rb') as f:
    response = requests.post(
        'http://cortexpy-api:8000/convert/',
        files={'file': f},
        data={'output_format': 'parquet'}
    )

# Save result
with open('output.parquet', 'wb') as f:
    f.write(response.content)

# Using direct API
from cortexpy_cli.api import CortexPyAPI

api = CortexPyAPI()
result = api.convert('data.xlsx', 'parquet')
print(f"Converted to: {result}")
```

## Security Considerations

1. **File Size Limits**: Implement max upload size
2. **Authentication**: Add API keys or OAuth
3. **Rate Limiting**: Prevent abuse
4. **Input Validation**: Sanitize file names and types
5. **Temporary File Cleanup**: Ensure proper cleanup
6. **Resource Limits**: Memory and CPU constraints

## Next Steps

1. Choose deployment strategy based on use case
2. Implement selected option
3. Add authentication if needed
4. Create Docker image with system dependencies
5. Deploy to target environment
6. Create notebook examples and documentation