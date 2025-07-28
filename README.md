# PDF to JSON Processor

## 🔍 Description
This solution extracts structured content from PDF files and converts them into JSON format based on a defined schema.

## 📦 Directory Structure
```
Challenge_1a/
├── sample_dataset/
│   ├── outputs/         # JSON files provided as outputs.
│   ├── pdfs/            # Input PDF files
│   └── schema/          # Output schema definition
│       └── output_schema.json
├── Dockerfile           # Docker container configuration
├── process_pdfs.py      # Sample processing script
└── README.md           # This file
```

## 🧪 How to Build & Run


### Build the Docker image:
```bash
docker build --platform=linux/amd64 -t pdf-processor .
```


### Run the container:

```bash

docker run --rm \
  -v $(pwd)/sample_dataset/pdfs:/app/input:ro \
  -v $(pwd)/sample_dataset/outputs:/app/output \
  --network none pdf-processor
```

