import asyncio
import socket
from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor

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


def update_node_status(node_id, increment):
    with driver.session() as session:
        query = """
        MATCH (n:Node {id: $node_id})
        SET n.status = coalesce(n.status, 0) + $increment
        """
        session.run(query, node_id=node_id, increment=increment)


async def check_nodes(executor):
    with driver.session() as session:
        result = session.run("MATCH (n:Node) RETURN n.id AS nodeId, n.host AS host, n.port AS port")
        nodes = [(record["nodeId"], record["host"], record["port"]) for record in result]

    loop = asyncio.get_running_loop()
    tasks = []
    for node_id, host, port in nodes:
        task = loop.run_in_executor(executor, check_and_update, node_id, host, port)
        tasks.append(task)

    await asyncio.gather(*tasks)


def check_and_update(node_id, host, port):
    if check_port(host, port):
        update_node_status(node_id, 0)
        print(f"{host}:{port} adresindeki {node_id} düğümü çevrimiçi.")
    else:
        update_node_status(node_id, 1)
        print(f"{host}:{port} adresindeki {node_id} düğümü çevrimdışı.")


def delete_offline_nodes():
    with driver.session() as session:
        session.run("MATCH (n:Node) WHERE n.status >= 100 DELETE n")


if __name__ == "__main__":
    executor = ThreadPoolExecutor()
    asyncio.run(check_nodes(executor))
    delete_offline_nodes()
