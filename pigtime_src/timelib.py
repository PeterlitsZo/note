import datetime
def long_time():
    """ from year to microsenced """
    return str(datetime.datetime.now())

def short_time():
    """ from year to day """
    return str(datetime.date.today())