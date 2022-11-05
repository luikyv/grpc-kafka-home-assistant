# Compile Protobuf
python -m grpc_tools.protoc -I ./src/protos  --python_out=./src/protos --grpc_python_out=./src/protos home.proto

# Run Kafka container
docker-compose -f ./kafka-stack-docker-compose-master/zk-single-kafka-single.yml up

# Set up Kafka topics
python kafka_setup.py
