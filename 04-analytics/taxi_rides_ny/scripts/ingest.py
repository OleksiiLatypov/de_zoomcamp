import argparse
import duckdb
import requests
from pathlib import Path
import sys

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"


def download_and_convert_files(taxi_type, years, months):
    data_dir = Path("data") / taxi_type
    data_dir.mkdir(exist_ok=True, parents=True)

    for year in years:
        for month in months:
            parquet_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
            parquet_filepath = data_dir / parquet_filename

            if parquet_filepath.exists():
                print(f"Skipping {parquet_filename} (already exists)")
                continue

            # Download CSV.gz file
            csv_gz_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.csv.gz"
            csv_gz_filepath = data_dir / csv_gz_filename

            print(f"Downloading {csv_gz_filename}...")
            response = requests.get(f"{BASE_URL}/{taxi_type}/{csv_gz_filename}", stream=True)
            try:
                response.raise_for_status()
            except Exception as e:
                print(f"Failed to download {csv_gz_filename}: {e}")
                continue

            with open(csv_gz_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Converting {csv_gz_filename} to Parquet...")
            con = duckdb.connect()
            con.execute(f"""
                COPY (SELECT * FROM read_csv_auto('{csv_gz_filepath}'))
                TO '{parquet_filepath}' (FORMAT PARQUET)
            """)
            con.close()

            # Remove the CSV.gz file to save space
            try:
                csv_gz_filepath.unlink()
            except Exception:
                pass
            print(f"Completed {parquet_filename}")


def update_gitignore(project_root: Path):
    gitignore_path = project_root / ".gitignore"

    # Read existing content or start with empty string
    content = gitignore_path.read_text() if gitignore_path.exists() else ""

    # Add data/ if not already present
    if 'data/' not in content:
        with open(gitignore_path, 'a') as f:
            f.write('\n# Data directory\ndata/\n' if content else '# Data directory\ndata/\n')
        print("Updated .gitignore to exclude data/")
    else:
        print(".gitignore already excludes data/")


def create_duckdb_tables(project_root: Path, taxi_types):
    db_path = project_root / "taxi_rides_ny.duckdb"
    con = duckdb.connect(str(db_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS prod")

    for taxi_type in taxi_types:
        print(f"Creating table prod.{taxi_type}_tripdata from parquet files...")
        con.execute(f"""
            CREATE OR REPLACE TABLE prod.{taxi_type}_tripdata AS
            SELECT * FROM read_parquet('data/{taxi_type}/*.parquet', union_by_name=true)
        """)
    con.close()
    print(f"DuckDB database written to {db_path}")


def main():
    parser = argparse.ArgumentParser(description="Download NYC TLC data and load into DuckDB (parquet conversion)")
    parser.add_argument('--sample', action='store_true', help='Only download a small sample (2019-01) for quick testing')
    parser.add_argument('--types', type=str, help='Comma-separated list of taxi types (yellow,green,fhv)', default='yellow,green')
    parser.add_argument('--years', type=str, help='Comma-separated list of years', default='2019,2020')
    args = parser.parse_args()

    project_root = Path('.').resolve()

    # Update .gitignore
    update_gitignore(project_root)

    if args.sample:
        years = [2019]
        months = [1]
        print("Running in sample mode: only 2019-01 will be downloaded")
    else:
        years = [int(y) for y in args.years.split(',')]
        months = list(range(1, 13))

    taxi_types = args.types.split(',')

    for taxi_type in taxi_types:
        download_and_convert_files(taxi_type, years, months)

    # Create DuckDB and tables
    create_duckdb_tables(project_root, taxi_types)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted by user', file=sys.stderr)
        sys.exit(1)
