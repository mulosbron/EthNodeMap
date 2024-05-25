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
                const osOptions = ['Linux', 'Windows', 'MacOS', 'Android', 'FreeBSD', 'Darwin', 'Others'];
                osOptions.forEach(osType => {
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
                const ispOptions = ['Contabo', 'AWS', 'Azure', 'Google', 'Alibaba', 'Oracle', 'IBM', 'Tencent', 
                'OVHCloud', 'DO', 'Linode', 'Salesforce', 'Huawei', 'Dell', 'Vultr', 'Heroku', 'Hetzner', 'Scaleway', 'Upcloud', 'Kamatera', 'Others'];
                ispOptions.forEach(ispType => {
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
                const clientOptions = ['Geth', 'Nethermind', 'Besu', 'Erigon', 'Reth', 'EthereumJS', 'Others'];
                clientOptions.forEach(clientType => {
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
                document.getElementById('node-count').innerHTML = `
                <ul class="list-group">
                    <p><br>Toplam Node Sayısı: ${data.NumberOfNodes}<br><br></p>
                </ul>`;
                fetchLatestNodes();
            });
    }

    function fetchLatestNodes() {
        fetch('https://api.eth-node-map.xyz/get-latest-nodes')
            .then(response => response.json())
            .then(data => {
                const listGroup = document.querySelector('#latest-node .list-group');
                listGroup.innerHTML = '';
                data.forEach(node => {
                    const minutesAgo = Math.floor((Date.now() - new Date(node.CreatedAt).getTime()) / 60000);
                    const listItem = document.createElement('li');
                    listItem.className = 'list-group-item';
                    listItem.innerHTML = `
                        <span>Country: ${node.Country}<br>Client: ${node.Client}<br>OS: ${node.OS}</span><br>
                        <span>Enode: <button class="copy-button" data-enode="${node.Enode}">Kopyala</button></span><br><br>
                        <span>${minutesAgo} dakika önce eklendi</span><br><br>
                    `;
                    listGroup.appendChild(listItem);
                });

                document.querySelectorAll('.copy-button').forEach(button => {
                    button.addEventListener('click', function () {
                        const enode = this.getAttribute('data-enode');
                        navigator.clipboard.writeText(enode).then(() => {
                            this.textContent = 'Kopyalandı';
                            this.disabled = true;

                            setTimeout(() => {
                                this.textContent = 'Kopyala';
                                this.disabled = false;
                            }, 2000); // 2 saniye sonra tekrar "Kopyala" yazısını göster
                        });
                    });
                });
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
                    <p><b>Created at:</b> ${data.CreatedAt}</p>
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
            var markerOS = marker.options.os.toLowerCase();
            var markerISP = marker.options.isp.toLowerCase();
            var markerClient = marker.options.client.toLowerCase();
            var markerCountry = marker.options.country;
            var markerRelationships = marker.options.relationships;
    
            var osMatch = false;
            switch (osFilterValue) {
                case 'Linux':
                    osMatch = markerOS.includes('linux');
                    break;
                case 'Windows':
                    osMatch = markerOS.includes('windows');
                    break;
                case 'MacOS':
                    osMatch = markerOS.includes('macos');
                    break;
                case 'Andorid':
                    osMatch = markerOS.includes('android');
                    break;
                case 'FreeBSD':
                    osMatch = markerOS.includes('freebsd');
                    break;
                case 'Darwin':
                    osMatch = markerOS.includes('darwin');
                    break;
                case 'Others':
                    osMatch = !markerOS.includes('linux') && !markerOS.includes('windows') &&
                        !markerOS.includes('macos') && !markerOS.includes('android') &&
                        !markerOS.includes('freebsd') && !markerOS.includes('darwin');
                    break;
                default:
                    osMatch = true;
            }
    
            var clientMatch = false;
            switch (clientFilterValue) {
                case 'Geth':
                    clientMatch = markerClient.includes('geth');
                    break;
                case 'Nethermind':
                    clientMatch = markerClient.includes('nethermind');
                    break;
                case 'Besu':
                    clientMatch = markerClient.includes('besu');
                    break;
                case 'Erigon':
                    clientMatch = markerClient.includes('erigon');
                    break;
                case 'Reth':
                    clientMatch = markerClient.includes('reth');
                    break;
                case 'EthereumJS':
                    clientMatch = markerClient.includes('ethereumjs');
                    break;
                case 'Others':
                    clientMatch = !markerClient.includes('geth') && !markerClient.includes('nethermind') &&
                        !markerClient.includes('besu') && !markerClient.includes('erigon') &&
                        !markerClient.includes('reth') && !markerClient.includes('ethereumjs');
                    break;
                default:
                    clientMatch = true;
            }
    
            var ispMatch = false;
            switch (ispFilterValue) {
                case 'Contabo':
                    ispMatch = markerISP.includes('contabo');
                    break;
                case 'AWS':
                    ispMatch = markerISP.includes('amazon') || markerISP.includes('aws');
                    break;
                case 'Azure':
                    ispMatch = markerISP.includes('microsoft') || markerISP.includes('azure');
                    break;
                case 'Google':
                    ispMatch = markerISP.includes('google');
                    break;
                case 'Alibaba':
                    ispMatch = markerISP.includes('alibaba');
                    break;
                case 'Oracle':
                    ispMatch = markerISP.includes('oracle');
                    break;
                case 'IBM':
                    ispMatch = markerISP.includes('ibm');
                    break;
                case 'Tencent':
                    ispMatch = markerISP.includes('tencent');
                    break;
                case 'OVHCloud':
                    ispMatch = markerISP.includes('ovh');
                    break;
                case 'DO':
                    ispMatch = markerISP.includes('digitalocean');
                    break;
                case 'Linode':
                    ispMatch = markerISP.includes('linode') || markerISP.includes('akamai');
                    break;
                case 'Salesforce':
                    ispMatch = markerISP.includes('salesforce');
                    break;
                case 'Huawei':
                    ispMatch = markerISP.includes('huawei') && markerISP.includes('cloud');
                    break;
                case 'Dell':
                    ispMatch = markerISP.includes('dell') && markerISP.includes('cloud');
                    break;
                case 'Vultr':
                    ispMatch = markerISP.includes('vultr');
                    break;
                case 'Heroku':
                    ispMatch = markerISP.includes('heroku');
                    break;
                case 'Hetzner':
                    ispMatch = markerISP.includes('hetzner');
                    break;
                case 'Scaleway':
                    ispMatch = markerISP.includes('scaleway');
                    break;
                case 'Upcloud':
                    ispMatch = markerISP.includes('upcloud');
                    break;
                case 'Kamatera':
                    ispMatch = markerISP.includes('kamatera');
                    break;
                case 'Others':
                    ispMatch = !markerISP.includes('contabo') && !markerISP.includes('amazon') &&
                        !markerISP.includes('aws') && !markerISP.includes('microsoft') &&
                        !markerISP.includes('azure') && !markerISP.includes('google') &&
                        !markerISP.includes('alibaba') && !markerISP.includes('oracle') &&
                        !markerISP.includes('ibm') && !markerISP.includes('tencent') &&
                        !markerISP.includes('ovh') && !markerISP.includes('digitalocean') &&
                        !markerISP.includes('linode') && !markerISP.includes('akamai') &&
                        !markerISP.includes('salesforce') && !(markerISP.includes('huawei') && markerISP.includes('cloud')) &&
                        !(markerISP.includes('dell') && markerISP.includes('cloud')) && !markerISP.includes('vultr') &&
                        !markerISP.includes('heroku') && !markerISP.includes('hetzner') &&
                        !markerISP.includes('scaleway') && !markerISP.includes('upcloud') &&
                        !markerISP.includes('kamatera');
                    break;
                default:
                    ispMatch = true;
            }
    
            var relationshipMatch = markerRelationships.includes(relationshipFilterValue) || relationshipFilterValue === 'all';
    
            if (osMatch &&
                clientMatch &&
                ispMatch &&
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
    setInterval(fetchLatestNodes, 30000);
    setInterval(() => fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/OS_', 'os-statistics'), 30000);
    setInterval(() => fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/CLIENT_', 'client-statistics'), 30000);
    setInterval(() => fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/ISP_', 'isp-statistics'), 30000);
    setInterval(() => fetchStatistics('https://api.eth-node-map.xyz/get-relationship-percentage/COUNTRY_', 'country-statistics'), 30000);
});
