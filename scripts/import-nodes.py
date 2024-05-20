from neo4j import GraphDatabase
import pandas as pd

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "1597536842"))


def add_node(tx, node_id, host, port, client, os):
    query = (
        "CREATE (n:Node {id: $node_id, host: $host, port: $port, "
        "client: $client, os: $os})"
    )
    tx.run(query, node_id=node_id, host=host, port=port, client=client, os=os)


def delete_duplicate_nodes(tx):
    tx.run("""
        MATCH (n)
        WITH n.id AS id, COLLECT(n) AS nodes, COUNT(n) AS count
        WHERE count > 1
        CALL {
            WITH nodes
            UNWIND nodes AS node
            RETURN node
            ORDER BY node.id DESC
            LIMIT 1
        }
        FOREACH (node in tail(nodes) | DELETE node)
    """)


def load_data(file_path):
    with driver.session() as session:
        data = pd.read_csv(file_path, on_bad_lines='skip', sep=',')
        for index, row in data.iterrows():
            session.execute_write(
                add_node,
                row['Node Id'], row['Host'], row['Port'], row['Client'], row['OS']
            )
        session.execute_write(delete_duplicate_nodes)


file_path = 'nodestrackerlist/export-nodestrackerlist10.csv'
load_data(file_path)
