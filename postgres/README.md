### Postgres Env File
- POSTGRES_USER: database user name
- POSTGRES_PASSWORD: database container
- POSTGRES_DB: database name used

### Postgres Data Dump
Backup dump is stored in `data/dump` as a sql file
- To create the dump, run `docker exec dcat_postgresql pg_dump -U postgres postgres > ./postgres/data/dump/dcat_db-$(date +%Y-%m-%d).sql`
- To reload existing dump, run
    - `docker exec dcat_postgresql dropdb -U POSTGRES_USER POSTGRES_DB`
    - `docker exec dcat_postgresql createdb -U POSTGRES_USER POSTGRES_DB`
    - `docker exec dcat_postgresql psql -U POSTGRES_USER -d POSTGRES_DB -f /backup_dump/dcat_db-2021-01-19.sql`