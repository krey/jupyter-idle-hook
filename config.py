import datetime

timeout = datetime.timedelta(seconds=1*60)
polling_interval = datetime.timedelta(seconds=30)

def idle_hook():
    print('hi')
