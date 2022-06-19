import json
import sys
import constant


def read_instance(filepath):
    try:
        with open(filepath, 'r') as file:
            instance_data = json.load(file)

        return instance_data
    except:
        print('Error while reading instance')
        return None


def get_file_path(instance=None):
    file = instance if instance is not None else (sys.argv[1] if len(sys.argv) > 1 else constant.DEFAULT_INSTANCE)
    return f'../{constant.INSTANCE_PATH}/{file}.{constant.INSTANCE_EXTENSION}'


def intersect(list1, list2):
    return list(set(list1) & set(list2))


def get_room_by_name(room_name, rooms):
    return list(filter(lambda r: r['Room'] == room_name, rooms))[0]
