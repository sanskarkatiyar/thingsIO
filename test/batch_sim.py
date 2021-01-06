import requests
import argparse
import jsonpickle
import random
import tqdm
from time import sleep

parser = argparse.ArgumentParser(description='Send simulated data to a thingsIO account')
parser.add_argument('--endpoint', default='http://34.120.7.225/store')
parser.add_argument('--num', default=1000, type=int, help='number of simulated requests')
parser.add_argument('--delay', default=1, type=int, help='delay in seconds per round')
parser.add_argument('--schema_file', default="schema2.json", help='path to the schema json')
parser.add_argument('--uuid_file', default="uids.txt", help='path to the uuids')

args = parser.parse_args()

API_KEYS = []
with open(args.uuid_file, "r") as fp:
    API_KEYS = [i.rstrip() for i in fp.readlines()]

URL = args.endpoint
NUM_REQ = args.num
SCHEMA  = None


with open(args.schema_file, 'r') as fp:
    SCHEMA = jsonpickle.decode(fp.read())

if SCHEMA is None:
    exit(-1)

def getRandom(s):
    if s == "numeric":
        return random.uniform(0,500)
    elif s == "location":
        return "{},{}".format(random.uniform(-85,85), random.uniform(-170,170))
    else:
        return ""


headers = {'content-type': 'application/json'}

for i in tqdm.trange(NUM_REQ):
    req = dict(SCHEMA)
    for k in SCHEMA.keys():
        req[k] = getRandom(SCHEMA[k]["type"])
    for u in API_KEYS:
        r = requests.post("{}/{}".format(URL, u), data=jsonpickle.encode(req), headers=headers)