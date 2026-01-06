1. 在src/influxdb.py中实现influxdb的连接和数据写入
2. INFLUXDB_URL=<http://localhost:8086> INFLUXDB_TOKEN=my-token INFLUXDB_ORG=my-org
INFLUXDB_BUCKET=battery_data 这是基本信息。
3. 按照项目里fastapi 的配置方式，配置influxdb的连接信息。
4. 在src/influxdb.py中实现数据写入的接口，数据写入的接口需要接收
5. influxdb我刚建好，需不要建表字段，你可以模拟一张表数据。模拟写入数据。
