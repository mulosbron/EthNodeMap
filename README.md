# EthNodeMap

## Overview
EthNodeMap is a visualization project designed to display Ethereum network nodes on an interactive map and as a graph structure. The platform allows users to explore node distribution and relationships across the globe.

## Links
- [ethernodesmap](https://ethernodesmap.org/en/index.html)
- [ethernodesmap API](https://api.ethernodesmap.org/)

## Purpose
To create a comprehensive visualization tool for Ethereum network nodes that provides real-time insights into the network's geographical distribution and infrastructure. The project aims to help users understand the Ethereum network's decentralization through interactive maps and graph visualizations.

### Key Objectives:
- Visualize Ethereum nodes geographically on a world map
- Display node relationships through tree graph structures
- Provide filtering capabilities by country, OS, ISP, and client type
- Collect and maintain up-to-date Ethereum node data

## Scope

### Technology Stack:
- **Backend**: Python 3.7+, Flask, Flask-CORS
- **Database**: Neo4j
- **Data Collection**: BeautifulSoup4, Requests
- **Frontend**: HTML, CSS, JavaScript
- **Visualization**: D3.js (graphs), Leaflet.js (maps)
- **Server**: Nginx

### Project Features:
- Node filtering by country, OS, ISP, and client type
- Interactive map with clickable node details
- Real-time statistics dashboard
- Tree graph visualization for selected countries
- Automated data collection from Etherscan
- RESTful API for accessing node data

## Implementation

### API Endpoints:
- `/nodes` - List all nodes with properties
- `/nodes/operating-systems` - List all unique operating systems
- `/nodes/clients` - List all unique client types
- `/nodes/countries` - List all unique countries
- `/nodes/isps` - List all unique ISPs
- `/nodes/ids` - List all unique node IDs
- `/nodes/details/<node_id>` - Get specific node details
- `/nodes/relationships/<country_name>` - Get node relationships for specific country
- `/nodes/count` - Get total node count
- `/nodes/latest` - List recently added nodes
- `/nodes/filter` - Filter nodes by criteria
- `/statistics/os` - Get operating system statistics
- `/statistics/client` - Get client statistics
- `/statistics/isp` - Get ISP statistics
- `/statistics/country` - Get country statistics

### Development Process:
1. **Data Collection**: Web scraping from Ethernodes.org
2. **Data Processing**: IPGeolocation API for location data
3. **Database Management**: Neo4j for storing nodes and relationships
4. **Visualization**: Interactive maps and graph structures
5. **API Development**: RESTful endpoints for frontend integration

## Screenshots

![Map View 1](https://3d55oj3b54lkqnmudprnnq3i7yue3vavavmx3gdwbi3dttpbhm2q.arweave.net/2PvXJ2HvFqg1lBvi1sNo_ihN1BUFWX2Ydgo2Oc3hOzU)
![Map View 2](https://cmcyws4nvvczl6lr7g7p655fsf26pmsybffcnmlz2ppepppocexa.arweave.net/EwWLS42tRZX5cfm-_3elkXXnslgJSiaxedPeR73uES4)
![Graph View](https://github.com/mulosbron/EthNodeMap/assets/91866065/627157dd-71fd-43ee-9282-1e7040110b79)
