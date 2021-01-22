-- -------------------------------------------------------------
-- TablePlus 3.12.0(354)
--
-- https://tableplus.com/
--
-- Database: dcat_dev
-- Generation Time: 2020-12-18 13:50:15.6330
-- -------------------------------------------------------------



-- Setup PostGIS if not installed
create extension if not exists postgis;
create extension if not exists fuzzystrmatch;
create extension if not exists postgis_tiger_geocoder;
create extension if not exists postgis_topology;

-- verify schema ownerships (alternative to psql's "\dn" command )
select 
    pg_catalog.pg_namespace.nspname as "name",
    pg_catalog.pg_roles.rolname as "owner"
from pg_catalog.pg_namespace
inner join pg_catalog.pg_roles on pg_catalog.pg_roles.oid = pg_catalog.pg_namespace.nspowner;

-- Add tiger to your search path
SET search_path=public,tiger; 

-- Test tiger by using the following SELECT statement.
SELECT na.address, na.streetname, na.streettypeabbrev, na.zip
FROM normalize_address('1 Devonshire Place, Boston, MA 02109') as na;

-- Test topology by using the following SELECT statement.
SELECT topology.createtopology('my_new_topo',26986,0.5);

-- End setup PostGIS if not installed


DROP TABLE IF EXISTS "public"."datasets";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."datasets" (
    "name" varchar(255) NOT NULL,
    "description" text NOT NULL,
    "json_metadata" jsonb NOT NULL,
    "created_at" timestamp NOT NULL DEFAULT now(),
    "updated_at" timestamp NOT NULL DEFAULT now(),
    "id" uuid NOT NULL,
    "provenance_id" uuid,
    "tsv" tsvector,
    "spatial_coverage" geometry,
    "temporal_coverage" tsrange,
    "temporal_coverage_start" timestamp,
    "temporal_coverage_end" timestamp,
    "variables_list" text,
    "standard_variables_list" text
);

DROP TABLE IF EXISTS "public"."provenance";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."provenance" (
    "provenance_type" varchar,
    "json_metadata" json,
    "name" varchar,
    "id" uuid NOT NULL
);

DROP TABLE IF EXISTS "public"."resources";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."resources" (
    "data_url" varchar NOT NULL,
    "resource_type" varchar NOT NULL,
    "json_metadata" jsonb NOT NULL,
    "layout" jsonb NOT NULL,
    "created_at" timestamp NOT NULL DEFAULT now(),
    "updated_at" timestamp NOT NULL DEFAULT now(),
    "name" varchar NOT NULL,
    "id" uuid NOT NULL,
    "dataset_id" uuid,
    "provenance_id" uuid,
    "is_queryable" bool NOT NULL DEFAULT true
);

DROP TABLE IF EXISTS "public"."resources_variables";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."resources_variables" (
    "resource_id" uuid,
    "variable_id" uuid
);

DROP TABLE IF EXISTS "public"."spatial_coverage_index";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."spatial_coverage_index" (
    "indexed_type" varchar NOT NULL,
    "spatial_coverage" geometry,
    "indexed_id" uuid NOT NULL
);

-- DROP TABLE IF EXISTS "public"."spatial_ref_sys";
-- -- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.
--
-- -- Table Definition
-- CREATE TABLE "public"."spatial_ref_sys" (
--     "srid" int4 NOT NULL,
--     "auth_name" varchar(256),
--     "auth_srid" int4,
--     "srtext" varchar(2048),
--     "proj4text" varchar(2048)
-- );

DROP TABLE IF EXISTS "public"."standard_variables";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."standard_variables" (
    "ontology" varchar NOT NULL,
    "uri" varchar NOT NULL,
    "description" varchar,
    "created_at" timestamp NOT NULL DEFAULT now(),
    "updated_at" timestamp NOT NULL DEFAULT now(),
    "name" varchar NOT NULL,
    "id" uuid NOT NULL
);

DROP TABLE IF EXISTS "public"."temporal_coverage_index";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."temporal_coverage_index" (
    "indexed_type" varchar NOT NULL,
    "start_time" timestamp NOT NULL,
    "end_time" timestamp NOT NULL,
    "indexed_id" uuid
);

DROP TABLE IF EXISTS "public"."variables";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."variables" (
    "json_metadata" jsonb NOT NULL,
    "name" varchar NOT NULL,
    "id" uuid NOT NULL,
    "dataset_id" uuid
);

DROP TABLE IF EXISTS "public"."variables_standard_variables";
-- This script only contains the table creation statements and does not fully represent the table in the database. It's still missing: indices, triggers. Do not use it as a backup.

-- Table Definition
CREATE TABLE "public"."variables_standard_variables" (
    "variable_id" uuid,
    "standard_variable_id" uuid
);

-- ALTER TABLE "public"."datasets" ADD FOREIGN KEY ("provenance_id") REFERENCES "public"."provenance"("id");
-- ALTER TABLE "public"."resources" ADD FOREIGN KEY ("provenance_id") REFERENCES "public"."provenance"("id");
-- ALTER TABLE "public"."resources" ADD FOREIGN KEY ("dataset_id") REFERENCES "public"."datasets"("id");
-- ALTER TABLE "public"."resources_variables" ADD FOREIGN KEY ("resource_id") REFERENCES "public"."resources"("id");
-- ALTER TABLE "public"."resources_variables" ADD FOREIGN KEY ("variable_id") REFERENCES "public"."variables"("id");
-- ALTER TABLE "public"."variables" ADD FOREIGN KEY ("dataset_id") REFERENCES "public"."datasets"("id");
-- ALTER TABLE "public"."variables_standard_variables" ADD FOREIGN KEY ("variable_id") REFERENCES "public"."variables"("id");
-- ALTER TABLE "public"."variables_standard_variables" ADD FOREIGN KEY ("standard_variable_id") REFERENCES "public"."standard_variables"("id");



-- Setup indices and triggers and functions

-- PROVENANCE
-- provenance_id_key
DROP INDEX IF EXISTS provenance_id_key;
CREATE UNIQUE INDEX provenance_id_key ON public.provenance USING btree (id);


-- DATASETS
-- ix_datasets_name
DROP INDEX IF EXISTS ix_datasets_name;
CREATE INDEX ix_datasets_name ON public.datasets USING btree (name);

-- ix_datasets_created_at
DROP INDEX IF EXISTS ix_datasets_created_at;
CREATE INDEX ix_datasets_created_at ON public.datasets USING btree (created_at);

-- datasets_tc_start_idx
DROP INDEX IF EXISTS datasets_tc_start_idx;
CREATE INDEX datasets_tc_start_idx ON public.datasets USING btree (temporal_coverage_start);

-- datasets_tc_end_idx
DROP INDEX IF EXISTS datasets_tc_end_idx;
CREATE INDEX datasets_tc_end_idx ON public.datasets USING btree (temporal_coverage_end);

-- datasets_spatial_gix
DROP INDEX IF EXISTS datasets_spatial_gix;
CREATE INDEX datasets_spatial_gix ON public.datasets USING gist (spatial_coverage);

-- datasets_id_key
DROP INDEX IF EXISTS datasets_id_key;
CREATE UNIQUE INDEX datasets_id_key ON public.datasets USING btree (id);

-- 'tsv_idx'
DROP INDEX IF EXISTS tsv_idx;
CREATE INDEX tsv_idx ON public.datasets USING gin (tsv);

-- DROP trigger
DROP TRIGGER IF EXISTS if_dist_exists ON public.datasets;

CREATE OR REPLACE FUNCTION datasets_tsv_trigger() RETURNS trigger AS $$
begin
  new.tsv :=
     setweight(to_tsvector('pg_catalog.english', coalesce(new.name,'')), 'A') ||
       setweight(to_tsvector('pg_catalog.english', coalesce(new.json_metadata->>'tags', '')), 'B') ||
       setweight(to_tsvector('pg_catalog.english', coalesce(new.variables_list, '')), 'D') ||
       setweight(to_tsvector('pg_catalog.english', coalesce(new.standard_variables_list, '')), 'C') ||
     setweight(to_tsvector('pg_catalog.english', coalesce(new.description,'')), 'D');
  return new;
end
$$ LANGUAGE plpgsql;

CREATE TRIGGER datasets_tsv_update BEFORE INSERT OR UPDATE
    ON datasets FOR EACH ROW EXECUTE PROCEDURE datasets_tsv_trigger();




-- RESOURCES
-- resources_id_key
DROP INDEX IF EXISTS resources_id_key;
CREATE UNIQUE INDEX resources_id_key ON public.resources USING btree (id);

-- queryable_resource_id_idx
DROP INDEX IF EXISTS queryable_resource_id_idx;
CREATE INDEX queryable_resource_id_idx ON public.resources USING btree (id) WHERE (is_queryable = true);

-- ix_resources_provenance_id
DROP INDEX IF EXISTS ix_resources_provenance_id;
CREATE INDEX ix_resources_provenance_id ON public.resources USING btree (provenance_id);

-- ix_resources_dataset_id
DROP INDEX IF EXISTS ix_resources_dataset_id;
CREATE INDEX ix_resources_dataset_id ON public.resources USING btree (dataset_id);

-- ix_resources_created_at
DROP INDEX IF EXISTS ix_resources_created_at;
CREATE INDEX ix_resources_created_at ON public.resources USING btree (created_at);





-- VARIABLES
-- variables_id_key
DROP INDEX IF EXISTS variables_id_key;
CREATE UNIQUE INDEX variables_id_key ON public.variables USING btree (id);

-- variables_dataset_id_name_key
DROP INDEX IF EXISTS variables_dataset_id_name_key;
CREATE UNIQUE INDEX variables_dataset_id_name_key ON public.variables USING btree (dataset_id, name);





-- STANDARD_VARIABLES
-- standard_variables_uri_key
DROP INDEX IF EXISTS standard_variables_uri_key;
CREATE UNIQUE INDEX standard_variables_uri_key ON public.standard_variables USING btree (uri);

-- standard_variables_id_key
DROP INDEX IF EXISTS standard_variables_id_key;
CREATE UNIQUE INDEX standard_variables_id_key ON public.standard_variables USING btree (id);

-- ix_standard_variables_name
DROP INDEX IF EXISTS ix_standard_variables_name;
CREATE INDEX ix_standard_variables_name ON public.standard_variables USING btree (name);

-- ix_standard_variables_created_at
DROP INDEX IF EXISTS ix_standard_variables_created_at;
CREATE INDEX ix_standard_variables_created_at ON public.standard_variables USING btree (created_at);




-- TEMPORAL_COVERAGE_INDEX
-- temporal_coverage_index_indexed_type_indexed_id_key
DROP INDEX IF EXISTS temporal_coverage_index_indexed_type_indexed_id_key;
CREATE UNIQUE INDEX temporal_coverage_index_indexed_type_indexed_id_key ON public.temporal_coverage_index USING btree (indexed_type, indexed_id);

-- ix_temporal_coverage_index_start_time
DROP INDEX IF EXISTS ix_temporal_coverage_index_start_time;
CREATE INDEX ix_temporal_coverage_index_start_time ON public.temporal_coverage_index USING btree (start_time);

-- ix_temporal_coverage_index_end_time
DROP INDEX IF EXISTS ix_temporal_coverage_index_end_time;
CREATE INDEX ix_temporal_coverage_index_end_time ON public.temporal_coverage_index USING btree (end_time);



-- SPATIAL_COVERAGE_INDEX
-- spatial_coverage_index_indexed_id_key
DROP INDEX IF EXISTS spatial_coverage_index_indexed_id_key;
CREATE UNIQUE INDEX spatial_coverage_index_indexed_id_key ON public.spatial_coverage_index USING btree (indexed_id);

-- idx_spatial_coverage_index_spatial_coverage_indexed_id
DROP INDEX IF EXISTS idx_spatial_coverage_index_spatial_coverage_indexed_id;
CREATE UNIQUE INDEX idx_spatial_coverage_index_spatial_coverage_indexed_id ON public.spatial_coverage_index USING btree (spatial_coverage, indexed_id);

-- idx_spatial_coverage_index_spatial_coverage
DROP INDEX IF EXISTS idx_spatial_coverage_index_spatial_coverage;
CREATE INDEX idx_spatial_coverage_index_spatial_coverage ON public.spatial_coverage_index USING gist (spatial_coverage);

ALTER TABLE "public"."datasets" ADD FOREIGN KEY ("provenance_id") REFERENCES "public"."provenance"("id");
ALTER TABLE "public"."resources" ADD FOREIGN KEY ("provenance_id") REFERENCES "public"."provenance"("id");
ALTER TABLE "public"."resources" ADD FOREIGN KEY ("dataset_id") REFERENCES "public"."datasets"("id");
ALTER TABLE "public"."resources_variables" ADD FOREIGN KEY ("resource_id") REFERENCES "public"."resources"("id");
ALTER TABLE "public"."resources_variables" ADD FOREIGN KEY ("variable_id") REFERENCES "public"."variables"("id");
ALTER TABLE "public"."variables" ADD FOREIGN KEY ("dataset_id") REFERENCES "public"."datasets"("id");
ALTER TABLE "public"."variables_standard_variables" ADD FOREIGN KEY ("variable_id") REFERENCES "public"."variables"("id");
ALTER TABLE "public"."variables_standard_variables" ADD FOREIGN KEY ("standard_variable_id") REFERENCES "public"."standard_variables"("id");
