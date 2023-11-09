import csv
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from sensor_msgs.msg import NavSatFix

def bag_to_csv(bagfile, csvfile):
    reader = rosbag2_py.SequentialReader()

    storage_options = rosbag2_py.StorageOptions(uri=bagfile, storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions(input_serialization_format="cdr",
                                                    output_serialization_format="cdr")

    reader.open(storage_options, converter_options)

    topics_and_types = reader.get_all_topics_and_types()

    # Create a dictionary mapping topic names to types
    topic_types = {topic_metadata.name: topic_metadata.type for topic_metadata in topics_and_types}

    with open(csvfile, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["stamp", "topic", "latitude", "longitude", "altitude"])  # write the header row
        while reader.has_next():
            (topic, data, t) = reader.read_next()
            msg_type = topic_types[topic]
            msg = deserialize_message(data, get_message(msg_type))
            stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            writer.writerow([stamp, topic, msg.latitude, msg.longitude, msg.altitude])

def main():
    bag_to_csv('/root/path03-2/', 'output.csv')

if __name__ == '__main__':
    main()