from neo4j import GraphDatabase
from datetime import datetime

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "1597536842"))


def add_created_at_property():
    with driver.session() as session:
        current_time = datetime.now().isoformat()
        query = f"MATCH (n:Node) SET n.created_at = '{current_time}'"
        session.run(query)
        print(f"Tüm düğümlere created_at özelliği {current_time} olarak eklendi.")


if __name__ == "__main__":
    add_created_at_property()
