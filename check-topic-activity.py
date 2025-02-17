import subprocess
import time

# Kafka settings
KAFKA_BROKER = "localhost:9091"
TOPIC_PREFIX = "prfx-"  # Set your desired topic prefix
POLL_INTERVAL = 60  # Polling interval in seconds

def get_topics_with_prefix(prefix):
    """Fetch all Kafka topics and filter by prefix."""
    cmd = f"kafka-topics --bootstrap-server {KAFKA_BROKER} --list"
    topics = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.splitlines()
    return [topic for topic in topics if topic.startswith(prefix)]

def get_latest_offsets(topic):
    """Fetch latest offsets for all partitions of a given topic."""
    cmd = f"kafka-run-class org.apache.kafka.tools.GetOffsetShell --broker-list {KAFKA_BROKER} --topic {topic}"
    output = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
    
    offsets = {}
    for line in output.splitlines():
        parts = line.split(":")
        if len(parts) == 3:
            partition, offset = int(parts[1]), int(parts[2])
            offsets[partition] = offset
    return offsets

def main():
    previous_offsets = {}
    i = 0

    while True:
        topics = get_topics_with_prefix(TOPIC_PREFIX)
        total_increase = 0

        current_offsets = {}
        for topic in topics:
            offsets = get_latest_offsets(topic)
            current_offsets[topic] = offsets
            # Calculate offset increase
            if topic in previous_offsets:
                for partition, offset in offsets.items():
                    prev_offset = previous_offsets[topic].get(partition, 0)
                    total_increase += max(0, offset - prev_offset)
        if(i == 0):
            print(f"Sleeping for {POLL_INTERVAL} seconds")
        else:        
            print(f"Total offset increase in last minute - iteration {i}: {total_increase}")
        i+=1
        # Store current offsets for next iteration
        previous_offsets = current_offsets.copy()

        # Wait for the next interval
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
