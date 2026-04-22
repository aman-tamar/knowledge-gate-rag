from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USERNAME = ""
PASSWORD = ""  

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def test_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Neo4j Connected' AS message")
        for record in result:
            print(record["message"])

if __name__ == "__main__":
    test_connection()