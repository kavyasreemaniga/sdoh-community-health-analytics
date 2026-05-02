# dbt SDOH Analytics

This dbt project transforms raw SDOH data from PostgreSQL bronze schema
into analytics-ready staging views and marts tables.

## Running the Project

```bash
# Install dependencies
dbt deps

# Run all models
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

## Model Lineage
## Profiles

Configure `~/.dbt/profiles.yml` with your PostgreSQL credentials.
See `.env.example` in the root directory for required variables.
