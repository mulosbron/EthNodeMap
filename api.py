from flask import Flask, jsonify, request
from flask_cors import CORS
from neo4j import GraphDatabase
import requests
import csv
import os

app = Flask(__name__)
CORS(app)

API_KEY = '88c913c742244d049c03aa976e993704'
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1597536842"))


def get_ethereum_nodes(tx):
    query = """
    MATCH (n:Node) 
    RETURN n.id AS NodeId, n.host AS Host, n.port AS Port, n.country AS Country, 
           n.client AS Client, n.type AS Type, n.os AS OS
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


@app.route('/get_nodes', methods=['GET'])
def get_nodes():
    with driver.session() as session:
        nodes = session.execute_read(get_ethereum_nodes)
    return jsonify(nodes)


@app.route('/get_os_types', methods=['GET'])
def get_os_types_endpoint():
    with driver.session() as session:
        os_types = session.execute_read(get_os_types)
    return jsonify(os_types)


@app.route('/get_client_types', methods=['GET'])
def get_client_types_endpoint():
    with driver.session() as session:
        client_types = session.execute_read(get_clients)
    return jsonify(client_types)


@app.route('/get_countries', methods=['GET'])
def get_countries_endpoint():
    with driver.session() as session:
        countries = session.execute_read(get_countries)
    return jsonify(countries)


@app.route('/get_isps', methods=['GET'])
def get_isps_endpoint():
    with driver.session() as session:
        isps = session.execute_read(get_isps)
    return jsonify(isps)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
