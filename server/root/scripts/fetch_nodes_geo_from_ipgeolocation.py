import os
import requests
from neo4j import GraphDatabase
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
API_KEY = os.getenv('API_KEY')

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, API_KEY]):
    raise EnvironmentError("Required .env file values are missing! Please check the .env file.")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def get_nodes_with_null_latitude():
    with driver.session() as session:
        result = session.run("""
            MATCH (n:Node)
            WHERE n.latitude IS NULL
            RETURN n.id AS id, n.host AS host
        """)
        nodes = [{"id": record["id"], "host": record["host"]} for record in result]
        return nodes


def fetch_geo_info(ip):
    url = f"https://api.ipgeolocation.io/ipgeo?apiKey={API_KEY}&ip={ip}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            geo_info = {
                "latitude": data.get("latitude", None),
                "longitude": data.get("longitude", None),
                "isp": data.get("isp", None),
                "country_name": data.get("country_name", None)
            }
            print(f"Geographic information retrieved for {ip}: {geo_info}")
            return geo_info
        else:
            print(f"API response is not valid, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while retrieving geographic information for {ip}: {e}")
        return None


def update_node_with_geo_info(node_id, geo_info):
    with driver.session() as session:
        session.run("""
            MATCH (n:Node {id: $node_id})
            SET n.latitude = $latitude,
                n.longitude = $longitude,
                n.isp = $isp,
                n.country_name = $country_name,
                n.updated_at = $updated_at
        """,
                    node_id=node_id,
                    latitude=geo_info['latitude'],
                    longitude=geo_info['longitude'],
                    isp=geo_info['isp'],
                    country_name=geo_info['country_name'],
                    updated_at=datetime.now().isoformat())
        print(f"Node {node_id} has been updated.")


def main():
    nodes = get_nodes_with_null_latitude()
    if nodes:
        print(f"{len(nodes)} nodes found.")
        for node in nodes:
            geo_info = fetch_geo_info(node['host'])
            if geo_info:
                update_node_with_geo_info(node['id'], geo_info)
    else:
        print("No nodes found with null latitude.")


if __name__ == "__main__":
    main()
    driver.close()
