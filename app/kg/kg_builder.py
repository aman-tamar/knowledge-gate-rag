from groq import Groq
from neo4j import GraphDatabase
import re
from nltk.stem import WordNetLemmatizer
import nltk

#  SETUP

nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

#  CONFIG

GROQ_API_KEY = "YOUR_API_KEY"

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = ""
NEO4J_PASSWORD = ""

# INIT 

llm = Groq(api_key=GROQ_API_KEY)

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

#  SPLIT TEXT 

def split_text(text):
    sentences = re.split(r'[.?!]', text)
    return [s.strip() for s in sentences if s.strip()]

#  LLM: Extract Triples

def extract_triples(text):
    prompt = f"""
Extract meaningful knowledge graph triples from the text.

Follow STRICTLY:
- Output ONLY triples
- Format: (Entity1, relation, Entity2)
- One triple per line
- Keep relations short (1–3 words)
- Avoid duplicates
- Ignore weak or unimportant relations

Examples:

Text:
Bitcoin is influenced by interest rates. Interest rates are controlled by central banks.

Output:
(Bitcoin, influenced by, interest rates)
(Interest rates, controlled by, central banks)

Text:
Edge maps help reduce blurriness in images. Blurriness affects image quality.

Output:
(Edge maps, reduce, blurriness)
(Blurriness, affects, image quality)

Now extract triples from:

Text:
{text}
"""

    response = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

#  CLEAN ENTITY 

def clean_entity(entity):
    entity = entity.lower().strip()
    entity = " ".join(entity.split())
    return entity.title()

#  CLEAN RELATION 

def clean_relation(rel):
    rel = rel.lower().strip()

    
    rel = re.sub(r'\b(is|are|was|were|be|been|being)\b', '', rel)

    
    rel = " ".join(rel.split())

    
    words = rel.split()
    words = [lemmatizer.lemmatize(w, pos='v') for w in words]

    rel = "_".join(words)

    return rel

#  PARSE TRIPLES

def parse_triples(triples_text):
    triples = []
    lines = triples_text.strip().split("\n")

    for line in lines:
        line = line.strip()

        if line.startswith("(") and line.endswith(")"):
            parts = line[1:-1].split(",")

            if len(parts) == 3:
                e1 = clean_entity(parts[0])
                rel = clean_relation(parts[1])
                e2 = clean_entity(parts[2])

                triples.append((e1, rel, e2))

    return triples

#  STORE IN NEO4J

def store_triples(triples):
    with driver.session() as session:
        for e1, rel, e2 in triples:
            rel = rel.replace(" ", "_").upper()
            query = f"""
            MERGE (a:Entity {{name: $e1}})
            MERGE (b:Entity {{name: $e2}})
            MERGE (a)-[r:{rel}]->(b)
            """
            session.run(query, e1=e1, e2=e2)

# MAIN TEST 

if __name__ == "__main__":

    text = """
    Bitcoin dropped last week because interest rates increased.
    Interest rates are affecting liquidity in financial markets.
    Reduced liquidity causes institutional investors to sell assets.
    Central banks control interest rates.
    """

    sentences = split_text(text)

    all_triples = []

    for sentence in sentences:
        triples_text = extract_triples(sentence)

        print("\nSentence:", sentence)
        print("LLM Output:", triples_text)

        triples = parse_triples(triples_text)

        print("Parsed:", triples)

        all_triples.extend(triples)

    store_triples(all_triples)

    print("\nStored in Neo4j")