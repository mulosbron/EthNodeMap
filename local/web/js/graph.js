const graphApp = (() => {
    const API_URL = 'http://127.0.0.1:5001';

    const fetchData = async (url) => {
        try {
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            console.error('Error fetching data:', error);
            return [];
        }
    };

    const createCheckboxLabel = (country, onChange) => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = country;
        checkbox.addEventListener('change', onChange);
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(country));
        return label;
    };

    const handleCheckboxChange = (drawGraph) => (event) => {
        const label = event.target.parentElement;
        if (event.target.checked) {
            label.style.backgroundColor = '#8B93B3';
            label.style.color = '#EDEDED';
        } else {
            label.style.backgroundColor = '';
            label.style.color = '';
        }
        drawGraph();
    };

    const loadCountries = async (drawGraph) => {
        const countries = await fetchData(`${API_URL}/nodes/countries`);
        const countrySelect = document.getElementById('country-select');
        const drawGraphHandler = handleCheckboxChange(drawGraph);

        countries.forEach(country => {
            const label = createCheckboxLabel(country, drawGraphHandler);
            countrySelect.appendChild(label);
        });
    };

    const getSelectedValues = (selector) => {
        const checkboxes = Array.from(document.querySelectorAll(selector));
        return checkboxes.filter(checkbox => checkbox.checked).map(checkbox => checkbox.value);
    };

    const getSelectedCountryNodes = async () => {
        const countries = getSelectedValues('#country-select input[type="checkbox"]:checked');
        const dataPromises = countries.map(country => fetchData(`${API_URL}/nodes/relationships/${country}`));
        const allData = await Promise.all(dataPromises);
        return allData.flat();
    };

    const createNode = (id, group) => ({ id, group });

    const createLink = (source, target) => ({ source, target });

    const generateGraphData = (data) => {
        const nodes = [];
        const links = [];
        const nodeMap = {};

        const rootNode = createNode("World", 1);
        nodes.push(rootNode);
        nodeMap[rootNode.id] = rootNode;

        data.forEach(item => {
            const { c, isp, os, client, n } = item;

            const countryNodeId = `${c.name}`;
            if (!nodeMap[countryNodeId]) {
                const countryNode = createNode(countryNodeId, 2);
                nodes.push(countryNode);
                links.push(createLink(rootNode.id, countryNode.id));
                nodeMap[countryNodeId] = countryNode;
            }

            const ispNodeId = `${c.name}-${isp.name}`;
            if (!nodeMap[ispNodeId]) {
                const ispNode = createNode(ispNodeId, 3);
                nodes.push(ispNode);
                links.push(createLink(countryNodeId, ispNode.id));
                nodeMap[ispNodeId] = ispNode;
            }

            const osNodeId = `${c.name}-${isp.name}-${os.name}`;
            if (!nodeMap[osNodeId]) {
                const osNode = createNode(osNodeId, 4);
                nodes.push(osNode);
                links.push(createLink(ispNodeId, osNode.id));
                nodeMap[osNodeId] = osNode;
            }

            const clientNodeId = `${c.name}-${isp.name}-${os.name}-${client.name}`;
            if (!nodeMap[clientNodeId]) {
                const clientNode = createNode(clientNodeId, 5);
                nodes.push(clientNode);
                links.push(createLink(osNodeId, clientNode.id));
                nodeMap[clientNodeId] = clientNode;
            }

            const nodeId = `${n.id}`;
            if (!nodeMap[nodeId]) {
                const nNode = createNode(nodeId, 6);
                nodes.push(nNode);
                links.push(createLink(clientNodeId, nNode.id));
                nodeMap[nodeId] = nNode;
            }
        });

        return { nodes, links };
    };

    const initializeGraph = (nodes, links) => {
        const width = window.innerWidth - 200;
        const height = window.innerHeight;

        d3.select("#graph").select("svg").remove();

        const svg = d3.select("#graph").append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .call(d3.zoom().on("zoom", function () {
                svg.attr("transform", d3.event.transform);
            }))
            .append("g");

        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(d => {
                if (d.source.group === 1 || d.target.group === 1) return 600;
                if (d.source.group === 2 || d.target.group === 2) return 500;
                return 300;
            }))
            .force("charge", d3.forceManyBody().strength(-1000))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius(15))
            .on("tick", () => {
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);

                node
                    .attr("cx", d => d.x)
                    .attr("cy", d => d.y);
            });

        const link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("stroke-width", 20)
            .attr("stroke", "#999");

        const node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(nodes)
            .enter().append("circle")
            .attr("r", d => {
                switch (d.group) {
                    case 1: return 6 * 30;
                    case 2: return 5 * 30;
                    case 3: return 4 * 30;
                    case 4: return 3 * 30;
                    case 5: return 2 * 30;
                    default: return 30;
                }
            })
            .attr("fill", d => d3.schemeCategory10[d.group % 10])
            .call(d3.drag()
                .on("start", dragstarted(simulation))
                .on("drag", dragged)
                .on("end", dragended(simulation)));

        node.append("title")
            .text(d => d.id);

        const legendData = [
            { color: d3.schemeCategory10[1], text: "World" },
            { color: d3.schemeCategory10[2], text: "Country" },
            { color: d3.schemeCategory10[3], text: "ISP" },
            { color: d3.schemeCategory10[4], text: "OS" },
            { color: d3.schemeCategory10[5], text: "Client" },
            { color: d3.schemeCategory10[6], text: "Node" }
        ];

        const legend = d3.select("#legend").selectAll(".legend-item")
            .data(legendData)
            .enter().append("div")
            .attr("class", "legend-item")
            .style("display", "flex")
            .style("align-items", "center")
            .style("margin-bottom", "5px");

        legend.append("div")
            .style("width", "20px")
            .style("height", "20px")
            .style("background-color", d => d.color)
            .style("margin-right", "5px");

        legend.append("div")
            .text(d => d.text);

        simulation.alpha(1).restart();
    };

    const dragstarted = (simulation) => (d) => {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    };

    const dragged = (d) => {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    };

    const dragended = (simulation) => (d) => {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    };

    const drawGraph = async () => {
        const data = await getSelectedCountryNodes();
        const { nodes, links } = generateGraphData(data);
        initializeGraph(nodes, links);
    };

    const init = () => {
        loadCountries(drawGraph);
    };

    return { init };
})();

document.addEventListener('DOMContentLoaded', graphApp.init);
