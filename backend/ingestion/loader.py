import os
import fitz
from pathlib import Path


def load_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    metadata = {"source": os.path.basename(file_path), "total_pages": len(doc)}
    page_texts = []

    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        page_texts.append({"page": page_num + 1, "text": page_text})
        text += f"--- Page {page_num + 1} ---\n{page_text}\n"

    doc.close()
    return text, metadata, page_texts


def load_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    metadata = {"source": os.path.basename(file_path), "total_pages": 1}
    return text, metadata, [{"page": 1, "text": text}]


def load_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    metadata = {"source": os.path.basename(file_path), "total_pages": 1}
    return text, metadata, [{"page": 1, "text": text}]


def load_document(file_path):
    file_ext = Path(file_path).suffix.lower()

    if file_ext == '.pdf':
        return load_pdf(file_path)
    elif file_ext == '.txt':
        return load_txt(file_path)
    elif file_ext in ['.md', '.markdown']:
        return load_markdown(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")


def load_all_documents(documents_dir):
    documents = []
    supported_extensions = {'.pdf', '.txt', '.md', '.markdown'}

    for file_path in Path(documents_dir).iterdir():
        if file_path.suffix.lower() in supported_extensions:
            try:
                text, metadata, page_texts = load_document(str(file_path))
                documents.append({
                    "text": text,
                    "metadata": metadata,
                    "page_texts": page_texts
                })
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    return documents
