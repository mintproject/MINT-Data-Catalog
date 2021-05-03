## MINT-Data-Catalog

### Set up .env files
- create postgres env file by running `cp ./postgres/.env.example ./postgres/.env`
- create dcat_service database connection env file by running `cp ./api/dcat_service/.env.example ./api/dcat_service/.env`

### To run Flask and Postgres service
- To force build docker images: `docker-compose --build-arg MAPGL_ACCESS_TOKEN=<your_mapgl_token> build --no-cache`
- Run `docker-compose up -d` to spin up all containers

### Frontend
- Frontend is written in Svelte an lives under `api/frontend` directory. 
- The main entry point into the frontend is `public/index.html`
- CSS and JS are compiled by Svelte from individual `.svelte` files inside `src/` and placed into `public/bundle.[css|js]`
- To (re)build Svelte, from within `frontend` directory, run `npm install && npm run build`, which will re-generate `public/bundle.[css|js]`
- To display maps, we use Mapbox, which requires an access token. Svelte expects it to be avaiable under `MAPGL_ACCESS_TOKEN` environment variable when running `npm run build`

### Verify Postgres service:
- Run `psql -h localhost -p 5433 -U postgres` to check database content
- For first time setup: after postgres container is started, in MINT-Data-Catalog:
    - run `docker cp ./postgres/dcat_db_tables_202012.sql dcat_postgresql:/tmp/`
    - run `docker exec -it dcat_postgresql psql -U postgres -f /tmp/dcat_db_tables_202012.sql` to create all tables manually
    - check database for `datasets`, `variables`, `resources` tables etc
