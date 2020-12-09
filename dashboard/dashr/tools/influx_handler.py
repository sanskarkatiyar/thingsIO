import os
import sys
from influxdb import InfluxDBClient
from influxdb import DataFrameClient
from pandas import DataFrame

class influx_handler:

    def __init__(self, influxDBHost=None):

        if influxDBHost is None:
            self.influxDBHost = os.getenv("INFLUXDB_SERVICE_HOST") or "localhost"
        else:
            self.influxDBHost = influxDBHost

        self.ReadClient = DataFrameClient(self.influxDBHost, 8086, 'root', 'root', 'thingsIODB')


    def getDatafromUUID(self, API_KEY):
        q = 'SELECT * FROM \"'+ API_KEY +'\" ;'
        result = self.ReadClient.query(q)
        try:
            df = result[API_KEY]
        except KeyError:
            return DataFrame()
        # print(result, file=sys.stderr)
        return df