# Basic Script for determining activity in topics

Just a basic example for easy checking the activity in a list of topics with a certain prefix.

- [Basic Script for determining activity in topics](#basic-script-for-determining-activity-in-topics)
  - [Disclaimer](#disclaimer)
  - [Setup](#setup)
    - [Start Docker Compose](#start-docker-compose)
    - [Connect](#connect)
    - [Create topics](#create-topics)
    - [Create Connectors](#create-connectors)
    - [Check Control Center](#check-control-center)
    - [Run our script](#run-our-script)
  - [Cleanup](#cleanup)

## Disclaimer

The code and/or instructions here available are **NOT** intended for production usage. 
It's only meant to serve as an example or reference and does not replace the need to follow actual and official documentation of referenced products.

## Setup

### Start Docker Compose

```bash
docker compose up -d
```

### Connect

If you already have the plugin folders you can jump to next step.

You can check the connector plugins available by executing:

```bash
curl localhost:8083/connector-plugins | jq
```

As you see we only have source connectors:

```text
[
  {
    "class": "org.apache.kafka.connect.mirror.MirrorCheckpointConnector",
    "type": "source",
    "version": "7.6.0-ce"
  },
  {
    "class": "org.apache.kafka.connect.mirror.MirrorHeartbeatConnector",
    "type": "source",
    "version": "7.6.0-ce"
  },
  {
    "class": "org.apache.kafka.connect.mirror.MirrorSourceConnector",
    "type": "source",
    "version": "7.6.0-ce"
  }
]
```

Let's install confluentinc/kafka-connect-datagen connector plugin for sink.

```shell
docker compose exec connect confluent-hub install --no-prompt confluentinc/kafka-connect-datagen:latest
```

Restart connect:

```shell
docker compose restart connect
```

Now if we list our plugins again we should see new one corresponding to the Datagen connector.

### Create topics 

Let's create first our topics with two partitions each:

```shell
kafka-topics --bootstrap-server localhost:9091 --topic prfx-customers --create --partitions 2 --replication-factor 1
kafka-topics --bootstrap-server localhost:9091 --topic prfx-orders --create --partitions 2 --replication-factor 1
```

### Create Connectors

Let's create our source connectors using datagen:

```bash
curl -i -X PUT -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/my-datagen-source2/config -d '{
    "name" : "my-datagen-source2",
    "connector.class": "io.confluent.kafka.connect.datagen.DatagenConnector",
    "kafka.topic" : "prfx-customers",
    "output.data.format" : "AVRO",
    "quickstart" : "SHOE_CUSTOMERS",
    "tasks.max" : "1"
}'
curl -i -X PUT -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/my-datagen-source3/config -d '{
    "name" : "my-datagen-source3",
    "connector.class": "io.confluent.kafka.connect.datagen.DatagenConnector",
    "kafka.topic" : "prfx-orders",
    "output.data.format" : "AVRO",
    "quickstart" : "SHOE_ORDERS",
    "tasks.max" : "1"
}'
```

### Check Control Center

Open http://localhost:9021 and check cluster is healthy including Kafka Connect.

### Run our script

We can now execute our script:

```shell
python3 check-topic-activity.py
```

- Let it run a couple of iterations and see the increase each last minute.
- The stop one of the connectors and see how increase reduces.
- Stop the other connector and check it reduces more.
- Let it run a couple of iterations with zero increase.
- Start connectors back and confirm increase is measured.

You should see something like:

```
Sleeping for 60 seconds
Total offset increase in last minute - iteration 1: 508
Total offset increase in last minute - iteration 2: 502
Total offset increase in last minute - iteration 3: 311
Total offset increase in last minute - iteration 4: 32
Total offset increase in last minute - iteration 5: 0
Total offset increase in last minute - iteration 6: 0
Total offset increase in last minute - iteration 7: 430
Total offset increase in last minute - iteration 8: 520
```

## Cleanup

```bash
docker compose down -v
```