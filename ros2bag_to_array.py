import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from std_msgs.msg import String

def bag_to_array(bagfile):
    reader = rosbag2_py.SequentialReader()

    storage_options = rosbag2_py.StorageOptions(uri=bagfile, storage_id="sqlite3")
    converter_options = rosbag2_py.ConverterOptions(input_serialization_format="cdr",
                                                    output_serialization_format="cdr")

    reader.open(storage_options, converter_options)

    topics_and_types = reader.get_all_topics_and_types()

    # Create a dictionary mapping topic names to types
    topic_types = {topic_metadata.name: topic_metadata.type for topic_metadata in topics_and_types}

    output_data = []
    while reader.has_next():
        (topic, data, t) = reader.read_next()
        msg_type = topic_types[topic]
        msg = deserialize_message(data, get_message(msg_type))
        # print(msg)
        output_data.append(msg)

    return output_data

def main():
    messages = bag_to_array('/root/path03-2/')
    print(messages[0])
    print(messages[0].latitude)
    print(messages[0].longitude)
    print(messages[0].altitude)

if __name__ == '__main__':
    main()