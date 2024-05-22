from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "1597536842"

def delete_all_relationships():
    query = """
    MATCH (n)-[r]->(m)
    DELETE r
    """

    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            session.run(query)
            print("Tüm ilişkiler başarıyla silindi.")

if __name__ == "__main__":
    delete_all_relationships()
