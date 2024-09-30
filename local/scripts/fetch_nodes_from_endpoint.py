import os
import asyncio
import socket
from concurrent.futures import ThreadPoolExecutor
import requests
from neo4j import GraphDatabase
from datetime import datetime
from dotenv import load_dotenv
import random
import time

load_dotenv()

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
API_KEY = os.getenv('API_KEY')
USER_AGENT = os.getenv('USER_AGENT')
NODES_URL_BASE = os.getenv('NODES_URL')

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, API_KEY, USER_AGENT, NODES_URL_BASE]):
    raise EnvironmentError("Required .env file values are missing! Please check the .env file.")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def generate_dynamic_nodes_url(base_url):
    random_column = random.randint(0, 8)
    random_dir = random.choice(['asc', 'desc'])
    start = random.randint(0, 5000)
    length = 50
    timestamp = int(datetime.now().timestamp())
    dynamic_url = (
        f"{base_url}&order%5B0%5D%5Bcolumn%5D={random_column}"
        f"&order%5B0%5D%5Bdir%5D={random_dir}"
        f"&start={start}&length={length}"
        f"&search%5Bvalue%5D=&search%5Bregex%5D=false"
        f"&_={timestamp}"
    )
    return dynamic_url


def get_node_count():
    with driver.session() as session:
        result = session.run("MATCH (n:Node) RETURN COUNT(n) AS count")
        return result.single()["count"]


def check_port(host, port, timeout=3):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, int(port)))
            return result == 0
    except socket.error as e:
        print(f"Socket error for {host}:{port} - {e}")
        return False


def node_exists(tx, node_id):
    query = "MATCH (n:Node {id: $node_id}) RETURN n"
    result = tx.run(query, node_id=node_id)
    return result.single() is not None


def add_node(tx, node_id, host, port, client, os, status, latitude=None, longitude=None, isp=None, country_name=None):
    query = (
        "CREATE (n:Node {id: $node_id, host: $host, port: $port, client: $client, os: $os, status: $status, "
        "latitude: $latitude, longitude: $longitude, isp: $isp, country_name: $country_name, created_at: $created_at})"
    )
    created_at = datetime.now().isoformat()
    tx.run(query, node_id=node_id, host=host, port=port, client=client, os=os, status=status,
           latitude=latitude, longitude=longitude, isp=isp, country_name=country_name, created_at=created_at)


def update_node_status(tx, node_id, status):
    query = "MATCH (n:Node {id: $node_id}) SET n.status = $status, n.updated_at = $updated_at"
    updated_at = datetime.now().isoformat()
    tx.run(query, node_id=node_id, status=status, updated_at=updated_at)


def fetch_geo_info(ip):
    url = f"https://api.ipgeolocation.io/ipgeo?apiKey={API_KEY}&ip={ip}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            geo_info = {
                "latitude": data.get("latitude", ""),
                "longitude": data.get("longitude", ""),
                "isp": data.get("isp", ""),
                "country_name": data.get("country_name", "")
            }
            print(f"Geolocation information retrieved for {ip}: {geo_info}")
            return geo_info
        else:
            raise ValueError(f"Invalid API response, status code: {response.status_code}")
    except Exception as e:
        print(f"Error retrieving geolocation information for {ip}: {e}")
        return None


def check_and_update(node):
    node_id = node['id']
    host = node['host']
    port = node['port']
    client = node['client']
    os = node['os']
    status = 0 if check_port(host, port) else 1
    geo_info = fetch_geo_info(host) if status == 0 else None
    if status == 0 and geo_info:
        if all([geo_info.get("latitude"), geo_info.get("longitude"), geo_info.get("isp"), geo_info.get("country_name")]):
            with driver.session() as session:
                if not session.execute_read(node_exists, node_id):
                    session.execute_write(add_node, node_id, host, port, client, os, status,
                                          geo_info['latitude'], geo_info['longitude'],
                                          geo_info['isp'], geo_info['country_name'])
                    print(f"Node {node_id} at {host}:{port} has been added.")
                else:
                    session.execute_write(update_node_status, node_id, status)
                    print(f"Node {node_id} at {host}:{port} has been updated.")
        else:
            print(f"Node {node_id} at {host}:{port} skipped due to missing geo information.")
    else:
        print(f"Node {node_id} at {host}:{port} has status {status} and was not processed for geo information.")


async def fetch_and_process_nodes(executor, max_retries=5):
    retries = 0
    while retries < max_retries:
        dynamic_url = generate_dynamic_nodes_url(NODES_URL_BASE)
        print(f"Generated dynamic URL: {dynamic_url}")
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.get(dynamic_url, headers=headers)
        print("API Response Status:", response.status_code)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if len(data) > 0:
                print(f"{len(data)} nodes found.")
                loop = asyncio.get_running_loop()
                tasks = []
                for node in data:
                    task = loop.run_in_executor(executor, check_and_update, node)
                    tasks.append(task)

                await asyncio.gather(*tasks)
                break
            else:
                print(f"Zero nodes found. Retrying with a new URL.")
        else:
            print(f"Failed to retrieve data from API. Response: {response.text}")
        retries += 1
        print(f"Attempt {retries}/{max_retries} failed. Retrying...")
        time.sleep(2)
    if retries == max_retries:
        print(f"Reached maximum number of retries. Operation failed.")


async def main():
    executor = ThreadPoolExecutor()
    await fetch_and_process_nodes(executor)


if __name__ == "__main__":
    asyncio.run(main())
    driver.close()
