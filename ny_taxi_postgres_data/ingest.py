import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
url = prefix + 'yellow_tripdata_2021-01.csv.gz'

# Create iterator over full dataset
df_iter = pd.read_csv(
    url,
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=100000
)

# Grab first chunk to define schema
df_chunk = next(df_iter)

# Connect to Postgres
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')

# Create table schema
df_chunk.head(0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')
print("Table created")

# Insert first chunk
df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
print(f"Inserted {len(df_chunk)} rows")

# Insert remaining chunks
for df_chunk in tqdm(df_iter):
    df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
    print(f"Inserted {len(df_chunk)} rows")

print("Data load complete!")
