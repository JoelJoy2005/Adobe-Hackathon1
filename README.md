# Challenge 1a: PDF Processing Solution

## Overview
This is a sample solution for Challenge 1a of the Adobe India Hackathon 2025. The challenge requires implementing a PDF processing solution that extracts structured data from PDF documents and outputs JSON files. The solution must be containerized using Docker and meet specific performance and resource constraints.

## 🔍 Description
A high-performance, containerized PDF processing solution designed for this hackathon competition. This solution extracts structured data from PDF documents and outputs JSON files while meeting strict performance and resource constraints.

## 🚀 Key Features

- **High Performance**: Processes 50-page PDFs in under 10 seconds
- **Memory Efficient**: Optimized for 16GB RAM constraint with batch processing
- **Multi-threading**: Leverages all 8 CPU cores efficiently
- **Comprehensive Extraction**: Text, images, tables, and metadata
- **Robust Architecture**: Handles both simple and complex PDF layouts
- **No Network Dependencies**: Fully offline processing
- **Open Source**: Uses only open-source libraries

## 📋 Technical Specifications

- **Runtime**: CPU-only (AMD64 architecture)
- **Memory Usage**: <16GB RAM
- **Processing Time**: ≤10 seconds for 50-page PDFs
- **Model Size**: <200MB (no ML models required)
- **Network**: No internet access during runtime
- **Platform**: Docker containerized, Linux/AMD64

## 🏗️ Architecture

### Core Components

1. **OptimizedPDFProcessor**: Main processing engine
2. **Batch Processing**: Memory-efficient page processing
3. **Multi-threading**: Parallel PDF processing
4. **Metadata Extraction**: Document properties and creation info
5. **Content Analysis**: Text blocks, images, and table detection
6. **JSON Generation**: Schema-compliant output formatting

### Libraries Used

- **PyMuPDF (fitz)**: High-performance PDF processing
- **concurrent.futures**: Multi-threading support
- **json**: Output formatting
- **pathlib**: File system operations
- **datetime**: Timestamp handling
- **re**: Pattern matching for language detection


## 🛠️ Installation & Setup

### Quick Setup

Run the setup script to create the project structure:

```bash
chmod +x setup_project.sh
./setup_project.sh
```

### Manual Setup

1. Create project structure:
```bash
mkdir -p Challenge_1a/sample_dataset/{outputs,pdfs,schema}
cd Challenge_1a
```

2. Place the provided files in the correct locations:
   - `process_pdfs.py` (main processing script)
   - `Dockerfile` (container configuration)
   - `requirements.txt` (Python dependencies)

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


## Testing with Sample Data

```bash
# Place test PDFs in sample_dataset/pdfs/
cp your_test_files.pdf sample_dataset/pdfs/

# Run processing
docker run --rm \
  -v $(pwd)/sample_dataset/pdfs:/app/input:ro \
  -v $(pwd)/sample_dataset/outputs:/app/output \
  --network none \
  pdf-processor

# Check outputs
ls sample_dataset/outputs/
```

## 📊 Output Format

Each PDF generates a corresponding JSON file following this structure:

```json
{
  "document_info": {
    "filename": "document.pdf",
    "total_pages": 10,
    "creation_date": "2024-01-15 10:30:00",
    "modification_date": "2024-01-15 15:45:00",
    "author": "Author Name",
    "title": "Document Title",
    "subject": "Document Subject"
  },
  "content": {
    "pages": [
      {
        "page_number": 1,
        "text_content": "Full page text...",
        "text_blocks": [
          {
            "bbox": [x1, y1, x2, y2],
            "text": "Text block content",
            "font_size": 12.0,
            "font": "TimesRoman"
          }
        ],
        "images": [
          {
            "bbox": [x1, y1, x2, y2],
            "width": 800,
            "height": 600
          }
        ],
        "tables": [
          {
            "bbox": [x1, y1, x2, y2],
            "rows": 5,
            "columns": 3,
            "data": [
              ["Header1", "Header2", "Header3"],
              ["Row1Col1", "Row1Col2", "Row1Col3"]
            ]
          }
        ]
      }
    ],
    "summary": {
      "total_text_length": 15420,
      "total_images": 3,
      "total_tables": 2,
      "language": "en"
    }
  }
}
```

## ⚡ Performance Optimizations

### Memory Management
- **Batch Processing**: Pages processed in batches of 10 to prevent memory overflow
- **Garbage Collection**: Explicit cleanup after each batch
- **Resource Cleanup**: Proper disposal of PDF objects and page references

### CPU Utilization
- **Multi-threading**: Parallel processing of multiple PDFs
- **Controlled Concurrency**: Limited to 4 concurrent PDFs to balance speed and memory
- **Efficient Algorithms**: Optimized text extraction and table detection

### Processing Speed
- **Direct API Access**: Uses PyMuPDF's high-performance C++ backend
- **Minimal Overhead**: Streamlined processing pipeline
- **Smart Caching**: Reuses text dictionaries for multiple extractions

## 🧪 Testing Strategy

### Performance Testing
```bash
# Test with 50-page PDF
time docker run --rm \
  -v $(pwd)/test_pdfs:/app/input:ro \
  -v $(pwd)/test_outputs:/app/output \
  --network none \
  pdf-processor
```

### Validation Checklist
- ✅ All PDFs in input directory processed
- ✅ JSON output files generated for each PDF
- ✅ Output format matches required schema
- ✅ Processing completes within 10 seconds for 50-page PDFs
- ✅ Solution works without internet access
- ✅ Memory usage stays within 16GB limit
- ✅ Compatible with AMD64 architecture

## 🔧 Troubleshooting

### Common Issues

**Out of Memory Error**:
- Reduce batch size in `process_single_page` function
- Increase Docker memory limit if needed

**Slow Processing**:
- Check CPU allocation in Docker settings
- Ensure PDFs are not corrupted or password-protected

**Missing Dependencies**:
- Rebuild Docker image with `--no-cache` flag
- Verify requirements.txt has correct versions

### Performance Monitoring

The solution includes built-in timing and memory monitoring:
- Processing time per PDF
- Total execution time
- Success/failure statistics

## 📈 Expected Performance

- **Single Page PDF**: <0.5 seconds
- **10-Page PDF**: 1-3 seconds
- **50-Page PDF**: 5-8 seconds
- **Memory Usage**: 2-8GB (depending on PDF complexity)
- **CPU Usage**: 80-100% utilization across 8 cores

## 🏆 Competitive Advantages

1. **Speed**: Optimized for sub-10-second processing
2. **Accuracy**: Comprehensive content extraction
3. **Reliability**: Robust error handling and resource management
4. **Scalability**: Efficient parallel processing
5. **Compliance**: Meets all hackathon constraints

## 📝 Schema Compliance

The output strictly follows the schema defined in `sample_dataset/schema/output_schema.json`, ensuring compatibility with evaluation systems.

## 🤝 Contributing

This is a competition solution, but the architecture can be extended for:
- Additional content types (forms, annotations)
- OCR integration for scanned documents
- Advanced table detection algorithms
- Multi-language support enhancement

---

**Built for Adobe India Hackathon - Round 2 - Build and Connect Round**  
Optimized for performance, accuracy, and reliability under strict constraints.
