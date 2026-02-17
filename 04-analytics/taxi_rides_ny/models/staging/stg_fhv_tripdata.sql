with source as (
    select * from {{ source('raw', 'fhv_tripdata') }}
),

renamed as (
    select
        -- identifiers
        cast(dispatching_base_num as string) as dispatching_base_num,
        cast(Affiliated_base_number as string) as affiliated_base_number,
        
        -- location ids
        cast(PUlocationID as integer) as pickup_location_id,
        cast(DOlocationID as integer) as dropoff_location_id,

        -- timestamps
        cast(pickup_datetime as timestamp) as pickup_datetime,
        cast(dropOff_datetime as timestamp) as dropoff_datetime,

        -- trip info
        cast(SR_Flag as string) as sr_flag

    from source
    -- Filter out records where dispatching_base_num IS NULL (data quality requirement)
    where dispatching_base_num is not null
)

select * from renamed
