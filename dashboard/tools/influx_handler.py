import os
import sys
from influxdb import InfluxDBClient
from influxdb import DataFrameClient

class influx_handler:

    def __init__(self, influxDBHost=None):

        if not influxDBHost:
            self.influxDBHost = os.getenv("INFLUXDB_SERVICE_HOST") or "localhost"
        else:
            self.influxDBHost = influxDBHost

        self.ReadClient = DataFrameClient(self.influxDBHost, 8086, 'root', 'root', 'thingsIODB')


    def getDatafromUUID(self, API_KEY):
        q = 'SELECT * FROM \"'+ API_KEY +'\" WHERE time > now() - 24h;'
        result = self.ReadClient.query(q)
        df = result[API_KEY]
        print(result, file=sys.stderr)
        return df