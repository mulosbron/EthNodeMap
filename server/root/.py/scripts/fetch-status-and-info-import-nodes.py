import asyncio
import socket
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import schedule
import time
import asyncio
from neo4j import GraphDatabase

# Define the headers and URL for web scraping
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, Gecko) "
                  "Chrome/118.0.0.0 Safari/537.36"
}
URL = "https://etherscan.io/nodetracker/nodes"
API_KEY = "88c913c742244d049c03aa976e993704"

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "1597536842"))


def check_port(host, port, timeout=3):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, int(port)))
            return result == 0
    except socket.error as e:
        print(f"{host}:{port} için soket hatası - {e}")
        return False


def add_node(tx, node_id, host, port, client, os, status, latitude=None, longitude=None, isp=None, country_name=None):
    query = (
        "CREATE (n:Node {id: $node_id, host: $host, port: $port, "
        "client: $client, os: $os, status: $status, latitude: $latitude, "
        "longitude: $longitude, isp: $isp, country_name: $country_name})"
    )
    tx.run(query, node_id=node_id, host=host, port=port, client=client, os=os, status=status,
           latitude=latitude, longitude=longitude, isp=isp, country_name=country_name)


def update_node_status(tx, node_id, status):
    query = (
        "MATCH (n:Node {id: $node_id}) "
        "SET n.status = $status"
    )
    tx.run(query, node_id=node_id, status=status)


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
            print(f"{ip} için coğrafi bilgi alındı: {geo_info}")
            return geo_info
        else:
            raise ValueError(f"API yanıtı uygun değil, durum kodu: {response.status_code}")
    except Exception as e:
        print(f"{ip} için coğrafi bilgi alınırken hata oluştu: {e}")
        return None


def check_and_update(node):
    node_id, host, port, client, os = node.values()
    status = 0 if check_port(host, port) else 1
    geo_info = fetch_geo_info(host) if status == 0 else None

    with driver.session() as session:
        if not session.read_transaction(node_exists, node_id):
            session.write_transaction(add_node, node_id, host, port, client, os, status,
                                      geo_info['latitude'] if geo_info else None,
                                      geo_info['longitude'] if geo_info else None,
                                      geo_info['isp'] if geo_info else None,
                                      geo_info['country_name'] if geo_info else None)
            print(f"{host}:{port} adresindeki {node_id} düğümü eklendi.")
        else:
            session.write_transaction(update_node_status, node_id, status)
            print(f"{host}:{port} adresindeki {node_id} düğümü güncellendi.")


def node_exists(tx, node_id):
    query = "MATCH (n:Node {id: $node_id}) RETURN n"
    result = tx.run(query, node_id=node_id)
    return result.single() is not None


async def scrape_and_check_nodes(executor):
    response = requests.get(URL, headers=HEADERS)
    print("Sayfa durumu:", response.status_code)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print("Sayfa içeriği başarıyla alındı.")

        nodes = []

        rows = soup.select('tbody.align-middle.text-nowrap tr')
        print(f"{len(rows)} satır bulundu.")

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 7:
                node_id = cols[0].text.strip()
                host = cols[2].text.strip()
                port = cols[3].text.strip()
                client = cols[5].text.strip()
                os = cols[7].text.strip()
                nodes.append({
                    'node_id': node_id,
                    'host': host,
                    'port': port,
                    'client': client,
                    'os': os
                })
                print(f"Node ID: {node_id}, Host: {host}, Port: {port}, Client: {client}, OS: {os}")

        loop = asyncio.get_running_loop()
        tasks = []
        for node in nodes:
            task = loop.run_in_executor(executor, check_and_update, node)
            tasks.append(task)

        await asyncio.gather(*tasks)


def job():
    executor = ThreadPoolExecutor()
    asyncio.run(scrape_and_check_nodes(executor))


schedule.every(24).minutes.do(job)


if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(5)

