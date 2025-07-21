from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import json
import os

def extract_outline(pdf_path):
    outline = []
    title = ""
    font_sizes = {}

    for page_num, page_layout in enumerate(extract_pages(pdf_path), start=1):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    line_text = text_line.get_text().strip()
                    if not line_text:
                        continue
                    
                    # Get font size (average of characters in line)
                    font_size = sum(char.size for char in text_line if isinstance(char, LTChar)) / max(len(text_line), 1)

                    # Grouping font sizes
                    rounded = round(font_size)
                    font_sizes[rounded] = font_sizes.get(rounded, 0) + 1

                    # Identify possible headings
                    if len(line_text.split()) <= 10 and line_text.istitle():
                        outline.append({
                            "level": "H1",  # Placeholder: change later using font hierarchy
                            "text": line_text,
                            "page": page_num
                        })

    # Assign actual levels based on top font sizes
    sizes = sorted(font_sizes.items(), key=lambda x: x[0], reverse=True)
    if sizes:
        biggest = sizes[0][0]
        second = sizes[1][0] if len(sizes) > 1 else biggest - 1
        third = sizes[2][0] if len(sizes) > 2 else second - 1

    for item in outline:
        # Simulate logic by mapping font size to level
        # Replace with actual font size logic per line if available
        item["level"] = "H1"

    return {"title": "Unknown Title", "outline": outline}

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"

    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, file)
            result = extract_outline(pdf_path)

            out_file = os.path.join(output_dir, file.replace(".pdf", ".json"))
            with open(out_file, "w") as f:
                json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
