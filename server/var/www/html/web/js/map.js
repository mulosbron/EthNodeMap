const mapApp = (() => {
    const API_URL = 'https://api.ethernodesmap.org';
    const map = L.map('map', {
        center: [45, -45],
        zoom: 3,
        minZoom: 2,
        maxBounds: [
            [-90, -180],
            [90, 180]
        ],
        maxBoundsViscosity: 1.0
    });
    const markers = L.markerClusterGroup();
    const allMarkers = [];
    let heatLayer;
    let choroplethLayer;
    
    const toggleMapLayers = () => {
        const mapView = document.querySelector('input[name="mapView"]:checked').value;
        if (mapView === 'heatmap') {
            if (heatLayer) {
                map.removeLayer(markers);
                if (choroplethLayer) map.removeLayer(choroplethLayer);
                map.addLayer(heatLayer);
            }
        } else if (mapView === 'choroplethmap') {
            if (choroplethLayer) {
                map.removeLayer(markers);
                if (heatLayer) map.removeLayer(heatLayer);
                map.addLayer(choroplethLayer);
            }
        } else {
            if (heatLayer) map.removeLayer(heatLayer);
            if (choroplethLayer) map.removeLayer(choroplethLayer);
            map.addLayer(markers);
        }
    };
    const initalizeTileLayer = () => {
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            noWrap: true
        }).addTo(map);      
    };
    const attachZoomEndListener = () => {
        map.on('zoomend', () => updateCircleRadius());
    };
    const initializeMap = () => {
        initalizeTileLayer();
        attachZoomEndListener();
        document.querySelectorAll('input[name="mapView"]').forEach(input => {
            input.addEventListener('change', toggleMapLayers);
        });
    };
    const calculateDynamicRadius = (zoom) => Math.min(400000 * Math.pow(2, 2 - zoom), 50000);
    const updateCircleRadius = () => {
        allMarkers.forEach(markerObj => {
            const radius = calculateDynamicRadius(map.getZoom());
            markerObj.circle.setRadius(radius);
        });
    };
    const fetchData = async (endpoint) => {
        try {
            const response = await fetch(`${API_URL}${endpoint}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching data:', error);
            return [];
        }
    };
    const createMarker = (node) => {
        const circle = L.circle([node.Latitude, node.Longitude], {
            radius: calculateDynamicRadius(map.getZoom()),
            os: node.OS,
            client: node.Client,
            country: node.Country,
            isp: node.ISP,
            nodeId: node.NodeId
        });
        circle.nodeData = node;
        circle.on('click', () => fetchNodeDetails(node));
        return { circle, nodeId: node.NodeId };
    };
    const populateMarkers = (nodes) => {
        nodes.forEach(node => {
            const markerObj = createMarker(node);
            allMarkers.push(markerObj);
            markers.addLayer(markerObj.circle);
        });
        map.addLayer(markers);
    };
    
    const fetchAndPopulateData = async () => {
        const nodes = await fetchData('/nodes');
        populateMarkers(nodes);
    };
    const populateFilters = (filterElement, options) => {
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.text = option;
            filterElement.add(optionElement);
        });
    };
    const fetchAndPopulateFilters = async () => {
        const countryData = await fetchData('/nodes/countries');
        const countryOptions = countryData;
        populateFilters(document.getElementById('country-filter'), countryOptions);
    };
    const fetchNodeDetails = (node) => {
        const modal = document.getElementById('node-details-modal');
        const span = modal.getElementsByClassName('close')[0];
    
        document.getElementById('node-id').textContent = node.NodeId;
        document.getElementById('node-host').textContent = node.Host;
        document.getElementById('node-port').textContent = node.Port;
        document.getElementById('node-client').textContent = node.Client;
        document.getElementById('node-os').textContent = node.OS;
        document.getElementById('node-isp').textContent = node.ISP;
        document.getElementById('node-country').textContent = node.Country;
        document.getElementById('node-coordinates').textContent = `${node.Latitude}, ${node.Longitude}`;
        document.getElementById('node-uptime').textContent = (100 - ((node.Status * 100) / 24)).toFixed(2);
    
        const createdAtUTC = new Date(node.CreatedAt);
        const options = { timeZone: 'Europe/Istanbul', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
        const createdAtLocal = createdAtUTC.toLocaleString('en-GB', options);
        document.getElementById('node-created-at').textContent = createdAtLocal;
    
        modal.showModal();
    
        span.onclick = () => {
            modal.close();
        }
    
        window.onclick = (event) => {
            if (event.target == modal) {
                modal.close();
            }
        }
    };    
    const updateDynamicData = (data) => {
        document.getElementById('total-node-count').textContent = data.NumberOfNodes;
    };
    const fetchAndPopulateDynamicData = async () => {
        const data = await fetchData('/nodes/count');
        updateDynamicData(data);
        await fetchAndPopulateLatestNodes();
    };
    const fetchAndPopulateLatestNodes = async () => {
        try {
            const data = await fetchData('/nodes/latest');
            populateLatestNodes(data, 0);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };
    const populateLatestNodes = (nodes, index) => {
        renderTable(nodes[index]);
        addCopyButtonListeners(nodes[index]);
        document.getElementById('left').onclick = () => {
            if (index > 0) {
                populateLatestNodes(nodes, index - 1);
            }
        };
        document.getElementById('right').onclick = () => {
            if (index < nodes.length - 1) {
                populateLatestNodes(nodes, index + 1);
            }
        };
        updateButtons(nodes, index);
    };
    const renderTable = (node) => {
        const latestNodeTable = document.querySelector('#latest-node tbody');
        latestNodeTable.innerHTML = '';
        const template = document.getElementById('latest-node-template').content;
        const row = template.cloneNode(true);
        row.querySelector('.node-country').textContent = ` ${node.Country}`;
        row.querySelector('.node-client').textContent = ` ${node.Client}`;
        row.querySelector('.node-os').textContent = ` ${node.OS}`;
        row.querySelector('.node-isp').textContent = ` ${node.ISP}`;
        row.querySelector('.copy-button').setAttribute('data-enode', node.Enode);
        row.querySelector('.node-added-time').textContent = `${node.MinutesAgo} minutes ago added`;
        latestNodeTable.appendChild(row);
    };
    const addCopyButtonListeners = (node) => {
        document.querySelectorAll('.copy-button').forEach(button => {
            button.onclick = () => {
                const enode = node.Enode;
                navigator.clipboard.writeText(enode).then(() => {
                    button.textContent = 'Copied';
                    button.disabled = true;
                    setTimeout(() => {
                        button.textContent = 'Copy';
                        button.disabled = false;
                    }, 2000);
                });
            };
        });
    };
    const updateButtons = (nodes, index) => {
        const leftButton = document.getElementById('left');
        const rightButton = document.getElementById('right');
        leftButton.disabled = index === 0;
        rightButton.disabled = index >= nodes.length - 1;
    };
    const fetchStatisticsByCategory = async (category) => {
        let data;
        switch (category) {
            case 'client':
                data = await fetchData('/statistics/client');
                return data.client;
            case 'country':
                data = await fetchData('/statistics/country');
                return data.country;
            case 'os':
                data = await fetchData('/statistics/os');
                return data.os;
            case 'isp':
                data = await fetchData('/statistics/isp');
                return data.isp;
            default:
                return [];
        }
    };
    const handleRadioChange = async (event) => {
        const selectedCategory = event.target.value;
        const data = await fetchStatisticsByCategory(selectedCategory);
        updateStatisticsTable('statistics-table', data);
    };
    const initializeRadioButtons = () => {
        const radioButtons = document.querySelectorAll('.radio-input');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', handleRadioChange);
        });
        const defaultRadio = document.getElementById('client');
        if (defaultRadio) {
            defaultRadio.checked = true;
            handleRadioChange({ target: { value: 'client' } });
        }
    };
    const updateStatisticsTable = (tableId, data) => {
        const table = document.querySelector(`#${tableId}`);
        const tbody = table.querySelector('tbody');
        const template = document.getElementById('statistics-row-template').content;
        tbody.innerHTML = '';
        data.sort((a, b) => b.percentage - a.percentage);
        data.forEach(item => {
            const row = template.cloneNode(true);
            row.querySelector('td:first-child').textContent = item.type;
            row.querySelector('.float-right').textContent = `${item.percentage.toFixed(2)}%`;
            row.querySelector('.list-group-progress').value = item.percentage.toFixed(2);
            tbody.appendChild(row);
        });
    };
    const filterMarkers = () => {
        const osFilterValue = document.getElementById('os-filter').value.toLowerCase();
        const ispFilterValue = document.getElementById('isp-filter').value.toLowerCase();
        const clientFilterValue = document.getElementById('client-filter').value.toLowerCase();
        const countryFilterValue = document.getElementById('country-filter').value.toLowerCase();
        markers.clearLayers();
        allMarkers.forEach(markerObj => {
            const marker = markerObj.circle;
            const markerOS = marker.options.os.toLowerCase();
            const markerISP = marker.options.isp.toLowerCase();
            const markerClient = marker.options.client.toLowerCase();
            const markerCountry = marker.options.country.toLowerCase();
            const osMatch = osFilterValue === 'all' || markerOS.includes(osFilterValue);
            const clientMatch = clientFilterValue === 'all' || markerClient.includes(clientFilterValue);
            const ispMatch = ispFilterValue === 'all' || markerISP.includes(ispFilterValue) || (ispFilterValue === 'aws' && markerISP.includes('amazon')) || (ispFilterValue === 'linode' && markerISP.includes('akamai'));
            const countryMatch = countryFilterValue === 'all' || markerCountry === countryFilterValue;
            if (osMatch && clientMatch && ispMatch && countryMatch) {
                markers.addLayer(marker);
            }
        });
        map.addLayer(markers);
    };
    const initializeEventListeners = () => {
        const filters = ['country-filter', 'os-filter', 'client-filter', 'isp-filter'];
        filters.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            if (filterElement) {
                filterElement.addEventListener('change', filterMarkers);
            } else {
                console.error(`'${filterId}' element not found.`);
            }
        });
    };
    const startIntervals = () => {
        setInterval(fetchAndPopulateDynamicData, 900000);
        setInterval(fetchAndPopulateLatestNodes, 900000);
    };
    const init = () => {
        initializeMap();
        initializeRadioButtons();
        fetchAndPopulateData();
        fetchAndPopulateFilters();
        fetchAndPopulateDynamicData();
        initializeEventListeners();
        startIntervals();
    };
    return { init };        
})();

document.addEventListener('DOMContentLoaded', mapApp.init);