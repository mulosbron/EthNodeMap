import math

from neo4j import GraphDatabase
import requests

uri = "bolt://localhost:7687"
username = "neo4j"
password = "1597536842"

driver = GraphDatabase.driver(uri, auth=(username, password))


def fetch_os_types_from_api():
    api_url = "http://127.0.0.1:5001/get-os-types"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        os_types = response.json()
        return [os_type for os_type in os_types if os_type and (isinstance(os_type, str) or (isinstance(os_type, float) and not math.isnan(os_type)))]
    except requests.exceptions.RequestException as e:
        print(f"API'den veri çekilemedi: {e}")
        return []


def classify_os(os_type):
    if isinstance(os_type, str):
        os_type_lower = os_type.lower()
        if "linux" in os_type_lower:
            return "LINUX"
        elif "windows" in os_type_lower:
            return "WINDOWS"
        elif "darwin" in os_type_lower:
            return "DARWIN"
        elif "android" in os_type_lower:
            return "ANDROID"
        elif "macos" in os_type_lower:
            return "MACOS"
        elif "freebsd" in os_type_lower:
            return "FREEBSD"
    return "UNKNOWN"


def create_relationships(tx, os_type):
    query = f"""
    MATCH (n:Node {{os: '{os_type}'}})
    WITH n
    ORDER BY id(n)
    WITH collect(n) AS nodes
    UNWIND range(0, size(nodes) - 2) AS i
    WITH nodes, nodes[i] AS n1, nodes[i + 1] AS n2
    MERGE (n1)-[:OS_{classify_os(os_type)}]->(n2)
    WITH nodes
    WITH nodes[size(nodes)-1] AS last, nodes[0] AS first
    MERGE (last)-[:OS_{classify_os(os_type)}]->(first)
    """
    tx.run(query)


def main():
    os_types = fetch_os_types_from_api()
    if not os_types:
        return

    print(f"Fetched OS types: {os_types}")

    with driver.session() as session:
        for os_type in os_types:
            session.execute_write(create_relationships, os_type)
            print(f"İlişkiler oluşturuldu: {os_type} - {classify_os(os_type)}")

        print("İlişkiler başarıyla oluşturuldu.")


if __name__ == "__main__":
    main()
