#!/usr/bin/env python3
"""
Optimized PDF Processing Solution for National Level Hackathon
Using PyMuPDF for high-performance PDF extraction and analysis
"""

import fitz  # PyMuPDF
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
import re

class OptimizedPDFProcessor:
    def __init__(self, input_dir="/app/input", output_dir="/app/output"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance optimizations
        self.max_workers = min(8, os.cpu_count() or 4)  # Use available CPUs efficiently
        self.chunk_size = 1024 * 1024  # 1MB chunks for memory management
        
    def extract_document_metadata(self, doc):
        """Extract document metadata efficiently"""
        metadata = doc.metadata
        
        # Convert dates safely
        creation_date = ""
        modification_date = ""
        
        try:
            if metadata.get('creationDate'):
                # Handle PDF date format (D:YYYYMMDDHHmmSSOHH'mm')
                date_str = metadata['creationDate']
                if date_str.startswith('D:'):
                    date_str = date_str[2:16]  # Extract YYYYMMDDHHMMSS part
                    creation_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} {date_str[8:10]}:{date_str[10:12]}:{date_str[12:14]}"
                else:
                    creation_date = date_str
        except:
            creation_date = ""
            
        try:
            if metadata.get('modDate'):
                date_str = metadata['modDate']
                if date_str.startswith('D:'):
                    date_str = date_str[2:16]
                    modification_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} {date_str[8:10]}:{date_str[10:12]}:{date_str[12:14]}"
                else:
                    modification_date = date_str
        except:
            modification_date = ""
        
        return {
            "creation_date": creation_date,
            "modification_date": modification_date,
            "author": metadata.get('author', ''),
            "title": metadata.get('title', ''),
            "subject": metadata.get('subject', '')
        }
    
    def detect_tables(self, page):
        """Simple table detection using text blocks and positioning"""
        tables = []
        text_dict = page.get_text("dict")
        
        # Group text blocks by similar y-coordinates (rows)
        rows = {}
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    y = round(line["bbox"][1], 1)  # Round y-coordinate
                    if y not in rows:
                        rows[y] = []
                    
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"] + " "
                    
                    if line_text.strip():
                        rows[y].append({
                            "x": line["bbox"][0],
                            "text": line_text.strip(),
                            "bbox": line["bbox"]
                        })
        
        # Detect table-like structures (multiple aligned columns)
        potential_tables = []
        row_keys = sorted(rows.keys())
        
        for i in range(len(row_keys) - 2):  # Need at least 3 rows for a table
            current_rows = []
            y_start = row_keys[i]
            
            # Check next few rows for alignment
            for j in range(i, min(i + 10, len(row_keys))):  # Check up to 10 rows
                y = row_keys[j]
                if len(rows[y]) >= 2:  # Multiple columns
                    current_rows.append(rows[y])
                else:
                    break
            
            if len(current_rows) >= 3:  # Valid table with 3+ rows
                # Convert to table format
                table_data = []
                max_cols = max(len(row) for row in current_rows)
                
                for row in current_rows:
                    # Sort by x-coordinate and pad missing columns
                    sorted_row = sorted(row, key=lambda x: x["x"])
                    row_data = [item["text"] for item in sorted_row]
                    
                    # Pad with empty strings if needed
                    while len(row_data) < max_cols:
                        row_data.append("")
                    
                    table_data.append(row_data[:max_cols])  # Ensure consistent column count
                
                if table_data:
                    # Calculate bounding box
                    all_bboxes = []
                    for row in current_rows:
                        for item in row:
                            all_bboxes.append(item["bbox"])
                    
                    if all_bboxes:
                        min_x = min(bbox[0] for bbox in all_bboxes)
                        min_y = min(bbox[1] for bbox in all_bboxes)
                        max_x = max(bbox[2] for bbox in all_bboxes)
                        max_y = max(bbox[3] for bbox in all_bboxes)
                        
                        tables.append({
                            "bbox": [min_x, min_y, max_x, max_y],
                            "rows": len(table_data),
                            "columns": max_cols,
                            "data": table_data
                        })
                
                # Skip processed rows
                i = j
        
        return tables
    
    def process_single_page(self, page, page_num):
        """Process a single page efficiently"""
        # Extract text with formatting information
        text_dict = page.get_text("dict")
        page_text = page.get_text()
        
        # Extract text blocks with formatting
        text_blocks = []
        for block in text_dict["blocks"]:
            if "lines" in block:
                block_text = ""
                font_info = {"size": 12, "name": "unknown"}
                
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                        # Get font information from first span
                        if span["text"].strip():
                            font_info["size"] = span.get("size", 12)
                            font_info["name"] = span.get("font", "unknown")
                
                if block_text.strip():
                    text_blocks.append({
                        "bbox": block["bbox"],
                        "text": block_text.strip(),
                        "font_size": font_info["size"],
                        "font": font_info["name"]
                    })
        
        # Extract images
        images = []
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bbox = page.get_image_bbox(img)
                
                images.append({
                    "bbox": list(image_bbox),
                    "width": base_image["width"],
                    "height": base_image["height"]
                })
            except:
                # Skip problematic images
                continue
        
        # Detect tables
        tables = self.detect_tables(page)
        
        return {
            "page_number": page_num + 1,
            "text_content": page_text,
            "text_blocks": text_blocks,
            "images": images,
            "tables": tables
        }
    
    def detect_language(self, text):
        """Simple language detection based on character patterns"""
        if not text:
            return "unknown"
        
        # Count different character types
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u00C0-\u017F\u0400-\u04FF\u4E00-\u9FFF]', text))
        
        if total_chars == 0:
            return "unknown"
        
        latin_ratio = latin_chars / total_chars
        
        if latin_ratio > 0.8:
            return "en"  # Primarily Latin script
        elif latin_ratio > 0.5:
            return "mixed"
        else:
            return "non-latin"
    
    def process_pdf(self, pdf_path):
        """Process a single PDF file with optimizations"""
        start_time = time.time()
        filename = pdf_path.name
        
        try:
            # Open PDF with memory optimization
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            # Extract metadata
            metadata = self.extract_document_metadata(doc)
            
            # Process pages in batches to manage memory
            pages_data = []
            batch_size = min(10, total_pages)  # Process in batches of 10 pages
            
            for batch_start in range(0, total_pages, batch_size):
                batch_end = min(batch_start + batch_size, total_pages)
                batch_pages = []
                
                # Process batch of pages
                for page_num in range(batch_start, batch_end):
                    page = doc[page_num]
                    page_data = self.process_single_page(page, page_num)
                    batch_pages.append(page_data)
                    
                    # Clean up page resources
                    page = None
                
                pages_data.extend(batch_pages)
                
                # Force garbage collection after each batch
                gc.collect()
            
            # Calculate summary statistics
            total_text_length = sum(len(page["text_content"]) for page in pages_data)
            total_images = sum(len(page["images"]) for page in pages_data)
            total_tables = sum(len(page["tables"]) for page in pages_data)
            
            # Detect language from first page text
            language = "unknown"
            if pages_data:
                language = self.detect_language(pages_data[0]["text_content"])
            
            # Build final JSON structure
            output_data = {
                "document_info": {
                    "filename": filename,
                    "total_pages": total_pages,
                    **metadata
                },
                "content": {
                    "pages": pages_data,
                    "summary": {
                        "total_text_length": total_text_length,
                        "total_images": total_images,
                        "total_tables": total_tables,
                        "language": language
                    }
                }
            }
            
            # Save JSON output
            output_file = self.output_dir / f"{pdf_path.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            doc.close()
            doc = None
            
            processing_time = time.time() - start_time
            print(f"Processed {filename}: {total_pages} pages in {processing_time:.2f}s")
            
            return True, filename, processing_time
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            return False, filename, 0
    
    def process_all_pdfs(self):
        """Process all PDFs in the input directory with parallel processing"""
        if not self.input_dir.exists():
            print(f"Input directory {self.input_dir} does not exist!")
            return
        
        pdf_files = list(self.input_dir.glob("*.pdf"))
        if not pdf_files:
            print("No PDF files found in input directory!")
            return
        
        print(f"Found {len(pdf_files)} PDF files to process...")
        
        # Process PDFs with controlled parallelism
        successful = 0
        total_time = 0
        
        # For memory efficiency, limit concurrent processing
        max_concurrent = min(4, self.max_workers, len(pdf_files))
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all tasks
            future_to_pdf = {
                executor.submit(self.process_pdf, pdf_file): pdf_file 
                for pdf_file in pdf_files
            }
            
            # Process completed tasks
            for future in as_completed(future_to_pdf):
                pdf_file = future_to_pdf[future]
                try:
                    success, filename, proc_time = future.result()
                    if success:
                        successful += 1
                        total_time += proc_time
                except Exception as e:
                    print(f"Exception processing {pdf_file.name}: {str(e)}")
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {successful}/{len(pdf_files)} files")
        if successful > 0:
            print(f"Average processing time: {total_time/successful:.2f}s per file")

def main():
    """Main entry point"""
    print("Starting optimized PDF processing...")
    print(f"Python version: {sys.version}")
    print(f"PyMuPDF version: {fitz.version[0]}")
    
    start_time = time.time()
    
    # Initialize processor
    processor = OptimizedPDFProcessor()
    
    # Process all PDFs
    processor.process_all_pdfs()
    
    total_time = time.time() - start_time
    print(f"\nTotal execution time: {total_time:.2f}s")
    
    # Force final cleanup
    gc.collect()

if __name__ == "__main__":
    main()
