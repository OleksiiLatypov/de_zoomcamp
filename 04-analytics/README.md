# Data Engineering Zoomcamp - Homework 4

## Question 1
`dbt run --select int_trips_unioned` builds which models?

**Answer:** int_trips_unioned only

```bash
dbt run --select int_trips_unioned --target prod
```

## Question 2
A new value 6 appears in payment_type when you have an accepted_values test for [1,2,3,4,5]. What happens when you run dbt test?

**Answer:** dbt will fail the test, returning a non-zero exit code

```bash
dbt test --select fct_trips --target prod
```

## Question 3
Count of records in fct_monthly_zone_revenue?

**Answer:** 12,184

```sql
SELECT COUNT(*) FROM prod.fct_monthly_zone_revenue;
```

## Question 4
Zone with highest revenue for Green taxis in 2020?

**Answer:** East Harlem North

```sql
SELECT 
    pickup_zone,
    SUM(revenue_monthly_total_amount) as total_revenue
FROM prod.fct_monthly_zone_revenue
WHERE service_type = 'Green'
    AND EXTRACT(YEAR FROM revenue_month) = 2020
GROUP BY pickup_zone
ORDER BY total_revenue DESC
LIMIT 1;
```

## Question 5
Total trips for Green taxis in October 2019?

**Answer:** 384,624

```sql
SELECT SUM(total_monthly_trips) as total_trips
FROM prod.fct_monthly_zone_revenue
WHERE service_type = 'Green'
    AND EXTRACT(YEAR FROM revenue_month) = 2019
    AND EXTRACT(MONTH FROM revenue_month) = 10;
```

## Question 6
Count of records in stg_fhv_tripdata (filter dispatching_base_num IS NULL)?

**Answer:** 43,244,693

```sql
-- stg_fhv_tripdata.sql
with source as (
    select * from {{ source('raw', 'fhv_tripdata') }}
),
renamed as (
    select
        cast(dispatching_base_num as string) as dispatching_base_num,
        cast(Affiliated_base_number as string) as affiliated_base_number,
        cast(PUlocationID as integer) as pickup_location_id,
        cast(DOlocationID as integer) as dropoff_location_id,
        cast(pickup_datetime as timestamp) as pickup_datetime,
        cast(dropOff_datetime as timestamp) as dropoff_datetime,
        cast(SR_Flag as string) as sr_flag
    from source
    where dispatching_base_num is not null
)
select * from renamed
```

```sql
SELECT COUNT(*) FROM prod.stg_fhv_tripdata;
```

