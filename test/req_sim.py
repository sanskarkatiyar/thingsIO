import requests
import argparse
import jsonpickle
import random
import tqdm
from time import sleep

parser = argparse.ArgumentParser(description='Send simulated data to a thingsIO account')
parser.add_argument('--endpoint', default='http://localhost:6000/store/')
parser.add_argument('--apikey', default='3619296a391f11eba1e100155d87074f', type=str)
parser.add_argument('--num', default=100, type=int, help='number of simulated requests')
parser.add_argument('--schema_file', default="schema.json", help='path to the schema json')

args = parser.parse_args()

API_KEY = args.apikey
URL = args.endpoint + API_KEY
NUM_REQ = args.num
SCHEMA  = None

with open(args.schema_file, 'r') as fp:
    SCHEMA = jsonpickle.decode(fp.read())

if SCHEMA is None:
    exit(-1)

def getRandom(s):
    if s == "numeric":
        return random.uniform(0,100)
    elif s == "location":
        return "{},{}".format(random.uniform(30,60), random.uniform(40,70))
    else:
        return ""


headers = {'content-type': 'application/json'}

for i in tqdm.trange(NUM_REQ):
    req = dict(SCHEMA)
    for k in SCHEMA.keys():
        req[k] = getRandom(SCHEMA[k]["type"])

    r = requests.post(URL, data=jsonpickle.encode(req), headers=headers)
    sleep(0.5)