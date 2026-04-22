from neo4j import GraphDatabase

# CONFIG 

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = ""
NEO4J_PASSWORD = ""

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

#  FIND CONNECTION 

def find_connection(entity1, entity2):
    query = """
    MATCH path = (a:Entity {name: $e1})-[*1..4]-(b:Entity {name: $e2})
    WHERE ALL(n IN nodes(path) WHERE SINGLE(x IN nodes(path) WHERE x = n))
    RETURN path
    LIMIT 20
    """

    with driver.session() as session:
        result = session.run(query, e1=entity1, e2=entity2)

        paths = []

        for record in result:
            path = record["path"]

            nodes = [node["name"] for node in path.nodes]
            rels = [rel.type for rel in path.relationships]

            paths.append((nodes, rels))

        # remove duplicates
        unique_paths = []
        seen = set()

        for nodes, rels in paths:
            key = tuple(nodes)
            if key not in seen:
                seen.add(key)
                unique_paths.append((nodes, rels))

        return unique_paths

#  FORMAT OUTPUT 

def format_path(nodes, rels):
    result = ""
    for i in range(len(rels)):
        result += f"{nodes[i]} --{rels[i]}--> "
    result += nodes[-1]
    return result

def clear_graph():
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

#  MAIN TEST 

if __name__ == "__main__":

    e1 = "Bitcoin"
    e2 = "Liquidity"

    paths = find_connection(e1, e2)

    if not paths:
        print("No connection found")
    else:
        print("\nConnections found:\n")
        for nodes, rels in paths:
            print(format_path(nodes, rels))