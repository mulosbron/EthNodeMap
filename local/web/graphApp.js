const countriesUrl = "http://127.0.0.1:5001/nodes/countries";
const nodeParentsUrl = "http://127.0.0.1:5001/nodes/country/";

async function fetchData(url) {
  const response = await fetch(url);
  return await response.json();
}

async function loadCountries() {
  const countries = await fetchData(countriesUrl);
  const countryList = document.getElementById('country-list');

  countries.forEach(country => {
    const label = document.createElement('label');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = country;
    checkbox.addEventListener('change', function () {
      if (this.checked) {
        label.style.backgroundColor = '#8B93B3';
        label.style.color = '#EDEDED';
      } else {
        label.style.backgroundColor = '';
        label.style.color = '';
      }
      drawGraph();
    });
    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(country));
    countryList.appendChild(label);
  });
}

async function getSelectedCountryNodes() {
  const checkboxes = Array.from(document.querySelectorAll('#country-list input[type="checkbox"]:checked'));
  const countries = checkboxes.map(checkbox => checkbox.value);
  let allData = [];
  for (let country of countries) {
    const data = await fetchData(`${nodeParentsUrl}${country}`);
    allData = allData.concat(data);
  }
  return allData;
}

async function drawGraph() {
  const data = await getSelectedCountryNodes();

  const nodes = [];
  const links = [];
  const nodeMap = {};

  const rootNode = { id: "Dünya", group: 1 };
  if (!nodeMap[rootNode.id]) {
    nodes.push(rootNode);
    nodeMap[rootNode.id] = rootNode;
  }

  data.forEach(item => {
    const { root, c, isp, os, client, n } = item;

    const countryNodeId = `${c.name}`
    if (!nodeMap[countryNodeId]) {
      const countryNode = { id: countryNodeId, group: 2 };
      nodes.push(countryNode);
      links.push({ source: rootNode.id, target: countryNode.id });
      nodeMap[countryNodeId] = countryNode;
    }

    const ispNodeId = `${c.name}-${isp.name}`;
    if (!nodeMap[ispNodeId]) {
      const ispNode = { id: ispNodeId, group: 3 };
      nodes.push(ispNode);
      links.push({ source: c.name, target: ispNode.id });
      nodeMap[ispNodeId] = ispNode;
    }

    const osNodeId = `${c.name}-${isp.name}-${os.name}`;
    if (!nodeMap[osNodeId]) {
      const osNode = { id: osNodeId, group: 4 };
      nodes.push(osNode);
      links.push({ source: ispNodeId, target: osNode.id });
      nodeMap[osNodeId] = osNode;
    }

    const clientNodeId = `${c.name}-${isp.name}-${os.name}-${client.name}`;
    if (!nodeMap[clientNodeId]) {
      const clientNode = { id: clientNodeId, group: 5 };
      nodes.push(clientNode);
      links.push({ source: osNodeId, target: clientNode.id });
      nodeMap[clientNodeId] = clientNode;
    }

    const nodeId = `${n.id}`;
    if (!nodeMap[nodeId]) {
      const nNode = { id: nodeId, group: 6 };
      nodes.push(nNode);
      links.push({ source: clientNodeId, target: nNode.id });
      nodeMap[nodeId] = nNode;
    }
  });

  const width = window.innerWidth - 200;
  const height = window.innerHeight;

  d3.select("#graph").select("svg").remove();

  const svg = d3.select("#graph").append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .call(d3.zoom().on("zoom", function () {
      svg.attr("transform", d3.event.transform)
    }))
    .append("g");

  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(300))
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
    .attr("stroke-width", 10)
    .attr("stroke", "#999");

  const node = svg.append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(nodes)
    .enter().append("circle")
    .attr("r", 30)
    .attr("fill", d => d3.schemeCategory10[d.group % 10])
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

  node.append("title")
    .text(d => d.id);

  const legendData = [
    { color: d3.schemeCategory10[1], text: "Dünya" },
    { color: d3.schemeCategory10[2], text: "Ülke" },
    { color: d3.schemeCategory10[3], text: "İSS" },
    { color: d3.schemeCategory10[4], text: "İşletim Sistemi" },
    { color: d3.schemeCategory10[5], text: "İstemci" },
    { color: d3.schemeCategory10[6], text: "Düğüm" }
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

  function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }

  function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
}

loadCountries();

document.getElementById('home-button').addEventListener('click', function() {
  window.location.href = 'index.html';
});
