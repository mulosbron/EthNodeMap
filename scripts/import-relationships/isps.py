from neo4j import GraphDatabase
import requests

uri = "bolt://localhost:7687"
username = "neo4j"
password = "1597536842"

driver = GraphDatabase.driver(uri, auth=(username, password))


def fetch_isps_from_api():
    api_url = "http://127.0.0.1:5001/get_isps"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        isps = response.json()
        return [isp for isp in isps if isp]
    except requests.exceptions.RequestException as e:
        print(f"API'den veri çekilemedi: {e}")
        return []


def classify_isp(isp):
    isp_lower = isp.lower()
    if "contabo" in isp_lower:
        return "CONTABO"
    elif "amazon" in isp_lower:
        return "AWS"
    elif "aws" in isp_lower:
        return "AWS"
    elif "microsoft" in isp_lower:
        return "AZURE"
    elif "azure" in isp_lower:
        return "AZURE"
    elif "google" in isp_lower:
        return "GOOGLE"
    elif "alibaba" in isp_lower:
        return "ALIBABA"
    elif "oracle" in isp_lower:
        return "ORACLE"
    elif "ibm" in isp_lower:
        return "IBM"
    elif "tencent" in isp_lower:
        return "TENCENT"
    elif "ovh" in isp_lower:
        return "OVHCLOUD"
    elif "digitalocean" in isp_lower:
        return "DO"
    elif "linode" in isp_lower:
        return "LINODE"
    elif "akamai" in isp_lower:
        return "LINODE"
    elif "salesforce" in isp_lower:
        return "SALESFORCE"
    elif "huawei" in isp_lower and "cloud" in isp_lower:
        return "HUAWEI"
    elif "dell" in isp_lower and "cloud" in isp_lower:
        return "DELL"
    elif "vultr" in isp_lower:
        return "VULTR"
    elif "heroku" in isp_lower:
        return "HEROKU"
    elif "hetzner" in isp_lower:
        return "HETZNER"
    elif "scaleway" in isp_lower:
        return "SCALEWAY"
    elif "upcloud" in isp_lower:
        return "UPCLOUD"
    elif "kamatera" in isp_lower:
        return "KAMATERA"
    else:
        return "OTHERS"


def create_isps_relationships(tx, isp):
    escaped_isp = isp.replace("'", "\\'")
    isp_type = classify_isp(escaped_isp.lower())
    query = f"""
    MATCH (n:Node {{isp: '{escaped_isp}'}})
    WITH n
    ORDER BY id(n)
    WITH collect(n) AS nodes
    UNWIND range(0, size(nodes) - 2) AS i
    WITH nodes, nodes[i] AS n1, nodes[i + 1] AS n2
    MERGE (n1)-[:{isp_type}]->(n2)
    WITH nodes
    WITH nodes[size(nodes)-1] AS last, nodes[0] AS first
    MERGE (last)-[:{isp_type}]->(first)
    RETURN count(*)
    """
    tx.run(query)


def main():
    isps = fetch_isps_from_api()
    if not isps:
        return

    print(f"Fetched ISPs: {isps}")

    with driver.session() as session:
        print("Veritabanı bağlantısı başarıyla kuruldu.")
        for isp in isps:
            session.execute_write(create_isps_relationships, isp)
            print(f"İlişkiler oluşturuldu: {isp} - {classify_isp(isp.lower())}")

    print("İlişkiler başarıyla oluşturuldu.")


if __name__ == "__main__":
    main()
