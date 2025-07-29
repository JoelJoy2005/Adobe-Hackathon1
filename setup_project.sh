#!/bin/bash

# Create the project structure for PDF processing challenge
echo "Setting up Challenge_1a project structure..."

# Create main directory
mkdir -p Challenge_1a

# Navigate to the project directory
cd Challenge_1a

# Create sample_dataset structure
mkdir -p sample_dataset/outputs
mkdir -p sample_dataset/pdfs
mkdir -p sample_dataset/schema

# Create output schema file
cat > sample_dataset/schema/output_schema.json << 'EOF'
{
  "type": "object",
  "properties": {
    "document_info": {
      "type": "object",
      "properties": {
        "filename": {"type": "string"},
        "total_pages": {"type": "integer"},
        "creation_date": {"type": "string"},
        "modification_date": {"type": "string"},
        "author": {"type": "string"},
        "title": {"type": "string"},
        "subject": {"type": "string"}
      },
      "required": ["filename", "total_pages"]
    },
    "content": {
      "type": "object",
      "properties": {
        "pages": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "page_number": {"type": "integer"},
              "text_content": {"type": "string"},
              "text_blocks": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "bbox": {"type": "array", "items": {"type": "number"}},
                    "text": {"type": "string"},
                    "font_size": {"type": "number"},
                    "font": {"type": "string"}
                  },
                  "required": ["bbox", "text"]
                }
              },
              "images": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "bbox": {"type": "array", "items": {"type": "number"}},
                    "width": {"type": "integer"},
                    "height": {"type": "integer"}
                  },
                  "required": ["bbox", "width", "height"]
                }
              },
              "tables": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "bbox": {"type": "array", "items": {"type": "number"}},
                    "rows": {"type": "integer"},
                    "columns": {"type": "integer"},
                    "data": {
                      "type": "array",
                      "items": {
                        "type": "array",
                        "items": {"type": "string"}
                      }
                    }
                  },
                  "required": ["bbox", "rows", "columns", "data"]
                }
              }
            },
            "required": ["page_number", "text_content", "text_blocks"]
          }
        },
        "summary": {
          "type": "object",
          "properties": {
            "total_text_length": {"type": "integer"},
            "total_images": {"type": "integer"},
            "total_tables": {"type": "integer"},
            "language": {"type": "string"}
          },
          "required": ["total_text_length", "total_images", "total_tables"]
        }
      },
      "required": ["pages", "summary"]
    }
  },
  "required": ["document_info", "content"]
}
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
PyMuPDF==1.23.5
python-dateutil==2.8.2
EOF

# Create .dockerignore
cat > .dockerignore << 'EOF'
sample_dataset/
*.md
.git/
.gitignore
setup_project.sh
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.pytest_cache/
EOF

echo "Project structure created successfully!"
echo "Directory structure:"
echo "Challenge_1a/"
echo "├── sample_dataset/"
echo "│   ├── outputs/"
echo "│   ├── pdfs/"
echo "│   └── schema/"
echo "│       └── output_schema.json"
echo "├── requirements.txt"
echo "├── .dockerignore"
echo "└── (Dockerfile and process_pdfs.py will be created next)"
echo ""
echo "To complete setup:"
echo "1. Run the Python script creation commands"
echo "2. Place your test PDFs in sample_dataset/pdfs/"
echo "3. Build and test the Docker container"
