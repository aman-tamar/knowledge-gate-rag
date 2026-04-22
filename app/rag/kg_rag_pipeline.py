from groq import Groq
from app.kg.graph_query import find_connection, format_path

# CONFIG

GROQ_API_KEY = "YOUR_API_KEY"

llm = Groq(api_key=GROQ_API_KEY)




# EXTRACT ENTITIES 



def extract_entities(question):
    prompt = f"""
Extract the main entities from the question.

Return ONLY comma-separated entities.

Example:
Question: How do central banks affect liquidity?
Output: Central Banks, Liquidity

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

# BUILD CONTEXT

def build_context(paths):
    context = ""

    for nodes, rels in paths:
        for i in range(len(rels)):
            context += f"{nodes[i]} {rels[i].lower()} {nodes[i+1]}. "
    
    return context

# GENERATE ANSWER

def generate_answer(question, context):
    prompt = f"""
You are a knowledgeable AI assistant.

Use the provided context to answer the question.

Context:
{context}

Question:
{question}

Answer clearly and logically:
"""

    response = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# MAIN TEST

if __name__ == "__main__":

    question = "How do central banks affect liquidity?"

    # manually chosen entities for now
    entities = extract_entities(question)

    if len(entities) < 2:
        print("Not enough entities found")
        exit()

    e1, e2 = entities[0], entities[1]

    paths = find_connection(e1, e2)

    if not paths:
        print("No knowledge found")
    else:
        context = build_context(paths)

        print("\nGenerated Context:\n")
        print(context)

        answer = generate_answer(question, context)

        print("\nFinal Answer:\n")
        print(answer)