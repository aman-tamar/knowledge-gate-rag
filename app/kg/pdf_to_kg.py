from app.rag.pdf_loader import load_pdf, split_text
from app.kg.kg_builder import extract_triples, parse_triples, store_triples
import re

# SPLIT SENTENCES

def split_sentences(text):
    sentences = re.split(r'[.?!]', text)
    return [s.strip() for s in sentences if s.strip()]


# SPLIT SENTENCES
def process_pdf(file_path):
    print("Processing PDF...")

    
    text = load_pdf(file_path)
    chunks = split_text(text, chunk_size=500, overlap=100)

    # VECTOR STORE 
    from app.rag.vector_store import VectorStore

    store = VectorStore()
    store.clear()             
    store.add_texts(chunks)
    store.save()

    print("Vector store updated")

    #  KG BUILD 
    all_triples = []

    for chunk in chunks:

        
        if len(chunk.split()) < 30:
            continue

        # ONE API CALL PER CHUNK
        triples_text = extract_triples(chunk)

        triples = parse_triples(triples_text)

        all_triples.extend(triples)

    clean_triples = []

    for e1, rel, e2 in all_triples:
        if not rel or rel.strip() == "":
            continue
        if not e1 or not e2:
            continue

        clean_triples.append((e1.strip(), rel.strip(), e2.strip()))

    all_triples = list(set(clean_triples))
    print("Sample triples:", all_triples[:5])
    
    from app.kg.graph_query import clear_graph
    clear_graph()

    store_triples(all_triples)

    print("KG + Vector store ready")

#  MAIN 

if __name__ == "__main__":

    file_path = "data/sample.pdf"

    print("Loading PDF...")
    text = load_pdf(file_path)

    print("Splitting into chunks...")
    chunks = split_text(text, chunk_size=500, overlap=100)

    all_triples = []

    print("Building Knowledge Graph...")

    for chunk in chunks:
        sentences = split_sentences(chunk)

        for sentence in sentences:

            
            if len(sentence.split()) < 5:
                continue

            triples_text = extract_triples(sentence)


            triples = parse_triples(triples_text)

            all_triples.extend(triples)

    print(f"Total triples extracted: {len(all_triples)}")

    
    all_triples = list(set(all_triples))

    print(f"Unique triples: {len(all_triples)}")

    store_triples(all_triples)

    print("KG stored in Neo4j")