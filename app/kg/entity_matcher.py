from neo4j import GraphDatabase
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# CONFIG 

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = ""
NEO4J_PASSWORD = ""

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

# GET ALL ENTITIES 

def get_all_entities():
    query = "MATCH (e:Entity) RETURN e.name AS name"

    with driver.session() as session:
        result = session.run(query)
        entities = [record["name"] for record in result]

    return entities

# MATCH ENTITY 

def match_entity(user_entity, kg_entities):
    best_match = None
    best_score = 0

    for entity in kg_entities:
        score = fuzz.ratio(user_entity.lower(), entity.lower())

        if score > best_score:
            best_score = score
            best_match = entity

    if best_score > 75:
        return best_match

    user_emb = model.encode([user_entity])[0]

    best_match = None
    best_sim = -1

    for entity in kg_entities:
        ent_emb = model.encode([entity])[0]
        sim = np.dot(user_emb, ent_emb)

        if sim > best_sim:
            best_sim = sim
            best_match = entity

    if best_sim > 0.5:
        return best_match

    return None