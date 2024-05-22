import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
api_key = "88c913c742244d049c03aa976e993704"
driver = GraphDatabase.driver(uri, auth=("neo4j", "1597536842"))


def fetch_nodes_without_geo_info(tx):
    query = """
    MATCH (n:Node)
    WHERE n.latitude IS NULL OR n.longitude IS NULL
    RETURN DISTINCT n.id AS nodeId, n.host AS host
    """
    result = tx.run(query)
    return [(record["nodeId"], record["host"]) for record in result]


def fetch_geo_info(ip):
    url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={ip}"
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


def update_node_properties(tx, node_id, properties):
    query = "MATCH (n:Node {id: $node_id}) SET n += $properties"
    print(f"{node_id} düğümü güncelleniyor, özellikler: {properties}")
    tx.run(query, node_id=node_id, properties=properties)


def main():
    with driver.session() as session:
        nodes = session.execute_read(fetch_nodes_without_geo_info)
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ip = {executor.submit(fetch_geo_info, host): (node_id, host) for node_id, host in nodes}
            for future in as_completed(future_to_ip):
                node_id, host = future_to_ip[future]
                geo_info = future.result()
                if geo_info:
                    session.execute_write(update_node_properties, node_id, geo_info)
                else:
                    print(f"{host} için coğrafi bilgi yok, {node_id} düğümü güncellenemedi")

    print("Coğrafi bilgi güncelleme süreci tamamlandı.")


if __name__ == "__main__":
    main()
