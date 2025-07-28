# Multi-stage build for optimized production image
FROM --platform=linux/amd64 python:3.10-slim as builder

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
WORKDIR /build
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM --platform=linux/amd64 python:3.10-slim

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Create app user and directory
RUN useradd --create-home --shell /bin/bash app
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/app/.local

# Copy application code
COPY process_pdfs.py .

# Set ownership and permissions
RUN chown -R app:app /app
USER app

# Add local Python packages to PATH
ENV PATH=/home/app/.local/bin:$PATH
ENV PYTHONPATH=/home/app/.local/lib/python3.10/site-packages:$PYTHONPATH

# Optimize Python settings for performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONHASHSEED=random

# Set memory and CPU optimizations
ENV OMP_NUM_THREADS=8
ENV MKL_NUM_THREADS=8
ENV NUMEXPR_NUM_THREADS=8

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import fitz; print('PyMuPDF ready')" || exit 1

# Run the PDF processor
CMD ["python", "process_pdfs.py"]
