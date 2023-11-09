import csv
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

def extract_fields(msg, prefix=''):
    fields = {}
    for attr in dir(msg):
        if not attr.startswith('_'):
            value = getattr(msg, attr)
            if hasattr(value, '__slots__'):
                fields.update(extract_fields(value, prefix=f'{prefix}{attr}.'))
            else:
                fields[f'{prefix}{attr}'] = value
    return fields

def bag_to_csv(bagfile, output_dir):
    reader = rosbag2_py.SequentialReader()

    storage_options = rosbag2_py.StorageOptions(uri=bagfile, storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions(input_serialization_format="cdr",
                                                    output_serialization_format="cdr")

    reader.open(storage_options, converter_options)

    topics_and_types = reader.get_all_topics_and_types()

    # Create a dictionary mapping topic names to types
    topic_types = {topic_metadata.name: topic_metadata.type for topic_metadata in topics_and_types}

    # Create a CSV writer for each type
    writers = {}
    for topic, msg_type in topic_types.items():
        csvfile = f"{output_dir}/{topic.replace('/', '_')}.csv"
        file = open(csvfile, 'w', newline='')
        writer = csv.writer(file)
        writer.writerow(["stamp", "topic"] + sorted(extract_fields(get_message(msg_type)())))
        writers[topic] = (file, writer)

    while reader.has_next():
        (topic, data, t) = reader.read_next()
        msg_type = topic_types[topic]
        msg = deserialize_message(data, get_message(msg_type))
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        fields = extract_fields(msg)
        writers[topic][1].writerow([stamp, topic] + [fields[key] for key in sorted(fields)])

    # Close all the files
    for file, writer in writers.values():
        file.close()

def main():
    bag_to_csv('/root/path03-2/', '/root/ros2bag_to_array/output/')

if __name__ == '__main__':
    main()