# EthNodeMap

EthNodeMap, Ethereum düğümlerinin bilgilerini Neo4j veritabanında yönetmek ve bu bilgileri çeşitli uç noktalardan sunmak için geliştirilmiş bir projedir. Bu proje, bir Flask API ve bu API'den elde edilen verileri görselleştirmek için bir frontend uygulaması içerir. Kullanıcılar, düğümlerin coğrafi konum bilgilerini, istemci türlerini, işletim sistemlerini ve daha fazlasını sorgulayabilir ve görselleştirebilir.


## ÖZELLİKLER

- **Düğüm Filtreleme ve Görüntüleme:** Kullanıcılar, harita üzerinde görüntüledikleri Ethereum düğümlerini ülke, işletim sistemi (OS), internet servis sağlayıcı (ISP) ve istemci türüne göre filtreleyebilirler. Ayrıca harita üzerinde üzerine tıkladıkları düğümlerin verilerini haritanın altında görüntüleyebilirler.
- **İstatistik Tabloları:** Haritanın sağında bulunan istatistik tablosunda çeşitli özelliklere göre düğümlerin dağılımını görebilirsiniz.
- **Dinamik Veriler:** Haritanın solunda bulunan alanda yeni eklenen düğümleri ve bazı bilgileri (bkz. toplam düğüm sayısı) görüntüleyebiliriz.
- **Graf Görünümü:** Graf görünümü butonuna basarak, seçilen ülke veya ülkelerin ağaç graf yapısını D3.js sayesinde görselleştirebilirsiniz.


## KURULUM

### Gereksinimler

- Python 3.7+
- HTML, CSS ve JavaScript
- Flask: Web sunucusu ve API'yi oluşturmak için.
- Flask-CORS: API'ye çapraz kaynak isteği (CORS) desteği eklemek için.
- Neo4j: Düğümleri depolayıp, ilişkiler kurmak için.
- BeautifulSoup4: Etherscan sitesinden düğüm verilerini çekmek için.
- Requests: HTTP istekleri yapmak için.
- D3.js (frontend): Grafı görselleştirmek için.
- Leaflet.js (frontend): Harita üzerinde düğümlerin konumunu göstermek için.

### Yükleme

1. Python bağımlılıklarını yükleyin:

```
pip install flask flask-cors neo4j beautifulsoup4 requests
```

2. Neo4j veritabanını çalıştırın ve aşağıdaki gibi yapılandırın:

```
neo4j start
```

### Ortam Değişkenleri

- `API_KEY`: IP coğrafi konum bilgileri için gerekli olan ipgeolocation API anahtarı.
- `NEO4J_URI`: Neo4j veritabanı URI'si (örneğin, `bolt://localhost:7687`).
- `NEO4J_USERNAME`: Neo4j kullanıcı adı.
- `NEO4J_PASSWORD`: Neo4j parolası.


## BACKEND

### API Uç Noktaları

- `/get-nodes`: Tüm düğümleri listele (Özellikleri ile birlikte).
- `/get-os-types`: Tüm benzersiz işletim sistemi türlerini listele.
- `/get-client-types`: Tüm benzersiz istemci türlerini listele.
- `/get-countries`: Tüm benzersiz ülkeleri listele.
- `/get-isps`: Tüm benzersiz internet servis sağlayıcılarını listele.
- `/get-node-ids`: Tüm benzersiz düğüm id'lerini listele.
- `/get-node-count`: Toplam düğüm sayısını al.
- `/get-node-details/<node_id>`: Belirli bir düğümün detaylarını al.
- `/get-latest-nodes`: En son eklenen düğümleri listele.
- `/nodes/<country_name>`: Belirli bir ülkedeki düğüm ilişkilerini al.
- `/get-statistics/<data_type>`: Belirtilen veri türü için istatistikleri al (os, client, isp, country).

### Çalıştırma

Uygulamayı başlatmak için aşağıdaki komutu kullanın:

```
python3 api.py
```

Local API, `http://127.0.0.1:5001` adresinde çalışacaktır.
Server API, `http://0.0.0.0:5001` adresinde çalışacaktır.

### Veri Toplama ve Güncelleme

#### Düğüm Verilerini Toplama

`fetch-nodes.py` dosyasını çalıştırarak Ethereum düğümlerini toplayabilir ve Neo4j veritabanına ekleyebilirsiniz:

```
python3 fetch-nodes.py
```

#### Düğüm Uptime Bilgisini Elde Etme

`fetch-status.py` dosyasını çalıştırarak düğüm durumlarını kontrol edebilir ve güncelleyebilirsiniz:

```
python3 fetch-status.py
```

#### İlişkileri İçe Aktarma

Düğüm ilişkilerini içe aktarmak için `import-relationships.py` dosyasını çalıştırın (fetch-status.py ve fetch-nodes.py dosyalarının içinde otomatik olarak çalışıyor):

```
python3 import-relationships.py
```


## FRONTEND

### Harita Görünümü

`index.html` dosyası, düğümleri Leaflet.js kullanarak dünya haritası üzerinde görüntülemek için kullanılır.

![index1](https://fdateevmw3puhezrzfmigsrc5ggu57r5odqlbhp6hbts76s3ii2a.arweave.net/KMEyEqy230OTMclYg0oi6Y1O_j1w4LCd_jhnL_pbQjQ)

![index2](https://5tlga24bfiqfuclhvaawurv73wnfdp6fh6xjkkg36w2xwam5xvaq.arweave.net/7NZga4EqIFoJZ6gBaka_3ZpRv8U_rpUo2_W1ewGdvUE)

### Ağaç Graf Görünümü

`graph.html` dosyası, düğümleri ve ilişkilerini D3.js kullanarak grafiksel olarak görüntülemek için kullanılır.

![graph](https://pz5mwdpog4cvbr55zslx5qumt5lu5xtjpblwcsrtpot2iu35unda.arweave.net/fnrLDe43BVDHvcyXfsKMn1dO3ml4V2FKM3unpFN9o0Y)

## DATABASE

![neo4j](https://svmn7f4pypvd5ablmcsngbx6bpjkbwsnmowirqa6juqcgpoielna.arweave.net/lVjfl4_D6j6AK2Ck0wb-C9Kg2k1jrIjAHk0gIz3IIto)

![neo4j2](https://paiqpil3yor2scueyboeeavx5ndnqvt3e7nm47s56lglxb7nqloq.arweave.net/eBEHoXvDo6kKhMBcQgK360bYVnsn2s5-XfLMu4ftgt0)

BeautifulSoup4 kullanılarak Etherscan sitesinden çekilen örnek bir düğüm yapısı:

```
client: Nethermind
host: 89.58.47.72
id: ec68c46aa0874badc8f9c02e68af8bae3a3f94027124f27c9bca02f7bf83ee700083602b91cf5781985bcb48d5ce7e2af144fcaa340f4adc8ae82117d651a393
os: linux-arm64
port: 30303
```

`fetch-nodes.py` betiği kullanılarak IPGeolocation API uç noktasına yollanan 'host' bilgisinin geri döndürdüğü bilgiler ile birlikte veri tabanına eklenen örnek bir düğüm yapısı:  

```
<elementId>: 4:574bd6e8-3b31-4b0f-ae15-03f2f836b8ff:658
<id>: 658
client: Nethermind
country_name: Germany
created_at: 2024-05-25T20:35:15.918528
host: 89.58.47.72
id: ec68c46aa0874badc8f9c02e68af8bae3a3f94027124f27c9bca02f7bf83ee700083602b91cf5781985bcb48d5ce7e2af144fcaa340f4adc8ae82117d651a393
isp: netcup GmbH
latitude: 49.45434
longitude: 11.07349
os: linux-arm64
port: 30303
status: 1
```

### Countries kök düğümünü oluşturma:

```
CREATE (root:Root {name: 'Countries'})
```

### Düğümlerden ülke bilgilerini çekip kök düğüme bağlı ülke düğümlerini yaratma::

```
MATCH (n) 
WITH DISTINCT n.country_name AS country_name 
CREATE (c:Country {name: country_name}) 
WITH c
MATCH (root:Root {name: 'Countries'}) 
MERGE (root)-[:HAS_COUNTRY]->(c)
```

### Her ülkeye bağlı ISP düğümlerini yaratma:

```
MATCH (c:Country)
UNWIND ['Contabo', 'AWS', 'Azure', 'Google', 'Alibaba', 'Oracle', 'IBM', 'Tencent', 'OVHCloud', 'DO', 'Linode', 'Salesforce', 'Huawei', 'Dell', 'Vultr', 'Heroku', 'Hetzner', 'Scaleway', 'Upcloud', 'Kamatera', 'Others'] AS isp_name
CREATE (isp:ISP {name: isp_name})
MERGE (c)-[:HAS_ISP]->(isp)
```

### Her ISP'ye bağlı OS düğümlerini yaratma:

```
MATCH (isp:ISP)
UNWIND ['Linux', 'Windows', 'MacOS', 'Android', 'FreeBSD', 'Darwin', 'Others'] AS os_name
CREATE (os:OS {name: os_name})
MERGE (isp)-[:HAS_OS]->(os)
```

### Her OS'a bağlı client düğümlerini yaratma:

```
MATCH (os:OS)
UNWIND ['Geth', 'Nethermind', 'Besu', 'Erigon', 'Reth', 'EthereumJS', 'Others'] AS client_name
CREATE (client:Client {name: client_name})
MERGE (os)-[:HAS_CLIENT]->(client)
```

### Düğümleri Bağlama:

```
MATCH (n:Node)
WITH n,
     COALESCE(n.country_name, 'Others') AS country_name,
     CASE
       WHEN toLower(n.isp) CONTAINS 'contabo' THEN 'Contabo'
       WHEN toLower(n.isp) CONTAINS 'aws' THEN 'AWS'
       WHEN toLower(n.isp) CONTAINS 'azure' THEN 'Azure'
       WHEN toLower(n.isp) CONTAINS 'google' THEN 'Google'
       WHEN toLower(n.isp) CONTAINS 'alibaba' THEN 'Alibaba'
       WHEN toLower(n.isp) CONTAINS 'oracle' THEN 'Oracle'
       WHEN toLower(n.isp) CONTAINS 'ibm' THEN 'IBM'
       WHEN toLower(n.isp) CONTAINS 'tencent' THEN 'Tencent'
       WHEN toLower(n.isp) CONTAINS 'ovhcloud' THEN 'OVHCloud'
       WHEN toLower(n.isp) CONTAINS 'do' THEN 'DO'
       WHEN toLower(n.isp) CONTAINS 'linode' THEN 'Linode'
       WHEN toLower(n.isp) CONTAINS 'salesforce' THEN 'Salesforce'
       WHEN toLower(n.isp) CONTAINS 'huawei' THEN 'Huawei'
       WHEN toLower(n.isp) CONTAINS 'dell' THEN 'Dell'
       WHEN toLower(n.isp) CONTAINS 'vultr' THEN 'Vultr'
       WHEN toLower(n.isp) CONTAINS 'heroku' THEN 'Heroku'
       WHEN toLower(n.isp) CONTAINS 'hetzner' THEN 'Hetzner'
       WHEN toLower(n.isp) CONTAINS 'scaleway' THEN 'Scaleway'
       WHEN toLower(n.isp) CONTAINS 'upcloud' THEN 'Upcloud'
       WHEN toLower(n.isp) CONTAINS 'kamatera' THEN 'Kamatera'
       ELSE 'Others'
     END AS isp_name,
     CASE
       WHEN toLower(n.os) CONTAINS 'linux' THEN 'Linux'
       WHEN toLower(n.os) CONTAINS 'windows' THEN 'Windows'
       WHEN toLower(n.os) CONTAINS 'macos' THEN 'MacOS'
       WHEN toLower(n.os) CONTAINS 'android' THEN 'Android'
       WHEN toLower(n.os) CONTAINS 'freebsd' THEN 'FreeBSD'
       WHEN toLower(n.os) CONTAINS 'darwin' THEN 'Darwin'
       ELSE 'Others'
     END AS os_name,
     CASE
       WHEN toLower(n.client) CONTAINS 'geth' THEN 'Geth'
       WHEN toLower(n.client) CONTAINS 'nethermind' THEN 'Nethermind'
       WHEN toLower(n.client) CONTAINS 'besu' THEN 'Besu'
       WHEN toLower(n.client) CONTAINS 'erigon' THEN 'Erigon'
       WHEN toLower(n.client) CONTAINS 'reth' THEN 'Reth'
       WHEN toLower(n.client) CONTAINS 'ethereumjs' THEN 'EthereumJS'
       ELSE 'Others'
     END AS client_name
MATCH (root:Root {name: 'Countries'})
MERGE (country:Country {name: country_name})<-[:HAS_COUNTRY]-(root)
MERGE (country)-[:HAS_ISP]->(isp:ISP {name: isp_name})
MERGE (isp)-[:HAS_OS]->(os:OS {name: os_name})
MERGE (os)-[:HAS_CLIENT]->(client:Client {name: client_name})
MERGE (client)-[:HAS_NODE]->(n)
```

### Belirli Bir Ülkeye Bağlı Düğümleri Görselleştirme:

```
MATCH (root:Root {name: 'Countries'})-[:HAS_COUNTRY]->(c:Country)-[:HAS_ISP]->(isp:ISP)-[:HAS_OS]->(os:OS)-[:HAS_CLIENT]->(client:Client)-[:HAS_NODE]->(n:Node {country_name : "Croatia"})
RETURN root, c, isp, os, client, n
```

### Tüm İlişkileri Silme:

```
MATCH ()-[r]->()
DELETE r
```

### Kök, Ülke, ISP, OS ve Client Düğümlerini Silme:

```
MATCH (n:Root) DELETE n
MATCH (n:Country) DELETE n
MATCH (n:ISP) DELETE n
MATCH (n:OS) DELETE n
MATCH (n:Client) DELETE n
```


## KAYNAKÇA

### Programlama Dilleri

- **Python:** [https://www.python.org/](https://www.python.org/)
- **JavaScript:** [https://developer.mozilla.org/en-US/docs/Web/JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- **HTML:** [https://developer.mozilla.org/en-US/docs/Web/HTML](https://developer.mozilla.org/en-US/docs/Web/HTML)
- **CSS:** [https://developer.mozilla.org/en-US/docs/Web/CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)

### Kütüphaneler

- **Flask:** https://flask.palletsprojects.com/
- **Flask-CORS:** [https://flask-cors.readthedocs.io/en/latest/](https://flask-cors.readthedocs.io/en/latest/)
- **Neo4j:** [https://neo4j.com/](https://neo4j.com/)
- **BeautifulSoup4:** https://www.crummy.com/software/BeautifulSoup/
- **Requests:** https://docs.python-requests.org/en/latest/
- **D3.js:** [https://d3js.org/](https://d3js.org/)
- **Leaflet.js:** [https://leafletjs.com/](https://leafletjs.com/)

### API ve Diğer Kaynaklar

- **Etherscan:** https://etherscan.io/nodetracker/nodes
- **IPGeolocation API:** https://ipgeolocation.io/documentation/ip-geolocation-api.html