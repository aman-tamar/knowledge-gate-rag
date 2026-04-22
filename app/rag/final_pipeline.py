from groq import Groq
from app.kg.graph_query import find_connection
from app.rag.vector_store import VectorStore
from sentence_transformers import SentenceTransformer
import numpy as np

# CONFIG 

GROQ_API_KEY = "YOUR_API_KEY"
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
llm = Groq(api_key=GROQ_API_KEY)


# FILTERING PATHS ON SIMILARITY 

def format_path_text(nodes, rels):
    text = ""
    for i in range(len(rels)):
        text += f"{nodes[i]} {rels[i].lower()} "
    text += nodes[-1]
    return text


def filter_paths_by_question(paths, question, embed_model, top_k=3):
    scored = []

    q_emb = embed_model.encode([question])[0]

    for nodes, rels in paths:
        sentence = ""

        for i in range(len(rels)):
            sentence += f"{nodes[i]} {rels[i].lower()} {nodes[i+1]} "

        path_emb = embed_model.encode([sentence])[0]

        score = (q_emb @ path_emb)

        scored.append((score, nodes, rels))

    scored.sort(reverse=True, key=lambda x: x[0])

    return scored[:top_k]   

# ENTITY EXTRACTION

def extract_entities(question):
    prompt = f"""
Extract the main entities from the question.

Return ONLY comma-separated entities.

Question:
{question}
"""

    response = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    output = response.choices[0].message.content.strip()
    entities = [e.strip() for e in output.split(",")]

    return entities

# BUILD KG CONTEXT

def build_kg_context(scored_paths):
    context = ""
    queries = []

    for score, nodes, rels in scored_paths:
        for i in range(len(rels)):
            sentence = f"{nodes[i]} {rels[i].lower()} {nodes[i+1]}"
            
            context += sentence + ". "
            queries.append((sentence, score))  

    return context, queries

# GENERATE FINAL ANSWER

def generate_answer(question, kg_context, docs):
    docs_text = "\n".join(docs)

    prompt = f"""
You are an intelligent AI assistant.

Answer the question clearly and concisely using the provided information.

Focus on the most relevant reasoning.
Avoid repetition.
Keep answer short and precise (3–5 sentences).

Context:
{kg_context}

Additional Information:
{docs_text}

Question:
{question}

Answer:
"""

    response = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content



def rank_paths(paths):
    scored = []

    for nodes, rels in paths:
        length_score = 1 / len(nodes)
        diversity_score = len(set(nodes)) / len(nodes)

        score = length_score + diversity_score

        scored.append((score, nodes, rels))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [(nodes, rels) for _, nodes, rels in scored[:4]]


def retrieve_weighted_docs(store, queries, question):
    q_emb = embed_model.encode([question])[0]

    doc_scores = {}

    for query, path_score in queries:
        results = store.search(query, k=2)

        for doc in results:
            doc_emb = embed_model.encode([doc])[0]

            sim = (q_emb @ doc_emb)

            final_score = sim * path_score 

            if doc in doc_scores:
                doc_scores[doc] = max(doc_scores[doc], final_score)
            else:
                doc_scores[doc] = final_score

    
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

    return [doc for doc, _ in sorted_docs[:5]]


def run_pipeline(question: str):

    from app.kg.entity_matcher import get_all_entities, match_entity
    from app.kg.graph_query import find_connection
    from app.rag.vector_store import VectorStore

    store = VectorStore()
    store.load()

    # extract entities
    entities = extract_entities(question)

    if len(entities) < 2:
        docs = store.search(question, k=5)
        return generate_answer(question, "", docs)

    kg_entities = get_all_entities()

    e1 = match_entity(entities[0], kg_entities)
    e2 = match_entity(entities[1], kg_entities)

    if not e1 or not e2:
        docs = store.search(question, k=5)
        return generate_answer(question, "", docs)

    e1 = e1.title()
    e2 = e2.title()

    paths = find_connection(e1, e2)

    scored_paths  = filter_paths_by_question(paths, question, embed_model)

    kg_context, queries = build_kg_context(scored_paths )

    docs = retrieve_weighted_docs(store, queries, question)

    answer = generate_answer(question, kg_context, docs)

    return answer


if __name__ == "__main__":
    from app.kg.entity_matcher import get_all_entities, match_entity

    
    store = VectorStore()
    store.load()

    question = "How are images processed before training?"

    
    entities = extract_entities(question)

    if len(entities) < 2:
        print("Not enough entities ")
        exit()

    kg_entities = get_all_entities()

    e1 = match_entity(entities[0], kg_entities)
    e2 = match_entity(entities[1], kg_entities)

    if not e1 or not e2:
        print("Entity matching failed, using RAG fallback...")

        docs = store.search(question, k=5)

        answer = generate_answer(question, "", docs)

        print("\nFINAL ANSWER:\n")
        print(answer)

        exit()

    print("\nExtracted Entities:", entities)
    print("Using Entities for KG:", e1, e2)

     
    e1 = e1.title()

    paths = find_connection(e1, e2)

    print("\n Raw KG Paths:")
    for nodes, rels in paths:
        print(nodes, rels)

    
    paths = rank_paths(paths)
    paths = filter_paths_by_question(paths, question)

    print("\n Final Selected Paths:")
    for nodes, rels in paths:
        print(nodes, rels)

    
    if len(paths) < 2:
        print(" Weak KG context, boosting with RAG...")

    
    kg_context, queries = build_kg_context(paths)

    print("\n Retrieval Queries:")
    for q in queries:
        print(q)

    
    docs = retrieve_weighted_docs(store, queries, question)

    print("\n Retrieved Docs:")
    for d in docs:
        print(d[:150], "\n---")

   
    answer = generate_answer(question, kg_context, docs)

    print("\nFINAL ANSWER:\n")
    print(answer)