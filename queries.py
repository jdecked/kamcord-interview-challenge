from csv_parser import parse_csv_data
from models import Query

users = parse_csv_data('data.csv')

over_september = Query().retention_query(users, start_date="2014-09-01", end_date="2014-09-30")
september8_10_android = Query().retention_query(users, start_date="2014-09-08", end_date="2014-09-10", filter=True, os_name="android")
# TODO: filter over_september query after first making...
over_september_ios_175 = Query().retention_query(users, start_date="2014-09-01", end_date="2014-09-30", filter=True, os_name="IOS", sdk_version="1.7.5")

print "Day­7 UI Retention over the month of September: %s" % (over_september.retention_rate)
print "Day­7 UI Retention from September 8 through September 10 for the Android SDK: %s" % (september8_10_android.retention_rate)
print "Day­7 UI Retention over the month of September for version 1.7.5 of the iOS SDK: %s" % (over_september_ios_175.retention_rate)
