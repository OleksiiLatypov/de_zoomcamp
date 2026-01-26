from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client()

# Set your project and dataset info
project_id = "peppy-primacy-41851"
dataset_id = "nyc_taxi"

# Reference the dataset
dataset_ref = client.dataset(dataset_id, project=project_id)

# List tables in the dataset (example action)
tables = list(client.list_tables(dataset_ref))
print(f"Tables in dataset {dataset_id}:")
for table in tables:
    print(f"- {table.table_id}")

# Run a query on a specific table in the dataset
query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.green_data`
    LIMIT 10
"""
query_job = client.query(query)  # API request
results = query_job.result()  # Waits for job to complete

for row in results:
    print(row)
