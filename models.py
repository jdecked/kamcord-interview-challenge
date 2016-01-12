import operator

from time import strptime, mktime
from datetime import date, timedelta
from math import floor

DEFAULT_RETENTION_DAYS = 7
POSSIBLE_RETENTION_TYPES = {
    "UI": "UI_OPEN_COUNT",
    "VIDEO": "VIDEO_VIEW_COUNT"
}
DATE_FORMAT = "%Y-%m-%d"

class Base(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def create(obj_type, *args, **kwargs):
    return obj_type(*args, **kwargs)

class User(Base):
    def __init__(self, event_count, event_name, event_time, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.events = []
        self.add_event(event_count, event_name, event_time)

    def add_event(self, event_count, event_name, event_time):
        new_event = create(Event, event_count=event_count, event_name=event_name, event_time=event_time)
        self.events.append(new_event)

    def __repr__(self):
        return "User(user_id=%r)" % self.user_id

class Event(Base):
    def __repr__(self):
        return "Event(event_count=%r, event_name=%r, event_time=%r)" % (self.event_count, self.event_name, self.event_time)

class Query(Base):
    def single_select_query(self, query_set, **criterion):
        """
        - Returns the first instance of an object whose attributes meet the criterion given as a keyword argument
        - query_set is a double-ended queue of any object type, where all objects in the deque are the same type
        """

        self.result = None
        criterion_name = criterion.keys()[0]
        criterion_value = criterion.values()[0]

        while len(query_set) > 1:
            if getattr(query_set[len(query_set)/2], criterion_name) < criterion_value:
                return self.single_select_query(query_set[len(query_set)/2:], **criterion)

            elif getattr(query_set[len(query_set)/2], criterion_name) > criterion_value:
                return self.single_select_query(query_set[:len(query_set)/2], **criterion)

            else:
                self.result = query_set[len(query_set)/2]
                break

        if len(query_set) == 1:
            if getattr(query_set[0], criterion_name) == criterion_value:
                return query_set[0]

        return result

    def exact_filter(self, **kwargs):
        self.filtered_results = []

        for result in self.results:
            for kwarg in kwargs:
                try:
                    if getattr(result, kwarg) == kwargs[kwarg]:
                        self.filtered_results.append(result)
                except:
                    continue

        return self.filtered_results

    def retention_query(self, query_set, retention_type=POSSIBLE_RETENTION_TYPES["UI"], days=DEFAULT_RETENTION_DAYS, filter=False, **criteria):
        """
        - Returns retention rate for event_name specified as retention_type, over specified number of days, between start_date and end_date given as kwargs,
          formatted as a string with a percentage
        - Also returns retained users
        - query_set is expected to be a hash table (dict) of User objects
        """

        self.results = []

        start_date = date.fromtimestamp(mktime(strptime(criteria['start_date'], DATE_FORMAT)))
        end_date = date.fromtimestamp(mktime(strptime(criteria.get('end_date', criteria['start_date']), DATE_FORMAT)))

        delta = end_date - start_date
        included_dates_retained = (start_date + timedelta(days=i) for i in range(delta.days + 1))
        included_dates_possible = (start_date + timedelta(days=i) for i in range(delta.days + 1))

        retained_user_counts = {date: 0 for date in included_dates_retained}
        possible_user_counts = {date: 0 for date in included_dates_possible}

        if filter:
            self.results = query_set.values()
            users = self.exact_filter(**criteria)
            self.results = []
        else:
            users = query_set.values()

        for user in users:
            event_dates = []

            for event in user.events:
                event_date = date.fromtimestamp(mktime(strptime(event.event_time[:10], DATE_FORMAT)))

                if (event_date >= start_date) and (event_date <= end_date + timedelta(days=days)):
                    if event.event_name == retention_type:
                        event_dates.append(event_date)

                        if event_date <= end_date:
                            possible_user_counts[event_date] += 1

            if len(event_dates) > 1:
                first_event = min(event_dates)
                target_date = first_event + timedelta(days=days)

                if target_date in event_dates:
                    retained_user_counts[first_event] += 1
                    self.results.append(user)

        self.retention_rate = (sum(retained_user_counts.values()) / float(sum(possible_user_counts.values()))) * 100
        self.retention_rate = str(self.retention_rate) + "%"

        return self
