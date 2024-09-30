import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
    raise EnvironmentError("Required .env file values are missing! Please check the .env file.")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

cypher_query = """
MATCH (n:Node)
WITH n,
    COALESCE(n.country_name) AS country_name,
    CASE
        WHEN toLower(n.isp) CONTAINS 'contabo' THEN 'Contabo'
        WHEN toLower(n.isp) CONTAINS 'aws' OR toLower(n.isp) CONTAINS 'amazon' THEN 'AWS'
        WHEN toLower(n.isp) CONTAINS 'azure' OR toLower(n.isp) CONTAINS 'microsoft' THEN 'Azure'
        WHEN toLower(n.isp) CONTAINS 'google' THEN 'Google'
        WHEN toLower(n.isp) CONTAINS 'alibaba' THEN 'Alibaba'
        WHEN toLower(n.isp) CONTAINS 'oracle' THEN 'Oracle'
        WHEN toLower(n.isp) CONTAINS 'ibm' THEN 'IBM'
        WHEN toLower(n.isp) CONTAINS 'tencent' THEN 'Tencent'
        WHEN toLower(n.isp) CONTAINS 'ovh' THEN 'OVHCloud'
        WHEN toLower(n.isp) CONTAINS 'digitalocean' THEN 'DigitalOcean'
        WHEN toLower(n.isp) CONTAINS 'linode' OR toLower(n.isp) CONTAINS 'akamai' THEN 'Linode'
        WHEN toLower(n.isp) CONTAINS 'akamai' THEN 'Linode'
        WHEN toLower(n.isp) CONTAINS 'salesforce' THEN 'Salesforce'
        WHEN toLower(n.isp) CONTAINS 'huawei' AND toLower(n.isp) CONTAINS 'cloud' THEN 'Huawei'
        WHEN toLower(n.isp) CONTAINS 'dell' AND toLower(n.isp) CONTAINS 'cloud' THEN 'Dell'
        WHEN toLower(n.isp) CONTAINS 'vultr' THEN 'Vultr'
        WHEN toLower(n.isp) CONTAINS 'heroku' THEN 'Heroku'
        WHEN toLower(n.isp) CONTAINS 'hetzner' THEN 'Hetzner'
        WHEN toLower(n.isp) CONTAINS 'scaleway' THEN 'Scaleway'
        WHEN toLower(n.isp) CONTAINS 'upcloud' THEN 'Upcloud'
        WHEN toLower(n.isp) CONTAINS 'kamatera' THEN 'Kamatera'
        ELSE "Other ISPs"
    END AS isp_name,
    CASE
        WHEN toLower(n.os) CONTAINS 'linux' THEN 'Linux'
        WHEN toLower(n.os) CONTAINS 'windows' THEN 'Windows'
        WHEN toLower(n.os) CONTAINS 'macos' THEN 'MacOS'
        ELSE "Other OSs"
    END AS os_name,
    CASE
        WHEN toLower(n.client) CONTAINS 'geth' THEN 'Geth'
        WHEN toLower(n.client) CONTAINS 'nethermind' THEN 'Nethermind'
        WHEN toLower(n.client) CONTAINS 'besu' THEN 'Besu'
        WHEN toLower(n.client) CONTAINS 'erigon' THEN 'Erigon'
        WHEN toLower(n.client) CONTAINS 'reth' THEN 'Reth'
        WHEN toLower(n.client) CONTAINS 'ethereumjs' THEN 'EthereumJS'
        ELSE 'Other Clients'
    END AS client_name
MATCH (root:Root {name: 'World'})
MERGE (country:Country {name: country_name})<-[:HAS_COUNTRY]-(root)
MERGE (country)-[:HAS_ISP]->(isp:ISP {name: isp_name})
MERGE (isp)-[:HAS_OS]->(os:OS {name: os_name})
MERGE (os)-[:HAS_CLIENT]->(client:Client {name: client_name})
MERGE (client)-[:HAS_NODE]->(n)
"""


def execute_relationship_query(driver, query):
    with driver.session() as session:
        session.run(query)
    print("Relationships created successfully.")


execute_relationship_query(driver, cypher_query)

driver.close()
