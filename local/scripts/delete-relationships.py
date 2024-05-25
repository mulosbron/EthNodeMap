from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "1597536842"))


def delete_all_relationships():
    with driver.session() as session:
        query = "MATCH (n)-[r]->(m) DELETE r"
        session.run(query)
        print("Tüm ilişkiler başarıyla silindi.")


if __name__ == "__main__":
    delete_all_relationships()
