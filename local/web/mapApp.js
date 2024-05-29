document.addEventListener('DOMContentLoaded', function () {
    var map = L.map('map').setView([0, 0], 1);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    var markers = L.markerClusterGroup();
    var allMarkers = [];

    async function fetchAndPopulateData() {
        try {
            const response = await fetch('http://127.0.0.1:5001/get-nodes');
            const data = await response.json();

            data.forEach(node => {
                var circle = L.circle([node.Latitude, node.Longitude], {
                    color: 'blue',
                    weight: 5,
                    opacity: 0.3,
                    fillColor: '#0000FF',
                    fillOpacity: 0.8,
                    radius: getDynamicRadius(map.getZoom()),
                    os: node.OS,
                    client: node.Client,
                    country: node.Country,
                    isp: node.ISP,
                    nodeId: node.NodeId
                }).bindPopup(`<b>enode://${node.NodeId}@${node.Host}:${node.Port}</b>`);
                circle.nodeData = node;
                circle.on('click', function () {
                    fetchNodeDetails(this.nodeData);
                });
                allMarkers.push({ circle, nodeId: node.NodeId });
                markers.addLayer(circle);
            });
            map.addLayer(markers);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    function fetchNodeDetails(node) {
        const nodeDetailsContainer = document.getElementById('node-details');
        const createdAtUTC = new Date(node.CreatedAt);
        const options = { timeZone: 'Europe/Istanbul', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
        const createdAtLocal = createdAtUTC.toLocaleString('tr-TR', options);
        const uptime = 100 - ((node.Status * 100) / 24);
    
        nodeDetailsContainer.innerHTML = `
            <h3>Node Detayları</h3>
            <p><b>NodeId:</b> ${node.NodeId}</p>
            <p><b>Host:</b> ${node.Host}</p>
            <p><b>Port:</b> ${node.Port}</p>
            <p><b>İstemci:</b> ${node.Client}</p>
            <p><b>İşletim Sistemi:</b> ${node.OS}</p>
            <p><b>İnternet Servis Sağlayıcı:</b> ${node.ISP}</p>
            <p><b>Ülke:</b> ${node.Country}</p>
            <p><b>Koordinat:</b> ${node.Latitude}, ${node.Longitude}</p>
            <p><b>Uptime:</b> %${uptime.toFixed(2)}</p>
            <p><b>Veritabanına Eklenme Tarihi (TSİ):</b> ${createdAtLocal}</p>
        `;
    }


    async function fetchFilters() {
        try {
            let response = await fetch('http://127.0.0.1:5001/get-os-types');
            let data = await response.json();
            const osFilter = document.getElementById('os-filter');
            const osOptions = ['Linux', 'Windows', 'MacOS', 'Android', 'FreeBSD', 'Darwin', 'Others'];
            osOptions.forEach(osType => {
                let option = document.createElement('option');
                option.value = osType;
                option.text = osType;
                osFilter.add(option);
            });

            response = await fetch('http://127.0.0.1:5001/get-isps');
            data = await response.json();
            const ispFilter = document.getElementById('isp-filter');
            const ispOptions = ['Contabo', 'AWS', 'Azure', 'Google', 'Alibaba', 'Oracle', 'IBM', 'Tencent',
                'OVHCloud', 'DO', 'Linode', 'Salesforce', 'Huawei', 'Dell', 'Vultr', 'Heroku', 'Hetzner', 'Scaleway', 'Upcloud', 'Kamatera', 'Others'];
            ispOptions.forEach(ispType => {
                let option = document.createElement('option');
                option.value = ispType;
                option.text = ispType;
                ispFilter.add(option);
            });

            response = await fetch('http://127.0.0.1:5001/get-client-types');
            data = await response.json();
            const clientFilter = document.getElementById('client-filter');
            const clientOptions = ['Geth', 'Nethermind', 'Besu', 'Erigon', 'Reth', 'EthereumJS', 'Others'];
            clientOptions.forEach(clientType => {
                let option = document.createElement('option');
                option.value = clientType;
                option.text = clientType;
                clientFilter.add(option);
            });

            response = await fetch('http://127.0.0.1:5001/get-countries');
            data = await response.json();
            const countryFilter = document.getElementById('country-filter');
            data.forEach(country => {
                let option = document.createElement('option');
                option.value = country;
                option.text = country;
                countryFilter.add(option);
            });
        } catch (error) {
            console.error('Error fetching filters:', error);
        }
    }

    async function fetchDynamicData() {
        try {
            const response = await fetch('http://127.0.0.1:5001/get-node-count');
            const data = await response.json();
            document.getElementById('node-count').innerHTML = `
                <ul class="list-group">
                    <p><br>Toplam Node Sayısı: ${data.NumberOfNodes}<br><br></p>
                </ul>`;
            await fetchLatestNodes();
        } catch (error) {
            console.error('Error fetching dynamic data:', error);
        }
    }

    async function fetchLatestNodes() {
        try {
            const response = await fetch('http://127.0.0.1:5001/get-latest-nodes');
            const data = await response.json();
            const listGroup = document.querySelector('#latest-node .list-group');
            listGroup.innerHTML = '';
            data.forEach(node => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                listItem.innerHTML = `
                    <span>Ülke: ${node.Country}<br>İstemci: ${node.Client}<br>OS: ${node.OS}</span><br>
                    <span>Enode: <button class="copy-button" data-enode="${node.Enode}">Kopyala</button></span><br><br>
                    <span>${node.MinutesAgo} dakika önce eklendi</span><br><br>
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
                        }, 2000);
                    });
                });
            });
        } catch (error) {
            console.error('Error fetching latest nodes:', error);
        }
    }

    async function fetchStatistics() {
        try {
            const osResponse = await fetch('http://127.0.0.1:5001/get-statistics/os');
            const osData = await osResponse.json();
            updateStatisticsTable('os-statistics', osData.os);

            const clientResponse = await fetch('http://127.0.0.1:5001/get-statistics/client');
            const clientData = await clientResponse.json();
            updateStatisticsTable('client-statistics', clientData.client);

            const ispResponse = await fetch('http://127.0.0.1:5001/get-statistics/isp');
            const ispData = await ispResponse.json();
            updateStatisticsTable('isp-statistics', ispData.isp);

            const countryResponse = await fetch('http://127.0.0.1:5001/get-statistics/country');
            const countryData = await countryResponse.json();
            updateStatisticsTable('country-statistics', countryData.country);

        } catch (error) {
            console.error('Error fetching statistics:', error);
        }
    }

    function updateStatisticsTable(tableId, data) {
        const listGroup = document.querySelector(`#${tableId} .list-group`);
        listGroup.innerHTML = '';

        data.sort((a, b) => b.percentage - a.percentage);

        data.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            listItem.innerHTML = `<span>${item.type}</span>
                <span class="list-group-progress" style="width: ${item.percentage.toFixed(2)}%;"></span>
                <span class="float-right text-muted">${item.percentage.toFixed(2)}%</span>`;
            listGroup.appendChild(listItem);
        });
    }

    function applyFilters() {
        var osFilterValue = document.getElementById('os-filter').value;
        var ispFilterValue = document.getElementById('isp-filter').value;
        var clientFilterValue = document.getElementById('client-filter').value;
        var countryFilterValue = document.getElementById('country-filter').value;

        markers.clearLayers();

        allMarkers.forEach(function (markerObj) {
            var marker = markerObj.circle;
            var markerOS = marker.options.os.toLowerCase();
            var markerISP = marker.options.isp.toLowerCase();
            var markerClient = marker.options.client.toLowerCase();
            var markerCountry = marker.options.country;

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
                case 'Android':
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

            if (osMatch &&
                clientMatch &&
                ispMatch &&
                (countryFilterValue === 'all' || markerCountry === countryFilterValue)) {
                markers.addLayer(marker);
            }
        });

        map.addLayer(markers);
    }

    function getDynamicRadius(zoom) {
        return Math.min(250000 * Math.pow(2, 2 - zoom), 50000);
    }

    function updateCircleRadius() {
        allMarkers.forEach(markerObj => {
            const radius = getDynamicRadius(map.getZoom());
            markerObj.circle.setRadius(radius);
        });
    }

    map.on('zoomend', updateCircleRadius);

    fetchAndPopulateData();
    fetchFilters();
    fetchDynamicData();
    fetchStatistics();

    document.getElementById('apply-filters').addEventListener('click', applyFilters);
    document.getElementById('navigate-button').addEventListener('click', function() {
        window.location.href = 'graph.html';
      });

    setInterval(fetchDynamicData, 1500000);
    setInterval(fetchLatestNodes, 1500000);
    setInterval(fetchStatistics, 1500000);
});
