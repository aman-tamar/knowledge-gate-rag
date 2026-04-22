import fitz  # PyMuPDF

# LOAD PDF

def load_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text

# SPLIT TEXT 

def split_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

# MAIN TEST

if __name__ == "__main__":
    file_path = "data/sample.pdf"  # put your PDF here

    text = load_pdf(file_path)

    print("\nTotal text length:", len(text))

    chunks = split_text(text)

    print("\nNumber of chunks:", len(chunks))

    print("\nSample chunk:\n")
    print(chunks[0])