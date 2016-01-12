import csv

from models import create, Query, User

def parse_csv_data(filename):
    with open(filename, 'r') as csvfile:
        data = list(csv.reader(csvfile))[1:]
        users = {}

        for datum in data:
            event_count = datum[1]
            event_name = datum[2]
            event_time = datum[3]
            user_id = datum[-1]

            if user_id in users.keys():
                users[user_id].add_event(event_count, event_name, event_time)
            else:
                new_user = create(User, event_count, event_name, event_time, user_id=user_id, sdk_version=datum[-2], os_name=datum[-3])
                users[user_id] = new_user

    return users
