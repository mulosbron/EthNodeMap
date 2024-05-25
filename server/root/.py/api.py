from flask import Flask, jsonify, request
from flask_cors import CORS
from neo4j import GraphDatabase

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


def get_relationships(tx):
    query = """
    MATCH (n:Node)-[r]->(m:Node)
    RETURN n.id AS StartNodeId, type(r) AS RelationshipType, m.id AS EndNodeId
    """
    result = tx.run(query)
    return [record.data() for record in result]


def get_node_count(tx):
    query = """
    MATCH (n:Node)
    RETURN COUNT(DISTINCT n.id) AS NumberOfNodes
    """
    result = tx.run(query)
    record = result.single()
    return record["NumberOfNodes"]


def get_all_relationship_types(tx):
    query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
    result = tx.run(query)
    return [record["relationshipType"] for record in result]


def filter_relationship_types_by_prefix(types, prefix):
    return [rtype for rtype in types if rtype.startswith(prefix)]


def get_node_details(tx, node_id):
    query = """
    MATCH (n:Node {id: $node_id})
    RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.client AS Client, n.os AS OS, n.status AS Status, 
    n.latitude AS Latitude, n.longitude AS Longitude, n.isp AS ISP, n.country_name AS Country, n.created_at AS CreatedAt
    """
    result = tx.run(query, node_id=node_id)
    return result.single().data()


def count_relationships(tx, relationship_prefix):
    query = f"""
    MATCH ()-[r]->()
    WHERE type(r) STARTS WITH $prefix
    RETURN type(r) AS RelationshipType, COUNT(r) AS Count
    """
    result = tx.run(query, prefix=relationship_prefix)
    return {record["RelationshipType"]: record["Count"] for record in result}


def get_percentage_distribution(tx, relationship_prefix):
    relationships = count_relationships(tx, relationship_prefix)
    total_count = sum(relationships.values())
    if total_count == 0:
        return {k: 0 for k in relationships.keys()}
    return {k: (v / total_count) * 100 for k, v in relationships.items()}


def get_latest_nodes(tx, limit):
    query = """
    MATCH (n:Node)
    RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.created_at AS CreatedAt,
           n.country_name AS Country, n.client AS Client, n.os AS OS
    ORDER BY n.created_at DESC
    LIMIT $limit
    """
    result = tx.run(query, limit=limit)
    nodes = []
    for record in result:
        enode = f"enode://{record['NodeId']}@{record['Host']}:{record['Port']}"
        node_data = {
            "Country": record["Country"],
            "Client": record["Client"],
            "OS": record["OS"],
            "Enode": enode,
            "CreatedAt": record["CreatedAt"]
        }
        nodes.append(node_data)
    return nodes


@app.route('/get-nodes', methods=['GET'])
def get_nodes_endpoint():
    with driver.session() as session:
        nodes = session.execute_read(get_nodes)
    return jsonify(nodes)


@app.route('/get-os-types', methods=['GET'])
def get_os_types_endpoint():
    with driver.session() as session:
        os_types = session.execute_read(get_os_types)
    return jsonify(os_types)


@app.route('/get-client-types', methods=['GET'])
def get_client_types_endpoint():
    with driver.session() as session:
        client_types = session.execute_read(get_clients)
    return jsonify(client_types)


@app.route('/get-countries', methods=['GET'])
def get_countries_endpoint():
    with driver.session() as session:
        countries = session.execute_read(get_countries)
    return jsonify(countries)


@app.route('/get-isps', methods=['GET'])
def get_isps_endpoint():
    with driver.session() as session:
        isps = session.execute_read(get_isps)
    return jsonify(isps)


@app.route('/get-node-ids', methods=['GET'])
def get_node_ids_endpoint():
    with driver.session() as session:
        node_ids = session.execute_read(get_node_ids)
    return jsonify(node_ids)


@app.route('/get-relationships', methods=['GET'])
def get_relationships_endpoint():
    with driver.session() as session:
        relationships = session.execute_read(get_relationships)
    return jsonify(relationships)


@app.route('/get-node-count', methods=['GET'])
def get_node_count_endpoint():
    with driver.session() as session:
        node_count = session.execute_read(get_node_count)
    return jsonify({"NumberOfNodes": node_count})


@app.route('/get-relationship-types', methods=['GET'])
def get_all_relationship_types_endpoint():
    with driver.session() as session:
        relationship_types = session.read_transaction(get_all_relationship_types)
    return jsonify(relationship_types)


@app.route('/get-relationship-types/clients', methods=['GET'])
def get_clients_relationship_types_endpoint():
    with driver.session() as session:
        relationship_types = session.read_transaction(get_all_relationship_types)
    filtered_relationship_types = filter_relationship_types_by_prefix(relationship_types, "CLIENT_")
    return jsonify(filtered_relationship_types)


@app.route('/get-relationship-types/countries', methods=['GET'])
def get_countries_relationship_types_endpoint():
    with driver.session() as session:
        relationship_types = session.read_transaction(get_all_relationship_types)
    filtered_relationship_types = filter_relationship_types_by_prefix(relationship_types, "COUNTRY_")
    return jsonify(filtered_relationship_types)


@app.route('/get-relationship-types/os-types', methods=['GET'])
def get_os_types_relationship_types_endpoint():
    with driver.session() as session:
        relationship_types = session.read_transaction(get_all_relationship_types)
    filtered_relationship_types = filter_relationship_types_by_prefix(relationship_types, "OS_")
    return jsonify(filtered_relationship_types)


@app.route('/get-relationship-types/isps', methods=['GET'])
def get_isps_relationship_types_endpoint():
    with driver.session() as session:
        relationship_types = session.read_transaction(get_all_relationship_types)
    filtered_relationship_types = filter_relationship_types_by_prefix(relationship_types, "ISP_")
    return jsonify(filtered_relationship_types)


@app.route('/get-node-details/<node_id>', methods=['GET'])
def get_node_details_endpoint(node_id):
    with driver.session() as session:
        node_details = session.execute_read(get_node_details, node_id)
    return jsonify(node_details)


@app.route('/get-relationship-percentage/<relationship_prefix>', methods=['GET'])
def get_relationship_percentage_endpoint(relationship_prefix):
    with driver.session() as session:
        percentage_distribution = session.read_transaction(get_percentage_distribution, relationship_prefix)
    return jsonify(percentage_distribution)


@app.route('/get-latest-nodes', methods=['GET'])
def get_latest_nodes_endpoint():
    limit = request.args.get('limit', default=50, type=int)
    with driver.session() as session:
        latest_nodes = session.execute_read(get_latest_nodes, limit)
    return jsonify(latest_nodes)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
