#
# Analytics server
#
import pickle
import jsonpickle
import platform
import json
import io
import os
import sys
import pika
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image 
sns.set()

from sklearn.metrics import r2_score, median_absolute_error, mean_absolute_error
from sklearn.metrics import median_absolute_error, mean_squared_error, mean_squared_log_error

from scipy.optimize import minimize
import statsmodels.tsa.api as smt
import statsmodels.api as sm

from tqdm import tqdm_notebook
import warnings
warnings.filterwarnings('ignore')
from itertools import product
import dashboard.tools.analytics_handler as analytics_handler


rabbitMQHost = os.getenv("RABBITMQ_SERVICE_HOST") or "localhost"
analytics_db = analytics_handler.analytics_handler()


def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

hostname = platform.node()

def plot_moving_average(series, field,window=10, plot_intervals=False, scale=1.96, filename='moving_average.png'):

    rolling_mean = series.rolling(window=window).mean()
    
    plt.figure(figsize=(17,8))
    plt.title('Moving average - {}\n window size = {}'.format(field, window))
    plt.plot(rolling_mean, 'g', label='Rolling mean trend')
    
    #Plot confidence intervals for smoothed values
    if plot_intervals:
        mae = mean_absolute_error(series[window:], rolling_mean[window:])
        deviation = np.std(series[window:] - rolling_mean[window:])
        lower_bound = rolling_mean - (mae + scale * deviation)
        upper_bound = rolling_mean + (mae + scale * deviation)
        plt.plot(upper_bound, 'r--', label='Upper bound / Lower bound')
        plt.plot(lower_bound, 'r--')
            
    plt.plot(series[window:], label='Actual values')
    plt.legend(loc='best')
    plt.grid(True)
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    return img_bytes

def exponential_smoothing(series, alpha):

    result = [series[0]] # first value is same as series
    for n in range(1, len(series)):
        result.append(alpha * series[n] + (1 - alpha) * result[n-1])
    return result

def plot_exponential_smoothing(series, field, alphas=[0.05,0.3],  filename='exponential_smoothing.png'):
 
    plt.figure(figsize=(17, 8))
    for alpha in alphas:
        plt.plot(exponential_smoothing(series, alpha), label="Alpha {}".format(alpha))
    plt.plot(series.values, "c", label = "Actual")
    plt.legend(loc="best")
    plt.axis('tight')
    plt.title('Exponential Smoothing - {}'.format(field))
    plt.grid(True)
    plt.savefig(filename)
    with Image.open(filename) as image:
        img_bytes = io.BytesIO(image)
    return img_bytes

def double_exponential_smoothing(series, alpha, beta):

    result = [series[0]]
    for n in range(1, len(series)+1):
        if n == 1:
            level, trend = series[0], series[1] - series[0]
        if n >= len(series): # forecasting
            value = result[-1]
        else:
            value = series[n]
        last_level, level = level, alpha * value + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend
        result.append(level + trend)
    return result

def plot_double_exponential_smoothing(series, field, alphas=[0.9,0.02], betas=[0.9,0.02], filename='double_exponential_smoothing.png'):
     
    plt.figure(figsize=(17, 8))
    for alpha in alphas:
        for beta in betas:
            plt.plot(double_exponential_smoothing(series, alpha, beta), label="Alpha {}, beta {}".format(alpha, beta))
    plt.plot(series.values, label = "Actual")
    plt.legend(loc="best")
    plt.axis('tight')
    plt.title('Double Exponential Smoothing - {}'.format(field))
    plt.grid(True)
    plt.savefig(filename)
    with Image.open(filename) as image:
        img_bytes = io.BytesIO(image)
    return img_bytes

def tsplot(y, field, lags=30, figsize=(12, 7), syle='bmh', filename='ts_plot.png'):
    
    if not isinstance(y, pd.Series):
        y = pd.Series(y)
        
    with plt.style.context(style='bmh'):
        fig = plt.figure(figsize=figsize)
        layout = (2,2)
        ts_ax = plt.subplot2grid(layout, (0,0), colspan=2)
        acf_ax = plt.subplot2grid(layout, (1,0))
        pacf_ax = plt.subplot2grid(layout, (1,1))
        
        y.plot(ax=ts_ax)
        p_value = sm.tsa.stattools.adfuller(y)[1]
        ts_ax.set_title('Time Series Analysis Plots - {}\n Dickey-Fuller: p={0:.5f}'.format(field, p_value))
        smt.graphics.plot_acf(y, lags=lags, ax=acf_ax)
        smt.graphics.plot_pacf(y, lags=lags, ax=pacf_ax)
        plt.tight_layout()
        plt.savefig(filename)
        with Image.open(filename) as image:
            img_bytes = io.BytesIO(image)
        return img_bytes
        
        
def optimize_SARIMA(y, parameters_list, d, D, s):
    """
        Return dataframe with parameters and corresponding AIC
        
        parameters_list - list with (p, q, P, Q) tuples
        d - integration order
        D - seasonal integration order
        s - length of season
    """
    
    results = []
    best_aic = float('inf')
    
    for param in tqdm_notebook(parameters_list):
        try: model = sm.tsa.statespace.SARIMAX(y, order=(param[0], d, param[1]),
                                               seasonal_order=(param[2], D, param[3], s)).fit(disp=-1)
        except:
            continue
            
        aic = model.aic
        
        #Save best model, AIC and parameters
        if aic < best_aic:
            best_model = model
            best_aic = aic
            best_param = param
        results.append([param, model.aic])
        
    result_table = pd.DataFrame(results)
    result_table.columns = ['parameters', 'aic']
    #Sort in ascending order, lower AIC is better
    result_table = result_table.sort_values(by='aic', ascending=True).reset_index(drop=True)
    
    return result_table


def receive():
    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='toAnalytics',exchange_type='direct')

    result = rabbitMQChannel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    rabbitMQChannel.queue_bind(
        exchange='toAnalytics', queue=queue_name, routing_key='data')

    print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        unpickled = pickle.load(body)
        jobid = unpickled['job_id']
        df = unpickled['data']
        operation = unpickled['op']
        params = unpickled['params']
        fieldset = params['fields']

        result = []
        for i in range(len(fieldset)):
            if(operation == 'moving_average'):
                result.append(plot_moving_average(df.iloc[:, i], fieldset[i], params['window'], plot_intervals=False))
            if(operation == 'exponential_smoothing'):
                result.append(plot_exponential_smoothing(df.iloc[:, i], [params['alpha1'], params['alpha2']], fieldset[i]))
            if(operation == 'double_exponential_smoothing'):
                result.append(plot_double_exponential_smoothing(df.iloc[:, i], fieldset[i] ,alphas=[params['alpha1'], params['alpha2']], betas=[params['beta1'], params['beta2']]))
            if(operation == 'ts_plot'):
                result.append(tsplot(df.iloc[:, i], fieldset[i], params['lags']))
        
        analytics_db.jobid_result_db.set(jobid,result)      
            # if(operation == 'sarima_stats'):
            #     ps = range(0, 4)
            #     d = 1
            #     qs = range(0, 4)
            #     Ps = range(0, 4)
            #     D = 1
            #     Qs = range(0, 4)
            #     s = 4
            #     #Create a list with all possible combinations of parameters
            #     parameters = product(ps, qs, Ps, Qs)
            #     parameters_list = list(parameters)
            #     result_table = optimize_SARIMA(df.iloc[:, i], parameters_list, d, D, s)
            #     p, q, P, Q = result_table.parameters[0]
            #     best_model = sm.tsa.statespace.SARIMAX(df.iloc[:, i], order=(p, d, q),
            #                                         seasonal_order=(P, D, Q, s)).fit(disp=-1)
            #     print(best_model.summary())
            #     print(best_model.predict(start=df.iloc[:, i].shape[0], end=df.iloc[:, i].shape[0] + 5))
            #     print(mean_absolute_percentage_error(df.iloc[:, i][s+d:], best_model.fittedvalues[s+d:]))

    rabbitMQChannel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    rabbitMQChannel.start_consuming()
    print("done")


if __name__ == '__main__':
    try:
        receive()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)