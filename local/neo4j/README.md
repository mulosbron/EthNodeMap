
### Creating the root node of the World:

```
CREATE (root:Root {name: 'World'})
```

### Fetching country information from nodes and creating country nodes linked to the root node:

```
MATCH (n)
WITH DISTINCT n.country_name AS country_name
CREATE (c:Country {name: country_name})
WITH c
MATCH (root:Root {name: 'World'})
MERGE (root)-[:HAS_COUNTRY]->(c)
```

### Creating ISP nodes linked to each country:

```
MATCH (c:Country)
UNWIND ['Contabo', 'AWS', 'Azure', 'Google', 'Alibaba', 'Oracle', 'IBM', 'Tencent', 'OVHCloud', 'DigitalOcean', 'Linode', 'Salesforce', 'Huawei', 'Dell', 'Vultr', 'Heroku', 'Hetzner', 'Scaleway', 'Upcloud', 'Kamatera', "Other ISPs"] AS isp_name
CREATE (isp:ISP {name: isp_name})
MERGE (c)-[:HAS_ISP]->(isp)
```

### Creating OS nodes linked to each ISP:

```
MATCH (isp:ISP)
UNWIND ['Linux', 'Windows', 'MacOS', "Other OSs"] AS os_name
CREATE (os:OS {name: os_name})
MERGE (isp)-[:HAS_OS]->(os)
```

### Creating client nodes linked to each OS:

```
MATCH (os:OS)
UNWIND ['Geth', 'Nethermind', 'Besu', 'Erigon', 'Reth', 'EthereumJS', 'Other Clients'] AS client_name
CREATE (client:Client {name: client_name})
MERGE (os)-[:HAS_CLIENT]->(client)
```

### Linking Nodes:

```
MATCH (n:Node)
WITH n,
    COALESCE(n.country_name) AS country_name,
    CASE
        WHEN toLower(n.isp) CONTAINS 'contabo' THEN 'Contabo'
        WHEN toLower(n.isp) CONTAINS 'aws' OR toLower(n.isp) CONTAINS 'amazon' THEN 'AWS'
        WHEN toLower(n.isp) CONTAINS 'azure' OR toLower(n.isp) CONTAINS 'microsoft' THEN 'Azure'
        WHEN toLower(n.isp) CONTAINS 'google' THEN 'Google'
        WHEN toLower(n.isp) CONTAINS 'alibaba' THEN 'Alibaba'
        WHEN toLower(n.isp) CONTAINS 'oracle' THEN 'Oracle'
        WHEN toLower(n.isp) CONTAINS 'ibm' THEN 'IBM'
        WHEN toLower(n.isp) CONTAINS 'tencent' THEN 'Tencent'
        WHEN toLower(n.isp) CONTAINS 'ovh' THEN 'OVHCloud'
        WHEN toLower(n.isp) CONTAINS 'digitalocean' THEN 'DigitalOcean'
        WHEN toLower(n.isp) CONTAINS 'linode' OR toLower(n.isp) CONTAINS 'akamai' THEN 'Linode'
        WHEN toLower(n.isp) CONTAINS 'akamai' THEN 'Linode'
        WHEN toLower(n.isp) CONTAINS 'salesforce' THEN 'Salesforce'
        WHEN toLower(n.isp) CONTAINS 'huawei' AND toLower(n.isp) CONTAINS 'cloud' THEN 'Huawei'
        WHEN toLower(n.isp) CONTAINS 'dell' AND toLower(n.isp) CONTAINS 'cloud' THEN 'Dell'
        WHEN toLower(n.isp) CONTAINS 'vultr' THEN 'Vultr'
        WHEN toLower(n.isp) CONTAINS 'heroku' THEN 'Heroku'
        WHEN toLower(n.isp) CONTAINS 'hetzner' THEN 'Hetzner'
        WHEN toLower(n.isp) CONTAINS 'scaleway' THEN 'Scaleway'
        WHEN toLower(n.isp) CONTAINS 'upcloud' THEN 'Upcloud'
        WHEN toLower(n.isp) CONTAINS 'kamatera' THEN 'Kamatera'
        ELSE "Other ISPs"
    END AS isp_name,
    CASE
        WHEN toLower(n.os) CONTAINS 'linux' THEN 'Linux'
        WHEN toLower(n.os) CONTAINS 'windows' THEN 'Windows'
        WHEN toLower(n.os) CONTAINS 'macos' THEN 'MacOS'
        ELSE "Other OSs"
    END AS os_name,
    CASE
        WHEN toLower(n.client) CONTAINS 'geth' THEN 'Geth'
        WHEN toLower(n.client) CONTAINS 'nethermind' THEN 'Nethermind'
        WHEN toLower(n.client) CONTAINS 'besu' THEN 'Besu'
        WHEN toLower(n.client) CONTAINS 'erigon' THEN 'Erigon'
        WHEN toLower(n.client) CONTAINS 'reth' THEN 'Reth'
        WHEN toLower(n.client) CONTAINS 'ethereumjs' THEN 'EthereumJS'
        ELSE 'Other Clients'
    END AS client_name
MATCH (root:Root {name: 'World'})
MERGE (country:Country {name: country_name})<-[:HAS_COUNTRY]-(root)
MERGE (country)-[:HAS_ISP]->(isp:ISP {name: isp_name})
MERGE (isp)-[:HAS_OS]->(os:OS {name: os_name})
MERGE (os)-[:HAS_CLIENT]->(client:Client {name: client_name})
MERGE (client)-[:HAS_NODE]->(n)
```

### Visualizing Nodes Linked to a Specific Country:

```
MATCH (root:Root)-[:HAS_COUNTRY]->(c:Country)-[:HAS_ISP]->(isp:ISP)-[:HAS_OS]->(os:OS)-[:HAS_CLIENT]->(client:Client)-[:HAS_NODE]->(n:Node {country_name : "Croatia"})
RETURN root, c, isp, os, client, n
```

### Deleting All Relationships:

```
MATCH ()-[r]->()
DELETE r
```

### Deleting Root, Country, ISP, OS, and Client Nodes:

```
MATCH (n:Root) DELETE n
MATCH (n:Country) DELETE n
MATCH (n:ISP) DELETE n
MATCH (n:OS) DELETE n
MATCH (n:Client) DELETE n
```
