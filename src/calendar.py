import datetime

def get_date_time():
     now = datetime.datetime.now()
     return now.strftime("%d %B %Y, %I:%M:%S %p")