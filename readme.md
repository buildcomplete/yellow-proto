# New York Yellow cab example rest API

The purpose is to create a simple API service allowing to _get some data_ from the dataset

## The following is the requirements from the client
* Use the dataset [yellow_tripdata_2020-01.csv](https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2020-01.csv) from amazon, but the csv data seems no longer to be avaliable, we use instead the 'parquet' format
* Build an application to serve the API that can run locally, with all requirements properly specified in the package.
* The application should be built as if it were to be put in production, keep scalability and performance in mind

## Testing of corrects
> The application is currently _not tested_ to see if the results are correct, the following tests must be made for each route

Id|Test|Responsible
-|-|-
1|Response should be valid according to specification from all routes when interval contain no data (need to be agreed with customer, suggest 0 or 404)|VJ
2|Check that results are correct when having 'one' sample|VJ
3|Results are selected correct according to query terms (manually specify dataset and verify selection on borders)|VJ
4|Results are correct when have 'two' samples (especially check agreement of median)|VJ
5|Results is correctly loaded when comming from multiple datafiles (example, median across data from January and February should give result as agreed upon)|VJ
6|Perfomance of a single 'get' no requirements is made, what should it be?|CG
7|How many concurrent users will be on the system?|CH

## Additional specification needed to decide on requirements
* how different will the queryes be? 
* can the results be cached? for instance for plots, the query might always asks for the timeranges of a full month, if so the result can be cached


# Starting the application
* Before starting the application [yellow_tripdata_2020-01.parquet](https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2020-01.parquet) must be copied to /storage/tripdata (It is not included in here)
* Build and run the image
```sh
wget -O storage/tripdata/yellow_tripdata_2020-01.parquet https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2020-01.parquet 
hostname -I
docker-compose build
docker-compose up
```
Note the IP adress from above, navigate to the IP adress and test the rest API.
```
http://{IP}/trip-dur/2020-01-01/00:00:00/2020-01-02/00:00:00
```

# Routes documentation
Requirements: all metrics can be queried with configurable start and end date

All routes have a start and end specified as the following template
{metric}/YYYY-MM-DD/hh:mm:ss/YYYY-MM-DD/hh:mm:ss 
* (first timestamp is minimum time, trip should be started _after_ this)
* (second timestamp is maximum time, trip should be started _before_ this)

## Average, median trip length 
(km and minutes), 
To get either range or duration, the _trip-range_ or _trip-dur_ routes can be used
```
trip-range/YYYY-MM-DD/hh:mm:ss/YYYY-MM-DD/hh:mm:ss 
trip-dur/YYYY-MM-DD/hh:mm:ss/YYYY-MM-DD/hh:mm:ss 
```

## Billings statistics 
(total, mean, median), using the total_amount variable.
```
bills/YYYY-MM-DD/hh:mm:ss/YYYY-MM-DD/hh:mm:ss 
```
## Billings statistics 
(total, mean, median), using the total_amount variable for trips starting at a given PULocationID or ending in a given DOLocationID.
```
bills-start-in/PULocationID/YYYY-MM-DD/hh:mm:ss/YYYY-MM-DD/hh:mm:ss
bills-end-in/PULocationID/YYYY-MM-DD/hh:mm:ss/YYYY-MM-DD/hh:mm:ss
```

## Known bugs / issues
* The respons time is arround 1 seconds for most routes after removing additional columns (is it good enough, there are no requirements in the spec)
* with one dataset loaded, it is consuming ~500mb of RAM for january-2020 (Loading all datasets would )
* Bills-start-in and Bills-end-in  does not work, the sub selection for PULocation needs to be fixed

## Design modifications
* The data could be loaded into a database that can handle the entire dataset fast, since for calculating median value, all the data need to be in memory at the same time.
* It is also possible that removing all the colums that are not needed, it would be feasable to have everything in memory, right now we use 500mb of ram for one month, assuming the same amount of data for each month gives 6gb-year, for 10 years that 60gb
* Maybee removing the unused columns would solve the problem, we are using the following column
  * trip_distance
  * total_amount
  * trip_dur
  * tpep_pickup_datetime
the dataset consist of 19 columns, and we just use 4column if we multiply the 60gb for 10 years with 4/19 we only seem to need ~4.5gb of memory