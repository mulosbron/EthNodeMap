import pytest
import sys
import os
import asyncio
from quart import Quart, g, jsonify
from unittest.mock import AsyncMock, patch, ANY
from datetime import datetime, timedelta
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase, AsyncSession

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from routes.node_routes import NodeRoutes
from utils.node_helper import NodeHelper
from services.node_service import NodeService
from db.neo4j_manager import AsyncSessionManager


@pytest.fixture
def mock_env_vars_different_host_port(monkeypatch):
    monkeypatch.setenv('APP_HOST', '192.168.0.10')
    monkeypatch.setenv('APP_PORT', '8080')
    monkeypatch.setenv('NEO4J_URI', 'bolt://localhost:7687')


@pytest.fixture
def mock_env_vars_default(monkeypatch):
    monkeypatch.delenv('APP_HOST', raising=False)
    monkeypatch.delenv('APP_PORT', raising=False)
    monkeypatch.setenv('NEO4J_URI', 'bolt://localhost:7687')


@pytest.fixture
def mock_env_vars_invalid_port(monkeypatch):
    monkeypatch.setenv('APP_PORT', '70000')
    monkeypatch.setenv('APP_HOST', '127.0.0.1')
    monkeypatch.setenv('NEO4J_URI', 'bolt://localhost:7687')


@pytest.fixture
def mock_async_session_manager():
    with patch('db.neo4j_manager.AsyncSessionManager') as mock_manager:
        instance = mock_manager.return_value
        instance.close_session = AsyncMock()
        yield mock_manager


@pytest.fixture
def app():
    app = Quart(__name__)
    node_routes = NodeRoutes()
    app.register_blueprint(node_routes.get_blueprint())
    return app


""" NEO4J """


# 1. AsyncSessionManager Singleton pattern test
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncGraphDatabase.driver')
async def test_singleton_pattern(mock_driver, mock_env_vars_default):
    instance1 = AsyncSessionManager()
    instance2 = AsyncSessionManager()
    assert instance1 is instance2, "AsyncSessionManager is not following Singleton pattern."


# 2. Get session returns existing session test
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncGraphDatabase.driver')
async def test_get_session_returns_existing_session(mock_driver, mock_env_vars_default, app):
    mock_session = AsyncMock(spec=AsyncSession)
    async with app.app_context():
        g.neo4j_session = mock_session
        manager = AsyncSessionManager()
        session = await manager.get_session()
    assert session == mock_session, "Existing session was not returned."


# 3. Test for Neo4j query timeout
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_nodes', new_callable=AsyncMock)
async def test_neo4j_query_timeout(mock_get_nodes, app):
    mock_get_nodes.side_effect = asyncio.TimeoutError("Database query timed out.")
    client = app.test_client()
    response = await client.get('/nodes')
    assert response.status_code == 504
    data = await response.get_json()
    assert "error" in data
    assert data["error"] == "Database query timed out."


# 4. Test for Neo4j connection error
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.get_session', new_callable=AsyncMock)
async def test_neo4j_connection_error(mock_get_session, app):
    mock_get_session.side_effect = RuntimeError("Neo4j connection error!")
    client = app.test_client()
    response = await client.get('/nodes')
    assert response.status_code == 500
    data = await response.get_json()
    assert "error" in data
    assert data["error"] == 'Error fetching nodes: 500 Internal Server Error: Database query execution failed.'


# 5. Test for execute_query throwing runtime error on failure
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.get_session', new_callable=AsyncMock)
async def test_async_session_manager_execute_query_failure(mock_get_session):
    mock_session = AsyncMock()
    mock_get_session.return_value = mock_session
    mock_session.run.side_effect = Exception("Query failed!")
    manager = AsyncSessionManager()
    with pytest.raises(RuntimeError, match="An error occurred while processing the query."):
        await manager.execute_query("MATCH (n) RETURN n")


# 6. Test for AsyncSessionManager.close_session method with valid session
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.get_session', new_callable=AsyncMock)
async def test_close_session_with_valid_session(mock_get_session, app):
    mock_session = AsyncMock()
    mock_get_session.return_value = mock_session
    async with app.app_context():
        g.neo4j_session = mock_session
        manager = AsyncSessionManager()
        await manager.close_session()
    mock_session.close.assert_called_once(), "Session close was not called."


# 7. Test for AsyncSessionManager.close_session method without session
@pytest.mark.asyncio
async def test_close_session_without_session(app):
    async with app.app_context():
        manager = AsyncSessionManager()
        assert 'neo4j_session' not in g, "There should be no session before closing."
        await manager.close_session()
        assert 'neo4j_session' not in g, "There should be no session to close."


""" ROUTES """


# 1. /nodes endpoint test
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_nodes', new_callable=AsyncMock)
async def test_fetch_nodes_endpoint(mock_get_nodes, app):
    mock_get_nodes.return_value = [{"node_id": "2845fa1ef7ca2660962c9fe4beb1688067d74141661858b3374c313a5110ebdb"}]
    client = app.test_client()
    response = await client.get('/nodes')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0


# 2. /nodes/operating-systems endpoint test
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_os_types', new_callable=AsyncMock)
async def test_fetch_os_types_endpoint(mock_get_os_types, app):
    mock_get_os_types.return_value = ["Linux"]
    client = app.test_client()
    response = await client.get('/nodes/operating-systems')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, list)


# 3. /nodes/clients endpoint test
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_clients', new_callable=AsyncMock)
async def test_fetch_clients_endpoint(mock_get_clients, app):
    mock_get_clients.return_value = ["Geth"]
    client = app.test_client()
    response = await client.get('/nodes/clients')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, list)


# 4. /nodes/countries endpoint test
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_countries', new_callable=AsyncMock)
async def test_fetch_countries_endpoint(mock_get_countries, app):
    mock_get_countries.return_value = ["USA"]
    client = app.test_client()
    response = await client.get('/nodes/countries')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, list)


# 5. /nodes/isps endpoint test
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_isps', new_callable=AsyncMock)
async def test_fetch_isps_endpoint(mock_get_isps, app):
    mock_get_isps.return_value = ["AWS"]
    client = app.test_client()
    response = await client.get('/nodes/isps')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, list)


# 6. /nodes/details/<node_id> endpoint test
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_node_details', new_callable=AsyncMock)
async def test_fetch_node_details_endpoint_valid(mock_get_node_details, app):
    mock_get_node_details.return_value = {
        "node_id": "2845fa1ef7ca2660962c9fe4beb1688067d74141661858b3374c313a5110ebdb"
    }
    client = app.test_client()
    valid_node_id = "2845fa1ef7ca2660962c9fe4beb1688067d74141661858b3374c313a5110ebdb"
    response = await client.get(f'/nodes/details/{valid_node_id}')
    assert response.status_code == 200
    data = await response.get_json()
    assert "node_id" in data


# 7. Invalid node_id test
@pytest.mark.asyncio
async def test_fetch_node_details_endpoint_invalid(app):
    client = app.test_client()
    invalid_node_id = "invalid123"
    response = await client.get(f'/nodes/details/{invalid_node_id}')
    assert response.status_code == 400


# 8. /nodes/count endpoint test
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_node_count', new_callable=AsyncMock)
async def test_fetch_node_count_endpoint(mock_get_node_count, app):
    mock_get_node_count.return_value = 100
    client = app.test_client()
    response = await client.get('/nodes/count')
    assert response.status_code == 200
    data = await response.get_json()
    assert "NumberOfNodes" in data


# 9. /nodes/latest endpoint test
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_latest_nodes', new_callable=AsyncMock)
async def test_fetch_latest_nodes_endpoint(mock_get_latest_nodes, app):
    mock_get_latest_nodes.return_value = [
        {"node_id": "2845fa1ef7ca2660962c9fe4beb1688067d74141661858b3374c313a5110ebdb"}
    ]
    client = app.test_client()
    response = await client.get('/nodes/latest?limit=10')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, list)
    assert len(data) <= 10


# 10. /statistics/<data_type> endpoint test
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_statistics', new_callable=AsyncMock)
async def test_fetch_statistics_endpoint(mock_get_statistics, app):
    mock_get_statistics.return_value = {"os": [{"type": "Linux", "count": 50, "percentage": 50.0}]}
    client = app.test_client()
    response = await client.get('/statistics/os')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, dict)


# 11. /nodes/filter endpoint test
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_filtered_nodes', new_callable=AsyncMock)
async def test_fetch_filter_nodes(mock_get_filtered_nodes, app):
    mock_get_filtered_nodes.return_value = [
        {"node_id": "2845fa1ef7ca2660962c9fe4beb1688067d74141661858b3374c313a5110ebdb"}
    ]
    client = app.test_client()
    response = await client.get('/nodes/filter?country=USA&os=Linux&client=Geth&isp=AWS')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, list)


# 12. Test for invalid limit with latest nodes
@pytest.mark.asyncio
async def test_invalid_limit_for_latest_nodes(app):
    client = app.test_client()
    response = await client.get('/nodes/latest?limit=-10')
    assert response.status_code == 400
    data = await response.get_json()
    assert "error" in data


# 13. Test for empty results
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_filtered_nodes', new_callable=AsyncMock)
async def test_no_results_for_filter(mock_get_filtered_nodes, app):
    mock_get_filtered_nodes.return_value = []
    client = app.test_client()
    response = await client.get('/nodes/filter?country=UnknownCountry&os=UnknownOS')
    assert response.status_code == 404
    data = await response.get_json()
    assert "message" in data
    assert data["message"] == "No nodes found for the given filters"


# 14. Test for an empty database
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_nodes', new_callable=AsyncMock)
async def test_empty_database(mock_get_nodes, app):
    mock_get_nodes.return_value = []
    client = app.test_client()
    response = await client.get('/nodes')
    assert response.status_code == 200
    data = await response.get_json()
    assert data == []


@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_nodes', new_callable=AsyncMock)
async def test_concurrent_requests(mock_get_nodes, app):
    mock_get_nodes.return_value = [{"node_id": "test_node"}]
    client = app.test_client()

    async def make_request():
        return await client.get('/nodes')

    tasks = [make_request() for _ in range(10)]
    responses = await asyncio.gather(*tasks)
    for response in responses:
        assert response.status_code == 200


# 16. Test for simulating database connection failure
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_nodes', new_callable=AsyncMock)
async def test_database_connection_failure(mock_get_nodes, app):
    mock_get_nodes.side_effect = RuntimeError("Database connection failed!")
    client = app.test_client()
    response = await client.get('/nodes')
    assert response.status_code == 500
    data = await response.get_json()
    assert "error" in data


# 17. Test for get_latest_nodes with large limit
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_latest_nodes', new_callable=AsyncMock)
async def test_large_limit_for_latest_nodes(mock_get_latest_nodes, app):
    mock_get_latest_nodes.return_value = [{
        "node_id": "2845fa1ef7ca2660962c9fe4beb1688067d74141661858b3374c313a5110ebdb"}] * 100
    client = app.test_client()
    response = await client.get('/nodes/latest?limit=5000')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, list)
    assert len(data) == 100


# 18. Test for the /nodes/country/<country_name> endpoint
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_relationships', new_callable=AsyncMock)
async def test_get_country_nodes_no_data(mock_get_relationships, app):
    mock_get_relationships.return_value = []
    client = app.test_client()
    response = await client.get('/nodes/country/Finlanda')
    assert response.status_code == 404
    data = await response.get_json()
    assert "message" in data
    assert data["message"] == "No nodes found for country Finlanda"


""" CONTROLLER """


# 1. Test for /nodes route - successful response
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_nodes', new_callable=AsyncMock)
async def test_handle_get_nodes_success(mock_get_nodes, app):
    mock_get_nodes.return_value = [{"node_id": "test_node"}]
    client = app.test_client()
    response = await client.get('/nodes')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, list)
    assert data[0]["node_id"] == "test_node"


# 2. Test for /nodes route - internal server error
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_nodes', new_callable=AsyncMock)
async def test_handle_get_nodes_error(mock_get_nodes, app):
    mock_get_nodes.side_effect = Exception("Test Error")
    client = app.test_client()
    response = await client.get('/nodes')
    assert response.status_code == 500
    data = await response.get_json()
    assert data["error"] == "Error fetching nodes: Test Error"


# 3. Test for /nodes/operating-systems route - successful response
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_os_types', new_callable=AsyncMock)
async def test_handle_get_os_types_success(mock_get_os_types, app):
    mock_get_os_types.return_value = ["Linux"]
    client = app.test_client()
    response = await client.get('/nodes/operating-systems')
    assert response.status_code == 200
    data = await response.get_json()
    assert data == ["Linux"]


# 4. Test for /nodes/operating-systems route - internal server error
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_os_types', new_callable=AsyncMock)
async def test_handle_get_os_types_error(mock_get_os_types, app):
    mock_get_os_types.side_effect = Exception("Test Error")
    client = app.test_client()
    response = await client.get('/nodes/operating-systems')
    assert response.status_code == 500
    data = await response.get_json()
    assert data["error"] == "Error fetching operating systems: Test Error"


# 5. Test for /nodes/clients route - successful response
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_clients', new_callable=AsyncMock)
async def test_handle_get_clients_success(mock_get_clients, app):
    mock_get_clients.return_value = ["Geth"]
    client = app.test_client()
    response = await client.get('/nodes/clients')
    assert response.status_code == 200
    data = await response.get_json()
    assert data == ["Geth"]


# 6. Test for /nodes/clients route - internal server error
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_clients', new_callable=AsyncMock)
async def test_handle_get_clients_error(mock_get_clients, app):
    mock_get_clients.side_effect = Exception("Test Error")
    client = app.test_client()
    response = await client.get('/nodes/clients')
    assert response.status_code == 500
    data = await response.get_json()
    assert data["description"] == "Error fetching clients: Test Error"


# 7. Test for /nodes/countries route - successful response
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_countries', new_callable=AsyncMock)
async def test_handle_get_countries_success(mock_get_countries, app):
    mock_get_countries.return_value = ["USA"]
    client = app.test_client()
    response = await client.get('/nodes/countries')
    assert response.status_code == 200
    data = await response.get_json()
    assert data == ["USA"]


# 8. Test for /nodes/countries route - internal server error
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_countries', new_callable=AsyncMock)
async def test_handle_get_countries_error(mock_get_countries, app):
    mock_get_countries.side_effect = Exception("Test Error")
    client = app.test_client()
    response = await client.get('/nodes/countries')
    assert response.status_code == 500
    data = await response.get_json()
    assert data["description"] == "Error fetching countries: Test Error"


# 9. Test for /nodes/details/<node_id> route - successful response
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_node_details', new_callable=AsyncMock)
async def test_handle_get_node_details_success(mock_get_node_details, app):
    mock_get_node_details.return_value = {"node_id": "test_node"}
    client = app.test_client()
    response = await client.get('/nodes/details/test_node')
    assert response.status_code == 200
    data = await response.get_json()
    assert data["node_id"] == "test_node"


# 10. Test for /nodes/details/<node_id> route - internal server error
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_node_details', new_callable=AsyncMock)
async def test_handle_get_node_details_error(mock_get_node_details, app):
    mock_get_node_details.side_effect = Exception("Test Error")
    client = app.test_client()
    response = await client.get('/nodes/details/test_node')
    assert response.status_code == 500
    data = await response.get_json()
    assert data["description"] == "Error fetching details for node test_node: Test Error"


# 11. /nodes/country/<country_name> route - successful response
@pytest.mark.asyncio
@patch('controllers.node_controller.NodeController.get_relationships', new_callable=AsyncMock)
async def test_handle_get_relationships_success(mock_get_relationships, app):
    mock_get_relationships.return_value = [{"relationship_type": "connected", "source": "node1", "target": "node2"}]
    client = app.test_client()
    response = await client.get('/nodes/country/USA')
    assert response.status_code == 200
    data = await response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0


# 12. Test for content validation
@pytest.mark.asyncio
@patch('services.node_service.NodeService.fetch_node_details', new_callable=AsyncMock)
async def test_node_details_content_validation(mock_get_node_details, app):
    mock_get_node_details.return_value = {
        "node_id": "2845fa1ef7ca2660962c9fe4beb1688067d74141661858b3374c313a5110ebdb",
        "host": "127.0.0.1",
        "port": 30303,
        "os": "Linux"
    }
    client = app.test_client()
    valid_node_id = "2845fa1ef7ca2660962c9fe4beb1688067d74141661858b3374c313a5110ebdb"
    response = await client.get(f'/nodes/details/{valid_node_id}')
    assert response.status_code == 200
    data = await response.get_json()
    assert "node_id" in data
    assert data["host"] == "127.0.0.1"
    assert data["port"] == 30303
    assert data["os"] == "Linux"


""" SERVICE """


# 1. Test for NodeService.get_nodes - successful response
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_nodes_success(mock_execute_query):
    mock_execute_query.return_value = [{"NodeId": "test_node"}]
    node_service = NodeService()
    nodes = await node_service.fetch_nodes()
    assert len(nodes) == 1
    assert nodes[0]["NodeId"] == "test_node"


# 2. Test for NodeService.get_nodes - database error
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_nodes_error(mock_execute_query):
    mock_execute_query.side_effect = Exception("Database Error")
    node_service = NodeService()
    with pytest.raises(Exception, match="Database Error"):
        await node_service.fetch_nodes()


# 3. Test for NodeService.get_os_types - successful response
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_os_types_success(mock_execute_query):
    mock_execute_query.return_value = [{"OS": "Linux"}]
    node_service = NodeService()
    os_types = await node_service.fetch_os_types()
    assert len(os_types) == 1
    assert os_types[0] == "Linux"


# 4. Test for NodeService.get_os_types - database error
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_os_types_error(mock_execute_query):
    mock_execute_query.side_effect = Exception("Database Error")
    node_service = NodeService()
    with pytest.raises(Exception, match="Database Error"):
        await node_service.fetch_os_types()


# 5. Test for NodeService.get_clients - successful response
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_clients_success(mock_execute_query):
    mock_execute_query.return_value = [{"Client": "Geth"}]
    node_service = NodeService()
    clients = await node_service.fetch_clients()
    assert len(clients) == 1
    assert clients[0] == "Geth"


# 6. Test for NodeService.get_clients - database error
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_clients_error(mock_execute_query):
    mock_execute_query.side_effect = Exception("Database Error")
    node_service = NodeService()
    with pytest.raises(Exception, match="Database Error"):
        await node_service.fetch_clients()


# 7. Test for NodeService.get_countries - successful response
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_countries_success(mock_execute_query):
    mock_execute_query.return_value = [{"Country": "USA"}]
    node_service = NodeService()
    countries = await node_service.fetch_countries()
    assert len(countries) == 1
    assert countries[0] == "USA"


# 8. Test for NodeService.get_countries - database error
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_countries_error(mock_execute_query):
    mock_execute_query.side_effect = Exception("Database Error")
    node_service = NodeService()
    with pytest.raises(Exception, match="Database Error"):
        await node_service.fetch_countries()


# 9. Test for NodeService.get_isps - successful response
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_isps_success(mock_execute_query):
    mock_execute_query.return_value = [{"ISP": "AWS"}]
    node_service = NodeService()
    isps = await node_service.fetch_isps()
    assert len(isps) == 1
    assert isps[0] == "AWS"


# 10. Test for NodeService.get_isps - database error
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_isps_error(mock_execute_query):
    mock_execute_query.side_effect = Exception("Database Error")
    node_service = NodeService()
    with pytest.raises(Exception, match="Database Error"):
        await node_service.fetch_isps()


# 11. Test for NodeService.get_node_ids - successful response
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_node_ids_success(mock_execute_query):
    mock_execute_query.return_value = [{"NodeID": "node123"}]
    node_service = NodeService()
    node_ids = await node_service.fetch_node_ids()
    assert len(node_ids) == 1
    assert node_ids[0] == "node123"


# 12. Test for NodeService.get_node_ids - database error
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_node_ids_error(mock_execute_query):
    mock_execute_query.side_effect = Exception("Database Error")
    node_service = NodeService()
    with pytest.raises(Exception, match="Database Error"):
        await node_service.fetch_node_ids()


# 13. Test for NodeService.get_node_count - successful response
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_node_count_success(mock_execute_query):
    mock_execute_query.return_value = [{"NumberOfNodes": 100}]
    node_service = NodeService()
    node_count = await node_service.fetch_node_count()
    assert node_count == 100


# 14. Test for NodeService.get_node_count - database error
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_node_count_error(mock_execute_query):
    mock_execute_query.side_effect = Exception("Database Error")
    node_service = NodeService()
    with pytest.raises(Exception, match="Database Error"):
        await node_service.fetch_node_count()


# 15. Test for NodeService.get_node_details - successful response
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_node_details_success(mock_execute_query):
    mock_execute_query.return_value = [{
        "NodeId": "node123", "Host": "127.0.0.1", "Port": 30303, "Client": "Geth", "Country": "USA"
    }]
    node_service = NodeService()
    node_details = await node_service.fetch_node_details("node123")
    assert node_details["NodeId"] == "node123"
    assert node_details["Host"] == "127.0.0.1"
    assert node_details["Port"] == 30303
    assert node_details["Client"] == "Geth"
    assert node_details["Country"] == "USA"


# 16. Test for NodeService.get_node_details - no node found
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_node_details_no_node(mock_execute_query):
    mock_execute_query.return_value = []
    node_service = NodeService()
    node_details = await node_service.fetch_node_details("invalid_node")
    assert node_details is None


# 17. Test for NodeService.get_node_details - database error
@pytest.mark.asyncio
@patch('db.neo4j_manager.AsyncSessionManager.execute_query', new_callable=AsyncMock)
async def test_get_node_details_error(mock_execute_query):
    mock_execute_query.side_effect = Exception("Database Error")
    node_service = NodeService()
    with pytest.raises(Exception, match="Database Error"):
        await node_service.fetch_node_details("node123")


""" HELPER """


# 1. Test for processing nodes with full database fields
@pytest.mark.asyncio
async def test_process_nodes_with_full_data():
    helper = NodeHelper()

    valid_node = {
        "id": "83f1d55e65830412210737044249bb45203333141c55fb4fd4f383a7e01577b0292e5723137d75dc33e67cccb9536fad4146037"
              "b9fa27bd453f4a68a0c9b1f72",
        "host": "65.108.138.187",
        "port": 30031,
        "country_name": "Finland",
        "client": "erigon",
        "os": "linux",
        "isp": "Hetzner Online GmbH",
        "created_at": "2024-09-08T21:41:18.578996",
        "updated_at": "2024-09-13T16:54:25.261662",
        "status": 0,
        "latitude": 60.17116,
        "longitude": 24.93265
    }

    result = [{
        "NodeId": valid_node["id"],
        "Host": valid_node["host"],
        "Port": valid_node["port"],
        "Country": valid_node["country_name"],
        "Client": valid_node["client"],
        "OS": valid_node["os"],
        "ISP": valid_node["isp"],
        "CreatedAt": valid_node["created_at"],
    }]

    processed_nodes = helper.process_nodes(result)
    assert len(processed_nodes) == 1
    processed_node = processed_nodes[0]
    assert processed_node["Country"] == "Finland"
    assert processed_node["Client"] == "erigon"
    assert processed_node["OS"] == "linux"
    assert processed_node["ISP"] == "Hetzner Online GmbH"
    assert "Enode" in processed_node
    assert "MinutesAgo" in processed_node
    assert processed_node[
               "Enode"] == ("enode://83f1d55e65830412210737044249bb45203333141c55fb4fd4f383a7e01577b0292e5723137d75dc3"
                            "3e67cccb9536fad4146037b9fa27bd453f4a68a0c9b1f72@65.108.138.187:30031")


# 2. Test for is_hexadecimal function
def test_is_hexadecimal_valid():
    assert NodeHelper.is_hexadecimal("a3f5") == 1
    assert NodeHelper.is_hexadecimal("ABC123") == 1


# 3. Test for is_hexadecimal function with invalid input
def test_is_hexadecimal_invalid():
    assert NodeHelper.is_hexadecimal("ZXY123") == 0
    assert NodeHelper.is_hexadecimal("1234G") == 0
    assert NodeHelper.is_hexadecimal(" ") == 0


# 4. Test for create_enode function with valid input
def test_create_enode_valid():
    record = {
        "NodeId": "abcdef123456",
        "Host": "127.0.0.1",
        "Port": 30303
    }
    expected_enode = "enode://abcdef123456@127.0.0.1:30303"
    assert NodeHelper.create_enode(record) == expected_enode


# 5. Test for create_enode function with missing data
def test_create_enode_missing_data():
    record = {
        "NodeId": "abcdef123456",
        "Host": "127.0.0.1"
    }
    with pytest.raises(KeyError):
        NodeHelper.create_enode(record)


# 6. Test for calculate_minutes_ago with valid input
def test_calculate_minutes_ago():
    current_time = datetime.now()
    past_time = current_time - timedelta(minutes=30)
    assert NodeHelper.calculate_minutes_ago(current_time, past_time) == 30


# 7. Test for calculate_minutes_ago when created_at is in the future
def test_calculate_minutes_ago_future_time():
    current_time = datetime.now()
    future_time = current_time + timedelta(minutes=30)
    assert NodeHelper.calculate_minutes_ago(current_time, future_time) == -30


# 8. Test for valid host and port
def test_get_valid_host_and_port_valid(monkeypatch):
    monkeypatch.setenv("APP_HOST", "192.168.1.1")
    monkeypatch.setenv("APP_PORT", "8080")
    host, port = NodeHelper.get_valid_host_and_port()
    assert host != "192.168.1.1"
    assert port != 8080


# 9. Test for invalid port
def test_get_valid_host_and_port_invalid_port(monkeypatch):
    monkeypatch.setenv("APP_PORT", "99999")
    host, port = NodeHelper.get_valid_host_and_port()
    assert host == "127.0.0.1"
    assert port == 5001


# 10. Test for missing port
def test_get_valid_host_and_port_missing_port(monkeypatch):
    monkeypatch.delenv("APP_PORT", raising=False)
    host, port = NodeHelper.get_valid_host_and_port()
    assert host == "127.0.0.1"
    assert port == 5001


# 11. Test for process_relationships with valid relationships
def test_process_relationships_valid():
    relationships = [
        {"relationship_type": "connected", "source": "node1", "target": "node2"},
        {"relationship_type": "connected", "source": "node3", "target": "node4"},
    ]
    processed = NodeHelper.process_relationships(relationships)
    assert len(processed) == 2


# 12. Test for process_relationships with error in result
def test_process_relationships_with_error():
    error_result = {"error": "Connection failed"}
    processed = NodeHelper.process_relationships(error_result)
    assert processed == error_result


# 13. Test for process_nodes with missing CreatedAt
def test_process_nodes_missing_created_at():
    helper = NodeHelper()
    result = [{
        "NodeId": "abcdef123456",
        "Host": "127.0.0.1",
        "Port": 30303,
        "Country": "USA",
        "Client": "Geth",
        "OS": "Linux",
        "ISP": "AWS"
    }]
    processed_nodes = helper.process_nodes(result)
    assert len(processed_nodes) == 0


# 14. Test for process_nodes with invalid CreatedAt format
def test_process_nodes_invalid_created_at_format():
    helper = NodeHelper()
    result = [{
        "NodeId": "abcdef123456",
        "Host": "127.0.0.1",
        "Port": 30303,
        "Country": "USA",
        "Client": "Geth",
        "OS": "Linux",
        "ISP": "AWS",
        "CreatedAt": "invalid-date-format"
    }]
    processed_nodes = helper.process_nodes(result)
    assert len(processed_nodes) == 0


""" API """


# 1. Test for starting the app with a different host and port
@pytest.mark.asyncio
@patch('api.uvicorn.run')
@pytest.mark.usefixtures("mock_env_vars_different_host_port", "mock_async_session_manager")
async def test_uvicorn_run_with_different_host_and_port(mock_uvicorn_run, app):
    from api import ApiServer
    server = ApiServer()
    server.start_server()
    mock_uvicorn_run.assert_called_with(ANY, host='192.168.0.10', port=8080)


# 2. Test for starting the app with the default host and port
@pytest.mark.asyncio
@patch('api.uvicorn.run')
@pytest.mark.usefixtures("mock_env_vars_default", "mock_async_session_manager")
async def test_uvicorn_run_with_default_host_and_port(mock_uvicorn_run, app):
    from api import ApiServer
    server = ApiServer()
    server.start_server()
    mock_uvicorn_run.assert_called_with(ANY, host='127.0.0.1', port=5001)


# 3. Test for starting the app with an invalid port
@pytest.mark.asyncio
@patch('api.uvicorn.run')
@pytest.mark.usefixtures("mock_env_vars_invalid_port", "mock_async_session_manager")
async def test_uvicorn_run_with_invalid_port(mock_uvicorn_run, app):
    from api import ApiServer
    server = ApiServer()
    server.start_server()
    mock_uvicorn_run.assert_called_with(ANY, host='127.0.0.1', port=5001)
