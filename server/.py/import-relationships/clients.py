import requests
import re
import math

uri = "bolt://localhost:7687"
username = "neo4j"
password = "1597536842"

driver = GraphDatabase.driver(uri, auth=(username, password))


def fetch_clients_from_api():
    api_url = "http://127.0.0.1:5001/get-client-types"
    response = requests.get(api_url)
    if response.status_code == 200:
        clients = response.json()
        return ["UNKNOWN" if client is None or (isinstance(client, float) and math.isnan(client)) else client for client in clients]
    else:
        print("API'den veri çekilemedi, HTTP Status:", response.status_code)
        return []


def clean_string(client):
    if client == "UNKNOWN":
        return client
    elif client == "":
        return "UNKNOWN"
    cleaned_string = re.sub(r'[^a-zA-Z\s]', '', client)
    cleaned_string = cleaned_string.replace(' ', '')
    return cleaned_string.upper()


def create_relationships(tx, client, cleaned_client):
    if not cleaned_client:
        return
    query = f"""
    MATCH (n:Node {{client: '{client}'}})
    WITH n
    ORDER BY id(n)
    WITH collect(n) AS nodes
    UNWIND range(0, size(nodes) - 2) AS i
    WITH nodes, nodes[i] AS n1, nodes[i + 1] AS n2
    MERGE (n1)-[:CLIENT_{cleaned_client}]->(n2)
    WITH nodes
    WITH nodes[size(nodes)-1] AS last, nodes[0] AS first
    MERGE (last)-[:CLIENT_{cleaned_client}]->(first)
    """
    tx.run(query)


def main():
    clients = fetch_clients_from_api()
    if not clients:
        return

    print(f"Fetched clients: {clients}")

    with driver.session() as session:
        for client in clients:
            clean_client = clean_string(client)
            session.execute_write(create_relationships, client, clean_client)
            print(f"İlişkiler oluşturuldu: {client} - {clean_client}")
        print("İlişkiler başarıyla oluşturuldu.")


if __name__ == "__main__":
    main()
