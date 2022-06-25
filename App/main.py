from fastapi import FastAPI
import os
import pandas as pd   #import the pandas library

app = FastAPI()

def read_parquet(selection):
    parquet_file = tripdata_path + 'yellow_tripdata_' + selection + '.parquet' 
    return pd.read_parquet(parquet_file, engine='pyarrow')

tripdata_path = "/storage/tripdata/" # Source folder to read data from
data_table = read_parquet('2020-01') # Read...

# Drop columns that we don't need, this reduces request handling time from 2.5s to 1s
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

# Create new column, containing trip duration
data_table['trip_dur'] = pd.to_timedelta(data_table['tpep_dropoff_datetime'] - data_table['tpep_pickup_datetime'])

# get the range, notice the start and end should be formated as 
# 2020-01-01 00:28:15
# Since this can be magically converted to a datetime datatype
def get_range_from_datetimes(start, end):
    gt = data_table['tpep_pickup_datetime'] >= start #trip started after 'start'
    lt = data_table['tpep_pickup_datetime'] <= end #trip not started after end
    return data_table.where(lt & gt)

# get the range, notice the start and end should be formated as 
# data: 2020-01-01
# time: 00:28:15
def get_range(start_date, start_time, end_date, end_time):
    start = "{} {}".format(start_date, start_time)
    end = "{} {}".format(end_date, end_time)
    return get_range_from_datetimes(start, end)

# Retrieve a list of some example routes to test with
@app.get("/")
async def root():
    return {
        "trip duration": "/trip-dur/2020-01-01/00:00:00/2021-01-02/00:00:00",
        "trip range": "/trip-range/2020-01-01/00:00:00/2021-01-02/00:00:00",
        "bills": "/bills/2020-01-01/00:00:00/2021-01-02/00:00:00",
        "bills starting in": "/bills-start-in/230/2020-01-01/00:00:00/2021-01-02/00:00:00",
        "bills ending in": "/bills-end-in/230/2020-01-01/00:00:00/2021-01-02/00:00:00",
    }

# Get trip average duration in minutes
@app.get("/trip-dur/{start_date}/{start_time}/{end_date}/{end_time}")
async def trip_range(start_date, start_time, end_date, end_time):
    subset = get_range(start_date, start_time, end_date, end_time)
    x = subset['trip_dur']
    sum = x.sum()
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
