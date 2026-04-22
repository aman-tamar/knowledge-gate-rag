from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

# INIT MODEL 

model = SentenceTransformer("BAAI/bge-base-en-v1.5")

#  CREATE VECTOR STORE

class VectorStore:
    def __init__(self):
        self.texts = []
        self.index = None

    def add_texts(self, texts):
        embeddings = model.encode(texts)

        self.texts.extend(texts)

        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)

        self.index.add(np.array(embeddings))

    def search(self, query, k=5):
        query_embedding = model.encode([query])

        distances, indices = self.index.search(np.array(query_embedding), k)

        results = []
        for idx in indices[0]:
            results.append(self.texts[idx])

        return results

    def save(self, path="vector_store.pkl"):
        with open(path, "wb") as f:
            pickle.dump((self.texts, self.index), f)

    def load(self, path="vector_store.pkl"):
        with open(path, "rb") as f:
            self.texts, self.index = pickle.load(f)

    def clear(self):
        self.index = None
        self.texts = []

#  MAIN TEST 

if __name__ == "__main__":

    from app.rag.pdf_loader import load_pdf, split_text

    file_path = "data/sample.pdf"

    text = load_pdf(file_path)
    chunks = split_text(text)

    store = VectorStore()
    store.add_texts(chunks)

    store.save()

    print("Vector store created")

    # test query
    query = "What is the main topic?"

    results = store.search(query)

    print("\nTop results:\n")
    for r in results:
        print(r[:200], "\n---")