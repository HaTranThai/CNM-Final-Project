#!/bin/bash
# Create Kafka topics for ECG CDSS
KAFKA_BROKER=${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}

echo "Creating Kafka topics..."

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER \
  --topic ecg_raw --partitions 3 --replication-factor 1

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER \
  --topic ecg_beat_event --partitions 3 --replication-factor 1

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER \
  --topic ecg_waveform --partitions 3 --replication-factor 1

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER \
  --topic ecg_beat_ready --partitions 3 --replication-factor 1

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER \
  --topic ecg_pred_beat --partitions 3 --replication-factor 1

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER \
  --topic ecg_alert --partitions 1 --replication-factor 1

echo "All topics created."
kafka-topics --list --bootstrap-server $KAFKA_BROKER
