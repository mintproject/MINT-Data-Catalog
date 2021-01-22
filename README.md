## MINT-Data-Catalog

### Set up .env files
- create postgres env file by running `cp ./postgres/.env.example ./postgres/.env`
- create dcat_service database connection env file by running `cp ./api/dcat_service/.env.example ./api/dcat_service/.env`

### To run Flask and Postgres service
- To force build docker images: `docker-compose -f docker-compose-dev.yml build --no-cache`
- Run `docker-compose -f docker-compose-dev.yml up -d` to spin up all containers
- To rebuild Svelte changes in ./api, run `cd frontend && npm install && npm run-script build && cd ..` 

### Verify Postgres service:
- Run `psql -h localhost -p 5433 -U postgres` to check database content
- For first time setup: after postgres container is started, in MINT-Data-Catalog:
    - run `docker cp ./postgres/dcat_db_tables_202012.sql dcat_postgresql:/tmp/`
    - run `docker exec -it dcat_postgresql psql -U postgres -f /tmp/dcat_db_tables_202012.sql` to create all tables manually
    - check database for `datasets`, `variables`, `resources` tables etc