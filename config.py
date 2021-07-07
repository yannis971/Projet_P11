import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# To generate a secret key :
# >>> import random, string
# >>> "".join([random.choice(string.printable) for _ in range(24)])
SECRET_KEY = "&,s]Qo&B`}G4;e'L],1tY?28"

MAX_BOOKING_PLACES = 12

ENV = 'test'
DEBUG =  False
TESTING = True


