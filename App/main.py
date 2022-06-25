from re import X
from fastapi import FastAPI
import os
import pandas as pd   #import the pandas library

app = FastAPI()

def read_parquet(selection):
    parquet_file = tripdata_path + 'yellow_tripdata_' + selection + '.parquet' 
    return pd.read_parquet(parquet_file, engine='pyarrow')

tripdata_path = "/storage/tripdata/"
data_table = read_parquet('2020-01')
data_table.drop([
    'VendorID', 
    'passenger_count', 
    'RatecodeID', 
    'store_and_fwd_flag', 
    'payment_type', 
    'fare_amount',
    'extra', 
    'mta_tax', 
    'tip_amount',
    'tolls_amount',
    'improvement_surcharge',
    'congestion_surcharge',
    'airport_fee'
    ], axis=1, inplace=True)

data_table['trip_dur'] = pd.to_timedelta(data_table['tpep_dropoff_datetime'] - data_table['tpep_pickup_datetime'])

def get_range_from_datetimes(start, end):
    gt = data_table['tpep_pickup_datetime'] >= start #trip started after 'start'
    lt = data_table['tpep_pickup_datetime'] <= end #trip not started after end
    return data_table.where(lt & gt)

def get_range(start_date, start_time, end_date, end_time):
    start = "{} {}".format(start_date, start_time)
    end = "{} {}".format(end_date, end_time)
    return get_range_from_datetimes(start, end)

@app.get("/")
async def root():
    return {
        "trip duration": "/trip-dur/{start_date}/{start_time}/{end_date}/{end_time}"
    }

@app.get("/trip-dur/{start_date}/{start_time}/{end_date}/{end_time}")
async def trip_range(start_date, start_time, end_date, end_time):
    subset = get_range(start_date, start_time, end_date, end_time)
    x = subset['trip_dur']
    sum = X.sum()
    mean = x.mean()
    median = x.median()
    return { "total": sum, "mean": mean, "median": median}


@app.get("/trip-range/{start_date}/{start_time}/{end_date}/{end_time}")
async def trip_range(start_date, start_time, end_date, end_time):
    subset = get_range(start_date, start_time, end_date, end_time)
    x = subset['trip_distance']
    sum = x.sum()
    mean = x.mean()
    median = x.median()
    return { "total": sum, "mean": mean, "median": median}

@app.get("/bills/{start_date}/{start_time}/{end_date}/{end_time}")
async def trip_cost(start_date, start_time, end_date, end_time):
    subset = get_range(start_date, start_time, end_date, end_time)
    x = subset['total_amount']
    sum = x.sum()
    mean = x.mean()
    median = x.median()
    return { "total": sum, "mean": mean, "median": median}

@app.get("/bills-start-in/{PULocationID}/{start_date}/{start_time}/{end_date}/{end_time}")
async def trip_cost_start(PULocationID, start_date, start_time, end_date, end_time):
    subset = get_range(start_date, start_time, end_date, end_time)
    subset = subset.where(subset['PULocationID'] == PULocationID) # To be fixed
    x = subset['total_amount']
    sum = x.sum()
    mean = x.mean()
    median = x.median()
    return { "total": sum, "mean": mean, "median": median}

@app.get("/bills-end-in/{DOLocationID}/{start_date}/{start_time}/{end_date}/{end_time}")
async def trip_cost_end(DOLocationID, start_date, start_time, end_date, end_time):
    subset = get_range(start_date, start_time, end_date, end_time)
    subset = subset.where(subset['DOLocationID'] == DOLocationID) # To be fixed
    
    x = subset['total_amount']
    sum = x.sum()
    mean = x.mean()
    median = x.median()
    return { "total": sum, "mean": mean, "median": median}
