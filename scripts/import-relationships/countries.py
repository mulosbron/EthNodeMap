from neo4j import GraphDatabase
import requests
import re

uri = "bolt://localhost:7687"
username = "neo4j"
password = "1597536842"

driver = GraphDatabase.driver(uri, auth=(username, password))


def fetch_countries_from_api():
    api_url = "http://127.0.0.1:5001/get-countries"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        countries = response.json()
        return [country for country in countries if country]
    except requests.exceptions.RequestException as e:
        print(f"API'den veri çekilemedi: {e}")
        return []


def clean_string(value):
    cleaned_value = re.sub(r'\s+', '', value)
    return cleaned_value.upper()


def create_country_relationships(tx, country, cleaned_country):
    query = f"""
    MATCH (n:Node {{country_name: '{country}'}})
    WITH n
    ORDER BY id(n)
    WITH collect(n) AS nodes
    UNWIND range(0, size(nodes) - 2) AS i
    WITH nodes, nodes[i] AS n1, nodes[i + 1] AS n2
    MERGE (n1)-[:COUNTRY_{cleaned_country}]->(n2)
    WITH nodes
    WITH nodes[size(nodes)-1] AS last, nodes[0] AS first
    MERGE (last)-[:COUNTRY_{cleaned_country}]->(first)
    RETURN count(*)
    """
    tx.run(query)


def main():
    countries = fetch_countries_from_api()
    if not countries:
        return

    print(f"Fetched countries: {countries}")

    with driver.session() as session:
        print("Veritabanı bağlantısı başarıyla kuruldu.")
        for country in countries:
            cleaned_country = clean_string(country)
            session.execute_write(create_country_relationships, country, cleaned_country)
            print(f"İlişkiler oluşturuldu: {country} - {cleaned_country}")

    print("İlişkiler başarıyla oluşturuldu.")


if __name__ == "__main__":
    main()
