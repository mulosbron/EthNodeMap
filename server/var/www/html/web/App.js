document.addEventListener('DOMContentLoaded', function () {
    var map = L.map('map').setView([0, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    var markers = L.markerClusterGroup();
    var allMarkers = [];

    function fetchAndPopulateData() {
        fetch('https://api.eth-node-map.xyz/get-nodes')
            .then(response => response.json())
            .then(data => {
                data.forEach(node => {
                    var marker = L.marker([node.Latitude, node.Longitude], {
                        os: node.OS,
                        client: node.Client,
                        country: node.Country,
                        isp: node.ISP,
                        nodeId: node.NodeId,
                        relationships: node.Relationships || []
                    }).bindPopup(`<b>${node.Client}</b><br>${node.Country}<br>${node.Host}<br>${node.ISP}<br>${node.OS}<br>${node.Port}`);
                    marker.on('click', function() {
                        fetchNodeDetails(node.NodeId);
                    });
                    allMarkers.push(marker);
                    markers.addLayer(marker);
                });
                map.addLayer(markers);
            });
    }

    function fetchFilters() {
        fetch('https://api.eth-node-map.xyz/get-os-types')
            .then(response => response.json())
            .then(data => {
                const osFilter = document.getElementById('os-filter');
                data.forEach(osType => {
                    let option = document.createElement('option');
                    option.value = osType;
                    option.text = osType;
                    osFilter.add(option);
                });
            });

        fetch('https://api.eth-node-map.xyz/get-isps')
            .then(response => response.json())
            .then(data => {
                const ispFilter = document.getElementById('isp-filter');
                data.forEach(ispType => {
                    let option = document.createElement('option');
                    option.value = ispType;
                    option.text = ispType;
                    ispFilter.add(option);
                });
            });

        fetch('https://api.eth-node-map.xyz/get-client-types')
            .then(response => response.json())
            .then(data => {
                const clientFilter = document.getElementById('client-filter');
                data.forEach(clientType => {
                    let option = document.createElement('option');
                    option.value = clientType;
                    option.text = clientType;
                    clientFilter.add(option);
                });
            });

        fetch('https://api.eth-node-map.xyz/get-countries')
            .then(response => response.json())
            .then(data => {
                const countryFilter = document.getElementById('country-filter');
                data.forEach(country => {
                    let option = document.createElement('option');
                    option.value = country;
                    option.text = country;
                    countryFilter.add(option);
                });
            });

        fetch('https://api.eth-node-map.xyz/get-relationship-types/clients')
            .then(response => response.json())
            .then(data => {
                const relationshipFilter = document.getElementById('relationship-filter');
                data.forEach(relationship => {
                    let option = document.createElement('option');
                    option.value = relationship;
                    option.text = relationship;
                    relationshipFilter.add(option);
                });
            });

        fetch('https://api.eth-node-map.xyz/get-relationship-types/countries')
            .then(response => response.json())
            .then(data => {
                const relationshipFilter = document.getElementById('relationship-filter');
                data.forEach(relationship => {
                    let option = document.createElement('option');
                    option.value = relationship;
                    option.text = relationship;
                    relationshipFilter.add(option);
                });
            });

        fetch('https://api.eth-node-map.xyz/get-relationship-types/os-types')
            .then(response => response.json())
            .then(data => {
                const relationshipFilter = document.getElementById('relationship-filter');
                data.forEach(relationship => {
                    let option = document.createElement('option');
                    option.value = relationship;
                    option.text = relationship;
                    relationshipFilter.add(option);
                });
            });

        fetch('https://api.eth-node-map.xyz/get-relationship-types/isps')
            .then(response => response.json())
            .then(data => {
                const relationshipFilter = document.getElementById('relationship-filter');
                data.forEach(relationship => {
                    let option = document.createElement('option');
                    option.value = relationship;
                    option.text = relationship;
                    relationshipFilter.add(option);
                });
            });
    }

    function fetchDynamicData() {
        fetch('https://api.eth-node-map.xyz/get-node-count')
            .then(response => response.json())
            .then(data => {
                document.getElementById('dynamic-data').innerHTML = `<h3>Dinamik Veriler</h3><p>Toplam Node Sayısı: ${data.NumberOfNodes}</p>`;
            });
    }

    function fetchStatistics(endpoint, tableId) {
        fetch(endpoint)
            .then(response => response.json())
            .then(data => {
                const listGroup = document.querySelector(`#${tableId} .list-group`);
                listGroup.innerHTML = '';
                const sortedData = Object.entries(data).sort((a, b) => b[1] - a[1]);
                sortedData.forEach(([key, value]) => {
                    const percentage = value.toFixed(2);
                    const listItem = document.createElement('li');
                    listItem.className = 'list-group-item';
                    listItem.innerHTML = `<span>${key.split('_')[1]}</span>
                        <span class="list-group-progress" style="width: ${percentage}%"></span>
                        <span class="float-right text-muted">${percentage}%</span>`;
                    listGroup.appendChild(listItem);
                });
            });
    }

    function fetchNodeDetails(nodeId) {
        fetch(`https://api.eth-node-map.xyz/get-node-details/${nodeId}`)
            .then(response => response.json())
            .then(data => {
                const nodeDetailsDiv = document.getElementById('node-details');
                nodeDetailsDiv.innerHTML = `
                    <h3>Node Detayları</h3>
                    <p><b>Client:</b> ${data.Client}</p>
                    <p><b>Country:</b> ${data.Country}</p>
                    <p><b>Host:</b> ${data.Host}</p>
                    <p><b>ISP:</b> ${data.ISP}</p>
                    <p><b>Latitude:</b> ${data.Latitude}</p>
                    <p><b>Longitude:</b> ${data.Longitude}</p>
                    <p><b>NodeId:</b> ${data.NodeId}</p>
                    <p><b>OS:</b> ${data.OS}</p>
                    <p><b>Port:</b> ${data.Port}</p>
                    <p><b>Status:</b> ${data.Status}</p>
                `;
            });
    }

    function applyFilters() {
        var osFilterValue = document.getElementById('os-filter').value;
        var ispFilterValue = document.getElementById('isp-filter').value;
        var clientFilterValue = document.getElementById('client-filter').value;
        var countryFilterValue = document.getElementById('country-filter').value;
        var relationshipFilterValue = document.getElementById('relationship-filter').value;

        markers.clearLayers();

        allMarkers.forEach(marker => {
            var markerOS = marker.options.os;
            var markerISP = marker.options.isp;
            var markerClient = marker.options.client;
            var markerCountry = marker.options.country;
            var markerRelationships = marker.options.relationships;

            var relationshipMatch = markerRelationships.includes(relationshipFilterValue) || relationshipFilterValue === 'all';

            if ((osFilterValue === 'all' || markerOS === osFilterValue) &&
                (ispFilterValue === 'all' || markerISP === ispFilterValue) &&
                (clientFilterValue === 'all' || markerClient === clientFilterValue) &&
                (countryFilterValue === 'all' || markerCountry === countryFilterValue) &&
                relationshipMatch) {
                markers.addLayer(marker);
            }
        });

        map.addLayer(markers);
    }

    fetchAndPopulateData();
    fetchFilters();
    fetchDynamicData();

    fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/OS_', 'os-statistics');
    fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/CLIENT_', 'client-statistics');
    fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/ISP_', 'isp-statistics');
    fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/COUNTRY_', 'country-statistics');

    document.getElementById('apply-filters').addEventListener('click', applyFilters);

    setInterval(fetchDynamicData, 30000);
    setInterval(() => fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/OS_', 'os-statistics'), 30000);
    setInterval(() => fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/CLIENT_', 'client-statistics'), 30000);
    setInterval(() => fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/ISP_', 'isp-statistics'), 30000);
    setInterval(() => fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/COUNTRY_', 'country-statistics'), 30000);
});
