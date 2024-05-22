from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "1597536842"))


def remove_status_property():
    with driver.session() as session:
        query = "MATCH (n:Node) REMOVE n.status"
        session.run(query)
        print("Tüm düğümlerden status özelliği kaldırıldı.")


if __name__ == "__main__":
    remove_status_property()
