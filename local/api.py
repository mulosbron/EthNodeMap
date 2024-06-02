from flask import Flask, jsonify, request
from flask_cors import CORS
from neo4j import GraphDatabase
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = '88c913c742244d049c03aa976e993704'
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1597536842"))


def get_nodes(tx):
    query = """
    MATCH (n:Node)
    RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.client AS Client, n.os AS OS, n.status AS Status, 
    n.latitude AS Latitude, n.longitude AS Longitude, n.isp AS ISP, n.country_name AS Country, n.created_at AS CreatedAt
    """
    result = tx.run(query)
    return [record.data() for record in result]


def get_os_types(tx):
    query = """
    MATCH (n:Node)
    RETURN DISTINCT n.os AS OS
    """
    result = tx.run(query)
    return [record["OS"] for record in result]


def get_clients(tx):
    query = """
    MATCH (n:Node)
    RETURN DISTINCT n.client AS Client
    """
    result = tx.run(query)
    return [record["Client"] for record in result]


def get_countries(tx):
    query = """
    MATCH (n:Node)
    RETURN DISTINCT n.country_name AS Country
    """
    result = tx.run(query)
    return [record["Country"] for record in result]


def get_isps(tx):
    query = """
    MATCH (n:Node)
    RETURN DISTINCT n.isp AS ISP
    """
    result = tx.run(query)
    return [record["ISP"] for record in result]


def get_node_ids(tx):
    query = """
    MATCH (n:Node)
    RETURN DISTINCT n.id AS NodeID
    """
    result = tx.run(query)
    return [record["NodeID"] for record in result]


def get_node_count(tx):
    query = """
    MATCH (n:Node)
    RETURN COUNT(DISTINCT n.id) AS NumberOfNodes
    """
    result = tx.run(query)
    record = result.single()
    return record["NumberOfNodes"]


def get_node_details(tx, node_id):
    query = """
    MATCH (n:Node {id: $node_id})
    RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.client AS Client, n.os AS OS, n.status AS Status, 
    n.latitude AS Latitude, n.longitude AS Longitude, n.isp AS ISP, n.country_name AS Country, n.created_at AS CreatedAt
    """
    result = tx.run(query, node_id=node_id)
    return result.single().data()


def get_latest_nodes(tx, limit):
    query = """
    MATCH (n:Node)
    RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.created_at AS CreatedAt,
           n.country_name AS Country, n.client AS Client, n.os AS OS, n.isp AS ISP
    ORDER BY n.created_at DESC
    LIMIT $limit
    """
    result = tx.run(query, limit=limit)
    nodes = []
    current_time = datetime.now()
    for record in result:
        enode = f"enode://{record['NodeId']}@{record['Host']}:{record['Port']}"
        created_at_str = record["CreatedAt"]
        if isinstance(created_at_str, str):
            created_at = datetime.fromisoformat(created_at_str)
            minutes_ago = int((current_time - created_at).total_seconds() / 60)
            node_data = {
                "Country": record["Country"],
                "Client": record["Client"],
                "OS": record["OS"],
                "ISP": record["ISP"],
                "Enode": enode,
                "MinutesAgo": minutes_ago
            }
            nodes.append(node_data)
    return nodes


def calculate_percentage(count, total):
    return (count / total) * 100 if total > 0 else 0


def get_statistics(tx, data_type):
    stats = {}

    total_nodes_query = """
    MATCH (n:Node)
    RETURN count(n) AS total_nodes
    """
    total_nodes_result = tx.run(total_nodes_query)
    total_nodes = total_nodes_result.single()["total_nodes"]

    queries = {
        "os": """
            MATCH (n:Node)
            RETURN n.os AS type, count(n) AS count
        """,
        "client": """
            MATCH (n:Node)
            RETURN n.client AS type, count(n) AS count
        """,
        "isp": """
            MATCH (n:Node)
            RETURN n.isp AS type, count(n) AS count
        """,
        "country": """
            MATCH (n:Node)
            RETURN n.country_name AS type, count(n) AS count
        """
    }

    if data_type in queries:
        query = queries[data_type]
        result = tx.run(query)
        type_counts = process_and_aggregate_data(result, data_type, total_nodes)
        stats[data_type] = type_counts
    else:
        stats["error"] = "Invalid data type requested"

    return stats


def process_and_aggregate_data(result, data_type, total_nodes):
    filtered_data = []
    categories = {
        "os": ['linux', 'windows', 'macos', 'android', 'freebsd', 'darwin'],
        "client": ['geth', 'nethermind', 'besu', 'erigon', 'reth', 'ethereumjs'],
        "isp": ['contabo', 'aws', 'azure', 'google', 'alibaba', 'oracle', 'ibm', 'tencent', 'ovh', 'digitalocean',
                'linode', 'akamai', 'salesforce', 'huawei', 'cloud', 'dell', 'cloud', 'vultr', 'heroku', 'hetzner',
                'scaleway', 'upcloud', 'kamatera']
    }

    other_label = {
        "os": "Diğer İS'ler",
        "client": "Diğer İstemciler",
        "isp": "Diğer İSS'ler",
        "country": "Diğer Ülkeler"
    }

    if data_type == "country":
        for record in result:
            filtered_data.append({
                "type": record["type"],
                "count": record["count"],
                "percentage": calculate_percentage(record["count"], total_nodes)
            })
        return filtered_data

    counts = {category: 0 for category in categories[data_type]}
    counts["other"] = 0
    percentages = {category: 0 for category in categories[data_type]}
    percentages["other"] = 0

    for record in result:
        item_type = record["type"].lower()
        matched = False
        if data_type == "client":
            matched = any(client_match(category, item_type) for category in categories[data_type])
        elif data_type == "os":
            matched = any(os_match(category, item_type) for category in categories[data_type])
        elif data_type == "isp":
            matched = any(isp_match(category, item_type) for category in categories[data_type])

        if matched:
            for category in categories[data_type]:
                if client_match(category, item_type) or os_match(category, item_type) or isp_match(category, item_type):
                    counts[category] += record["count"]
                    percentages[category] += calculate_percentage(record["count"], total_nodes)
                    break
        else:
            counts["other"] += record["count"]
            percentages["other"] += calculate_percentage(record["count"], total_nodes)

    for category in categories[data_type]:
        if counts[category] > 0:
            filtered_data.append({
                "type": category.capitalize(),
                "count": counts[category],
                "percentage": percentages[category]
            })

    if counts["other"] > 0:
        filtered_data.append({
            "type": other_label[data_type],
            "count": counts["other"],
            "percentage": percentages["other"]
        })

    return filtered_data


def client_match(clientFilterValue, markerClient):
    match clientFilterValue:
        case 'geth':
            return 'geth' in markerClient
        case 'nethermind':
            return 'nethermind' in markerClient
        case 'besu':
            return 'besu' in markerClient
        case 'erigon':
            return 'erigon' in markerClient
        case 'reth':
            return 'reth' in markerClient
        case 'ethereumjs':
            return 'ethereumjs' in markerClient
        case 'other clients':
            return all(keyword not in markerClient for keyword in
                       ['geth', 'nethermind', 'besu', 'erigon', 'reth', 'ethereumjs'])
        case _:
            return False


def os_match(osFilterValue, markerOS):
    match osFilterValue:
        case 'linux':
            return 'linux' in markerOS
        case 'windows':
            return 'windows' in markerOS
        case 'macos':
            return 'macos' in markerOS
        case 'android':
            return 'android' in markerOS
        case 'freebsd':
            return 'freebsd' in markerOS
        case 'darwin':
            return 'darwin' in markerOS
        case 'other oss':
            return all(
                keyword not in markerOS for keyword in ['linux', 'windows', 'macos', 'android', 'freebsd', 'darwin'])
        case _:
            return False


def isp_match(ispFilterValue, markerISP):
    match ispFilterValue:
        case 'contabo':
            return 'contabo' in markerISP
        case 'aws':
            return any(keyword in markerISP for keyword in ['amazon', 'aws'])
        case 'azure':
            return any(keyword in markerISP for keyword in ['microsoft', 'azure'])
        case 'google':
            return 'google' in markerISP
        case 'alibaba':
            return 'alibaba' in markerISP
        case 'oracle':
            return 'oracle' in markerISP
        case 'ibm':
            return 'ibm' in markerISP
        case 'tencent':
            return 'tencent' in markerISP
        case 'ovh':
            return 'ovh' in markerISP
        case 'digitalocean':
            return 'digitalocean' in markerISP
        case 'linode':
            return any(keyword in markerISP for keyword in ['linode', 'akamai'])
        case 'salesforce':
            return 'salesforce' in markerISP
        case 'huawei':
            return 'huawei' in markerISP and 'cloud' in markerISP
        case 'dell':
            return 'dell' in markerISP and 'cloud' in markerISP
        case 'vultr':
            return 'vultr' in markerISP
        case 'heroku':
            return 'heroku' in markerISP
        case 'hetzner':
            return 'hetzner' in markerISP
        case 'scaleway':
            return 'scaleway' in markerISP
        case 'upcloud':
            return 'upcloud' in markerISP
        case 'kamatera':
            return 'kamatera' in markerISP
        case 'other isps':
            return all(keyword not in markerISP for keyword in
                       ['contabo', 'amazon', 'aws', 'microsoft', 'azure', 'google', 'alibaba', 'oracle', 'ibm',
                        'tencent', 'ovh', 'digitalocean', 'linode', 'akamai', 'salesforce', 'huawei', 'cloud', 'dell',
                        'cloud', 'vultr', 'heroku', 'hetzner', 'scaleway', 'upcloud', 'kamatera'])
        case _:
            return False


@app.route('/nodes', methods=['GET'])
def get_nodes_endpoint():
    with driver.session() as session:
        nodes = session.execute_read(get_nodes)
    return jsonify(nodes)


@app.route('/nodes/os-types', methods=['GET'])
def get_os_types_endpoint():
    with driver.session() as session:
        os_types = session.execute_read(get_os_types)
    return jsonify(os_types)


@app.route('/nodes/client-types', methods=['GET'])
def get_client_types_endpoint():
    with driver.session() as session:
        client_types = session.execute_read(get_clients)
    return jsonify(client_types)


@app.route('/nodes/countries', methods=['GET'])
def get_countries_endpoint():
    with driver.session() as session:
        countries = session.execute_read(get_countries)
    return jsonify(countries)


@app.route('/nodes/isps', methods=['GET'])
def get_isps_endpoint():
    with driver.session() as session:
        isps = session.execute_read(get_isps)
    return jsonify(isps)


@app.route('/nodes/ids', methods=['GET'])
def get_node_ids_endpoint():
    with driver.session() as session:
        node_ids = session.execute_read(get_node_ids)
    return jsonify(node_ids)


@app.route('/nodes/count', methods=['GET'])
def get_node_count_endpoint():
    with driver.session() as session:
        node_count = session.execute_read(get_node_count)
    return jsonify({"NumberOfNodes": node_count})


@app.route('/nodes/details/<node_id>', methods=['GET'])
def get_node_details_endpoint(node_id):
    with driver.session() as session:
        node_details = session.execute_read(get_node_details, node_id)
    return jsonify(node_details)


@app.route('/nodes/latest', methods=['GET'])
def get_latest_nodes_endpoint():
    limit = request.args.get('limit', default=50, type=int)
    with driver.session() as session:
        latest_nodes = session.execute_read(get_latest_nodes, limit)
    return jsonify(latest_nodes)


@app.route('/nodes/country/<country_name>', methods=['GET'])
def get_relationships(country_name):
    with driver.session() as session:
        query = """
        MATCH (root:Root {name: 'World'})-[:HAS_COUNTRY]->(c:Country {name: $country_name})-[:HAS_ISP]->(isp:ISP)
        -[:HAS_OS]->(os:OS)-[:HAS_CLIENT]->(client:Client)-[:HAS_NODE]->(n:Node) 
        RETURN root, c, isp, os, client, n
        """
        result = session.run(query, {"country_name": country_name})
        data = [record.data() for record in result]
        return jsonify(data)


@app.route('/statistics/<data_type>', methods=['GET'])
def get_statistics_endpoint(data_type):
    with driver.session() as session:
        statistics = session.execute_read(get_statistics, data_type)
    return jsonify(statistics)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
