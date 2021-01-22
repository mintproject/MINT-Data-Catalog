--
-- PostgreSQL database dump
--

-- Dumped from database version 10.15
-- Dumped by pg_dump version 10.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: DATABASE postgres; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON DATABASE postgres IS 'default administrative connection database';


--
-- Name: my_new_topo; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA my_new_topo;


ALTER SCHEMA my_new_topo OWNER TO postgres;

--
-- Name: tiger; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tiger;


ALTER SCHEMA tiger OWNER TO postgres;

--
-- Name: tiger_data; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tiger_data;


ALTER SCHEMA tiger_data OWNER TO postgres;

--
-- Name: topology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO postgres;

--
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';


--
-- Name: postgis_tiger_geocoder; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder WITH SCHEMA tiger;


--
-- Name: EXTENSION postgis_tiger_geocoder; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_tiger_geocoder IS 'PostGIS tiger geocoder and reverse geocoder';


--
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


--
-- Name: datasets_tsv_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.datasets_tsv_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
  new.tsv :=
     setweight(to_tsvector('pg_catalog.english', coalesce(new.name,'')), 'A') ||
       setweight(to_tsvector('pg_catalog.english', coalesce(new.json_metadata->>'tags', '')), 'B') ||
       setweight(to_tsvector('pg_catalog.english', coalesce(new.variables_list, '')), 'D') ||
       setweight(to_tsvector('pg_catalog.english', coalesce(new.standard_variables_list, '')), 'C') ||
     setweight(to_tsvector('pg_catalog.english', coalesce(new.description,'')), 'D');
  return new;
end
$$;


ALTER FUNCTION public.datasets_tsv_trigger() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: edge_data; Type: TABLE; Schema: my_new_topo; Owner: postgres
--

CREATE TABLE my_new_topo.edge_data (
    edge_id integer NOT NULL,
    start_node integer NOT NULL,
    end_node integer NOT NULL,
    next_left_edge integer NOT NULL,
    abs_next_left_edge integer NOT NULL,
    next_right_edge integer NOT NULL,
    abs_next_right_edge integer NOT NULL,
    left_face integer NOT NULL,
    right_face integer NOT NULL,
    geom public.geometry(LineString,26986)
);


ALTER TABLE my_new_topo.edge_data OWNER TO postgres;

--
-- Name: edge; Type: VIEW; Schema: my_new_topo; Owner: postgres
--

CREATE VIEW my_new_topo.edge AS
 SELECT edge_data.edge_id,
    edge_data.start_node,
    edge_data.end_node,
    edge_data.next_left_edge,
    edge_data.next_right_edge,
    edge_data.left_face,
    edge_data.right_face,
    edge_data.geom
   FROM my_new_topo.edge_data;


ALTER TABLE my_new_topo.edge OWNER TO postgres;

--
-- Name: VIEW edge; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON VIEW my_new_topo.edge IS 'Contains edge topology primitives';


--
-- Name: COLUMN edge.edge_id; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON COLUMN my_new_topo.edge.edge_id IS 'Unique identifier of the edge';


--
-- Name: COLUMN edge.start_node; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON COLUMN my_new_topo.edge.start_node IS 'Unique identifier of the node at the start of the edge';


--
-- Name: COLUMN edge.end_node; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON COLUMN my_new_topo.edge.end_node IS 'Unique identifier of the node at the end of the edge';


--
-- Name: COLUMN edge.next_left_edge; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON COLUMN my_new_topo.edge.next_left_edge IS 'Unique identifier of the next edge of the face on the left (when looking in the direction from START_NODE to END_NODE), moving counterclockwise around the face boundary';


--
-- Name: COLUMN edge.next_right_edge; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON COLUMN my_new_topo.edge.next_right_edge IS 'Unique identifier of the next edge of the face on the right (when looking in the direction from START_NODE to END_NODE), moving counterclockwise around the face boundary';


--
-- Name: COLUMN edge.left_face; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON COLUMN my_new_topo.edge.left_face IS 'Unique identifier of the face on the left side of the edge when looking in the direction from START_NODE to END_NODE';


--
-- Name: COLUMN edge.right_face; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON COLUMN my_new_topo.edge.right_face IS 'Unique identifier of the face on the right side of the edge when looking in the direction from START_NODE to END_NODE';


--
-- Name: COLUMN edge.geom; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON COLUMN my_new_topo.edge.geom IS 'The geometry of the edge';


--
-- Name: edge_data_edge_id_seq; Type: SEQUENCE; Schema: my_new_topo; Owner: postgres
--

CREATE SEQUENCE my_new_topo.edge_data_edge_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE my_new_topo.edge_data_edge_id_seq OWNER TO postgres;

--
-- Name: edge_data_edge_id_seq; Type: SEQUENCE OWNED BY; Schema: my_new_topo; Owner: postgres
--

ALTER SEQUENCE my_new_topo.edge_data_edge_id_seq OWNED BY my_new_topo.edge_data.edge_id;


--
-- Name: face; Type: TABLE; Schema: my_new_topo; Owner: postgres
--

CREATE TABLE my_new_topo.face (
    face_id integer NOT NULL,
    mbr public.geometry(Polygon,26986)
);


ALTER TABLE my_new_topo.face OWNER TO postgres;

--
-- Name: TABLE face; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON TABLE my_new_topo.face IS 'Contains face topology primitives';


--
-- Name: face_face_id_seq; Type: SEQUENCE; Schema: my_new_topo; Owner: postgres
--

CREATE SEQUENCE my_new_topo.face_face_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE my_new_topo.face_face_id_seq OWNER TO postgres;

--
-- Name: face_face_id_seq; Type: SEQUENCE OWNED BY; Schema: my_new_topo; Owner: postgres
--

ALTER SEQUENCE my_new_topo.face_face_id_seq OWNED BY my_new_topo.face.face_id;


--
-- Name: layer_id_seq; Type: SEQUENCE; Schema: my_new_topo; Owner: postgres
--

CREATE SEQUENCE my_new_topo.layer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE my_new_topo.layer_id_seq OWNER TO postgres;

--
-- Name: node; Type: TABLE; Schema: my_new_topo; Owner: postgres
--

CREATE TABLE my_new_topo.node (
    node_id integer NOT NULL,
    containing_face integer,
    geom public.geometry(Point,26986)
);


ALTER TABLE my_new_topo.node OWNER TO postgres;

--
-- Name: TABLE node; Type: COMMENT; Schema: my_new_topo; Owner: postgres
--

COMMENT ON TABLE my_new_topo.node IS 'Contains node topology primitives';


--
-- Name: node_node_id_seq; Type: SEQUENCE; Schema: my_new_topo; Owner: postgres
--

CREATE SEQUENCE my_new_topo.node_node_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE my_new_topo.node_node_id_seq OWNER TO postgres;

--
-- Name: node_node_id_seq; Type: SEQUENCE OWNED BY; Schema: my_new_topo; Owner: postgres
--

ALTER SEQUENCE my_new_topo.node_node_id_seq OWNED BY my_new_topo.node.node_id;


--
-- Name: relation; Type: TABLE; Schema: my_new_topo; Owner: postgres
--

CREATE TABLE my_new_topo.relation (
    topogeo_id integer NOT NULL,
    layer_id integer NOT NULL,
    element_id integer NOT NULL,
    element_type integer NOT NULL
);


ALTER TABLE my_new_topo.relation OWNER TO postgres;

--
-- Name: datasets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.datasets (
    name character varying(255) NOT NULL,
    description text NOT NULL,
    json_metadata jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    id uuid NOT NULL,
    provenance_id uuid,
    tsv tsvector,
    spatial_coverage public.geometry,
    temporal_coverage tsrange,
    temporal_coverage_start timestamp without time zone,
    temporal_coverage_end timestamp without time zone,
    variables_list text,
    standard_variables_list text
);


ALTER TABLE public.datasets OWNER TO postgres;

--
-- Name: provenance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provenance (
    provenance_type character varying,
    json_metadata json,
    name character varying,
    id uuid NOT NULL
);


ALTER TABLE public.provenance OWNER TO postgres;

--
-- Name: resources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resources (
    data_url character varying NOT NULL,
    resource_type character varying NOT NULL,
    json_metadata jsonb NOT NULL,
    layout jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    id uuid NOT NULL,
    dataset_id uuid,
    provenance_id uuid,
    is_queryable boolean DEFAULT true NOT NULL
);


ALTER TABLE public.resources OWNER TO postgres;

--
-- Name: resources_variables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resources_variables (
    resource_id uuid,
    variable_id uuid
);


ALTER TABLE public.resources_variables OWNER TO postgres;

--
-- Name: spatial_coverage_index; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.spatial_coverage_index (
    indexed_type character varying NOT NULL,
    spatial_coverage public.geometry,
    indexed_id uuid NOT NULL
);


ALTER TABLE public.spatial_coverage_index OWNER TO postgres;

--
-- Name: standard_variables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.standard_variables (
    ontology character varying NOT NULL,
    uri character varying NOT NULL,
    description character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE public.standard_variables OWNER TO postgres;

--
-- Name: temporal_coverage_index; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.temporal_coverage_index (
    indexed_type character varying NOT NULL,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone NOT NULL,
    indexed_id uuid
);


ALTER TABLE public.temporal_coverage_index OWNER TO postgres;

--
-- Name: variables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.variables (
    json_metadata jsonb NOT NULL,
    name character varying NOT NULL,
    id uuid NOT NULL,
    dataset_id uuid
);


ALTER TABLE public.variables OWNER TO postgres;

--
-- Name: variables_standard_variables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.variables_standard_variables (
    variable_id uuid,
    standard_variable_id uuid
);


ALTER TABLE public.variables_standard_variables OWNER TO postgres;

--
-- Name: edge_data edge_id; Type: DEFAULT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.edge_data ALTER COLUMN edge_id SET DEFAULT nextval('my_new_topo.edge_data_edge_id_seq'::regclass);


--
-- Name: face face_id; Type: DEFAULT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.face ALTER COLUMN face_id SET DEFAULT nextval('my_new_topo.face_face_id_seq'::regclass);


--
-- Name: node node_id; Type: DEFAULT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.node ALTER COLUMN node_id SET DEFAULT nextval('my_new_topo.node_node_id_seq'::regclass);


--
-- Data for Name: edge_data; Type: TABLE DATA; Schema: my_new_topo; Owner: postgres
--

COPY my_new_topo.edge_data (edge_id, start_node, end_node, next_left_edge, abs_next_left_edge, next_right_edge, abs_next_right_edge, left_face, right_face, geom) FROM stdin;
\.


--
-- Data for Name: face; Type: TABLE DATA; Schema: my_new_topo; Owner: postgres
--

COPY my_new_topo.face (face_id, mbr) FROM stdin;
0	\N
\.


--
-- Data for Name: node; Type: TABLE DATA; Schema: my_new_topo; Owner: postgres
--

COPY my_new_topo.node (node_id, containing_face, geom) FROM stdin;
\.


--
-- Data for Name: relation; Type: TABLE DATA; Schema: my_new_topo; Owner: postgres
--

COPY my_new_topo.relation (topogeo_id, layer_id, element_id, element_type) FROM stdin;
\.


--
-- Data for Name: datasets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.datasets (name, description, json_metadata, created_at, updated_at, id, provenance_id, tsv, spatial_coverage, temporal_coverage, temporal_coverage_start, temporal_coverage_end, variables_list, standard_variables_list) FROM stdin;
delete	delete test	{}	2021-01-15 21:10:16.600283	2021-01-15 21:12:07.150959	ca18126f-950a-40fb-be32-7fcf3236f4f1	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	'delet':1A,2 'test':3	\N	\N	\N	\N	\N	\N
new_name - outside of docker	Test dataset desription blag blah blah blah	{"variables": [{"@id": "blah"}, {"@id": "blah1"}], "new_metadata": "test"}	2021-01-19 22:24:52.672784	2021-01-19 22:24:52.672784	9d60263a-0f0e-426e-90c6-2c3ae5c2ed21	d5aff519-03a5-472e-b1e6-00ba49884179	'blag':9 'blah':10,11,12 'dataset':7 'desript':8 'docker':5A 'name':2A 'new':1A 'outsid':3A 'test':6	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: provenance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provenance (provenance_type, json_metadata, name, id) FROM stdin;
user	{"contact_information": {"email": "email@example.com"}}	test_user_xtw	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11
user	{"contact_information": {"email": "email@example.com"}}	test_api_outside	d5aff519-03a5-472e-b1e6-00ba49884179
\.


--
-- Data for Name: resources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.resources (data_url, resource_type, json_metadata, layout, created_at, updated_at, name, id, dataset_id, provenance_id, is_queryable) FROM stdin;
www.data_url_1.com	csv	{"spatial_coverage": {"type": "BoundingBox", "value": {"xmax": "-56.5", "xmin": 5, "ymax": "-5.5", "ymin": -5}}, "temporal_coverage": {"end_time": "2018-02-01T14:40:30", "start_time": "2018-01-01T14:40:30"}}	{}	2021-01-15 21:12:07.22056	2021-01-15 21:12:07.22056	2-variables file	7fc07e3b-3d34-42aa-8ce0-c394d5542eaa	ca18126f-950a-40fb-be32-7fcf3236f4f1	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	t
www.data_url_2.com	netcdf	{"spatial_coverage": {"type": "Point", "value": {"x": -118.47, "y": 34.0}}}	{}	2021-01-15 21:12:07.22056	2021-01-15 21:12:07.22056	1-variables file	e99ac19c-b75a-4684-a0aa-17c6af735557	ca18126f-950a-40fb-be32-7fcf3236f4f1	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	t
www.data_url_1.com	csv	{"spatial_coverage": {"type": "BoundingBox", "value": {"xmax": "-56.5", "xmin": 5, "ymax": "-5.5", "ymin": -5}}, "temporal_coverage": {"end_time": "2018-02-01T14:40:30", "start_time": "2018-01-01T14:40:30"}}	{}	2021-01-19 22:24:52.743853	2021-01-19 22:24:52.743853	2-variables file (outside)	dbda6a3e-580c-4522-bd31-aafbc7221b50	9d60263a-0f0e-426e-90c6-2c3ae5c2ed21	d5aff519-03a5-472e-b1e6-00ba49884179	t
www.data_url_2.com	NetCDF	{"new_metadata": 23, "spatial_coverage": {"type": "Point", "value": {"x": -118.47, "y": 34.0}}}	{}	2021-01-19 22:24:52.743853	2021-01-19 22:24:52.743853	0-variables file (outside)	3c8943a1-96d2-45d2-a21c-a1de3f12b2c9	9d60263a-0f0e-426e-90c6-2c3ae5c2ed21	d5aff519-03a5-472e-b1e6-00ba49884179	t
\.


--
-- Data for Name: resources_variables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.resources_variables (resource_id, variable_id) FROM stdin;
7fc07e3b-3d34-42aa-8ce0-c394d5542eaa	7152584f-0819-4c7d-8522-a09c20b925b6
7fc07e3b-3d34-42aa-8ce0-c394d5542eaa	0313fd35-74dd-41c2-9208-b39d1baf4ff5
e99ac19c-b75a-4684-a0aa-17c6af735557	7152584f-0819-4c7d-8522-a09c20b925b6
dbda6a3e-580c-4522-bd31-aafbc7221b50	8a5b0c38-a557-40d5-b57c-ae695fcd37c2
dbda6a3e-580c-4522-bd31-aafbc7221b50	f7fb84b7-88aa-4e43-b315-524a3b95111b
\.


--
-- Data for Name: spatial_coverage_index; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_coverage_index (indexed_type, spatial_coverage, indexed_id) FROM stdin;
RESOURCE	0103000020E61000000100000005000000000000000000144000000000000014C0000000000000144000000000000016C00000000000404CC000000000000016C00000000000404CC000000000000014C0000000000000144000000000000014C0	7fc07e3b-3d34-42aa-8ce0-c394d5542eaa
RESOURCE	0101000020E6100000AE47E17A149E5DC00000000000004140	e99ac19c-b75a-4684-a0aa-17c6af735557
RESOURCE	0103000020E61000000100000005000000000000000000144000000000000014C0000000000000144000000000000016C00000000000404CC000000000000016C00000000000404CC000000000000014C0000000000000144000000000000014C0	dbda6a3e-580c-4522-bd31-aafbc7221b50
RESOURCE	0101000020E6100000AE47E17A149E5DC00000000000004140	3c8943a1-96d2-45d2-a21c-a1de3f12b2c9
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: standard_variables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.standard_variables (ontology, uri, description, created_at, updated_at, name, id) FROM stdin;
GSN	www.example.com/sn1		2021-01-15 21:12:07.130095	2021-01-15 21:12:07.130095	sn1	5c6ccd58-53b2-5cee-a7d7-96ce3888ab87
GSN	www.example.com/sn2		2021-01-15 21:12:07.130095	2021-01-15 21:12:07.130095	sn2	3fb35cc2-56e5-540a-94a2-fab02f5139ce
OtherUPDSDFG	www.example.com/sn3		2021-01-15 21:12:07.130095	2021-01-15 21:12:07.130095	sn3	7529c859-83cb-563f-8cb8-3d6449fe237c
GSN	www.example.com/sn4		2021-01-15 21:12:07.130095	2021-01-15 21:12:07.130095	sn4	6cede7e3-927f-5c2c-b67e-2d7dccc622b4
GSN	www.example.com/sn5		2021-01-15 21:12:07.130095	2021-01-15 21:12:07.130095	sn5	3c3601a7-1c36-5dfa-8aac-12d07fd93258
GSN	www.example.com/sn6		2021-01-15 21:12:07.130095	2021-01-15 21:12:07.130095	sn6	7370308c-2e57-5a15-ae54-ead6e195835c
OtherUPDSDFG	www.example.com/sv1		2021-01-19 21:52:50.866523	2021-01-19 22:24:52.651068	sv1	b21bec34-b146-42bb-a9d5-fb5517779d53
OtherUPDSDFG	www.example.com/sv2		2021-01-19 21:52:50.866523	2021-01-19 22:24:52.651068	sv2	b1ee936a-681a-4d0e-ba47-4f0d30c22d39
OtherUPDSDFG	www.example.com/sv3		2021-01-19 21:52:50.866523	2021-01-19 22:24:52.651068	sv3	bb66eda6-0288-4e56-a575-a92e22e79504
GSN	www.example.com/sv4		2021-01-19 21:52:50.866523	2021-01-19 22:24:52.651068	sv4	bdcc6d85-9bc7-5111-be9b-d91fa4eccd1e
GSN	www.example.com/sv5		2021-01-19 21:52:50.866523	2021-01-19 22:24:52.651068	sv5	8e586aea-56fa-5217-a3ab-65b97c544c4b
GSN	www.example.com/sv6		2021-01-19 21:52:50.866523	2021-01-19 22:24:52.651068	sv6	11622bfc-ae2e-52df-a0ff-3b9819dd6ba2
\.


--
-- Data for Name: temporal_coverage_index; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.temporal_coverage_index (indexed_type, start_time, end_time, indexed_id) FROM stdin;
RESOURCE	2018-01-01 14:40:30	2018-02-01 14:40:30	7fc07e3b-3d34-42aa-8ce0-c394d5542eaa
RESOURCE	2018-01-01 14:40:30	2018-02-01 14:40:30	dbda6a3e-580c-4522-bd31-aafbc7221b50
\.


--
-- Data for Name: variables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.variables (json_metadata, name, id, dataset_id) FROM stdin;
{"unit": "mm s-1"}	var1-test	7152584f-0819-4c7d-8522-a09c20b925b6	ca18126f-950a-40fb-be32-7fcf3236f4f1
{"unit": "mm s-2"}	var2-test	0313fd35-74dd-41c2-9208-b39d1baf4ff5	ca18126f-950a-40fb-be32-7fcf3236f4f1
{"unit": "mm s-1"}	var1-test-outside	8a5b0c38-a557-40d5-b57c-ae695fcd37c2	9d60263a-0f0e-426e-90c6-2c3ae5c2ed21
{"unit": "mm s-2", "new_field": 343, "new_metadata": 23}	new variable name	f7fb84b7-88aa-4e43-b315-524a3b95111b	9d60263a-0f0e-426e-90c6-2c3ae5c2ed21
\.


--
-- Data for Name: variables_standard_variables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.variables_standard_variables (variable_id, standard_variable_id) FROM stdin;
7152584f-0819-4c7d-8522-a09c20b925b6	7529c859-83cb-563f-8cb8-3d6449fe237c
7152584f-0819-4c7d-8522-a09c20b925b6	6cede7e3-927f-5c2c-b67e-2d7dccc622b4
7152584f-0819-4c7d-8522-a09c20b925b6	3c3601a7-1c36-5dfa-8aac-12d07fd93258
0313fd35-74dd-41c2-9208-b39d1baf4ff5	7370308c-2e57-5a15-ae54-ead6e195835c
8a5b0c38-a557-40d5-b57c-ae695fcd37c2	b1ee936a-681a-4d0e-ba47-4f0d30c22d39
8a5b0c38-a557-40d5-b57c-ae695fcd37c2	bb66eda6-0288-4e56-a575-a92e22e79504
f7fb84b7-88aa-4e43-b315-524a3b95111b	b1ee936a-681a-4d0e-ba47-4f0d30c22d39
f7fb84b7-88aa-4e43-b315-524a3b95111b	8e586aea-56fa-5217-a3ab-65b97c544c4b
f7fb84b7-88aa-4e43-b315-524a3b95111b	bb66eda6-0288-4e56-a575-a92e22e79504
\.


--
-- Data for Name: geocode_settings; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.geocode_settings (name, setting, unit, category, short_desc) FROM stdin;
\.


--
-- Data for Name: pagc_gaz; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.pagc_gaz (id, seq, word, stdword, token, is_custom) FROM stdin;
\.


--
-- Data for Name: pagc_lex; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.pagc_lex (id, seq, word, stdword, token, is_custom) FROM stdin;
\.


--
-- Data for Name: pagc_rules; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.pagc_rules (id, rule, is_custom) FROM stdin;
\.


--
-- Data for Name: topology; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.topology (id, name, srid, "precision", hasz) FROM stdin;
1	my_new_topo	26986	0.5	f
\.


--
-- Data for Name: layer; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.layer (topology_id, layer_id, schema_name, table_name, feature_column, feature_type, level, child_id) FROM stdin;
\.


--
-- Name: edge_data_edge_id_seq; Type: SEQUENCE SET; Schema: my_new_topo; Owner: postgres
--

SELECT pg_catalog.setval('my_new_topo.edge_data_edge_id_seq', 1, false);


--
-- Name: face_face_id_seq; Type: SEQUENCE SET; Schema: my_new_topo; Owner: postgres
--

SELECT pg_catalog.setval('my_new_topo.face_face_id_seq', 1, false);


--
-- Name: layer_id_seq; Type: SEQUENCE SET; Schema: my_new_topo; Owner: postgres
--

SELECT pg_catalog.setval('my_new_topo.layer_id_seq', 1, false);


--
-- Name: node_node_id_seq; Type: SEQUENCE SET; Schema: my_new_topo; Owner: postgres
--

SELECT pg_catalog.setval('my_new_topo.node_node_id_seq', 1, false);


--
-- Name: edge_data edge_data_pkey; Type: CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.edge_data
    ADD CONSTRAINT edge_data_pkey PRIMARY KEY (edge_id);


--
-- Name: face face_primary_key; Type: CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.face
    ADD CONSTRAINT face_primary_key PRIMARY KEY (face_id);


--
-- Name: node node_primary_key; Type: CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.node
    ADD CONSTRAINT node_primary_key PRIMARY KEY (node_id);


--
-- Name: relation relation_layer_id_topogeo_id_element_id_element_type_key; Type: CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.relation
    ADD CONSTRAINT relation_layer_id_topogeo_id_element_id_element_type_key UNIQUE (layer_id, topogeo_id, element_id, element_type);


--
-- Name: edge_end_node_idx; Type: INDEX; Schema: my_new_topo; Owner: postgres
--

CREATE INDEX edge_end_node_idx ON my_new_topo.edge_data USING btree (end_node);


--
-- Name: edge_gist; Type: INDEX; Schema: my_new_topo; Owner: postgres
--

CREATE INDEX edge_gist ON my_new_topo.edge_data USING gist (geom);


--
-- Name: edge_left_face_idx; Type: INDEX; Schema: my_new_topo; Owner: postgres
--

CREATE INDEX edge_left_face_idx ON my_new_topo.edge_data USING btree (left_face);


--
-- Name: edge_right_face_idx; Type: INDEX; Schema: my_new_topo; Owner: postgres
--

CREATE INDEX edge_right_face_idx ON my_new_topo.edge_data USING btree (right_face);


--
-- Name: edge_start_node_idx; Type: INDEX; Schema: my_new_topo; Owner: postgres
--

CREATE INDEX edge_start_node_idx ON my_new_topo.edge_data USING btree (start_node);


--
-- Name: face_gist; Type: INDEX; Schema: my_new_topo; Owner: postgres
--

CREATE INDEX face_gist ON my_new_topo.face USING gist (mbr);


--
-- Name: node_gist; Type: INDEX; Schema: my_new_topo; Owner: postgres
--

CREATE INDEX node_gist ON my_new_topo.node USING gist (geom);


--
-- Name: datasets_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX datasets_id_key ON public.datasets USING btree (id);


--
-- Name: datasets_spatial_gix; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX datasets_spatial_gix ON public.datasets USING gist (spatial_coverage);


--
-- Name: datasets_tc_end_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX datasets_tc_end_idx ON public.datasets USING btree (temporal_coverage_end);


--
-- Name: datasets_tc_start_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX datasets_tc_start_idx ON public.datasets USING btree (temporal_coverage_start);


--
-- Name: idx_spatial_coverage_index_spatial_coverage; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_spatial_coverage_index_spatial_coverage ON public.spatial_coverage_index USING gist (spatial_coverage);


--
-- Name: idx_spatial_coverage_index_spatial_coverage_indexed_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_spatial_coverage_index_spatial_coverage_indexed_id ON public.spatial_coverage_index USING btree (spatial_coverage, indexed_id);


--
-- Name: ix_datasets_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_datasets_created_at ON public.datasets USING btree (created_at);


--
-- Name: ix_datasets_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_datasets_name ON public.datasets USING btree (name);


--
-- Name: ix_resources_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resources_created_at ON public.resources USING btree (created_at);


--
-- Name: ix_resources_dataset_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resources_dataset_id ON public.resources USING btree (dataset_id);


--
-- Name: ix_resources_provenance_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resources_provenance_id ON public.resources USING btree (provenance_id);


--
-- Name: ix_standard_variables_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_standard_variables_created_at ON public.standard_variables USING btree (created_at);


--
-- Name: ix_standard_variables_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_standard_variables_name ON public.standard_variables USING btree (name);


--
-- Name: ix_temporal_coverage_index_end_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_temporal_coverage_index_end_time ON public.temporal_coverage_index USING btree (end_time);


--
-- Name: ix_temporal_coverage_index_start_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_temporal_coverage_index_start_time ON public.temporal_coverage_index USING btree (start_time);


--
-- Name: provenance_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX provenance_id_key ON public.provenance USING btree (id);


--
-- Name: queryable_resource_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX queryable_resource_id_idx ON public.resources USING btree (id) WHERE (is_queryable = true);


--
-- Name: resources_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX resources_id_key ON public.resources USING btree (id);


--
-- Name: spatial_coverage_index_indexed_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX spatial_coverage_index_indexed_id_key ON public.spatial_coverage_index USING btree (indexed_id);


--
-- Name: standard_variables_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX standard_variables_id_key ON public.standard_variables USING btree (id);


--
-- Name: standard_variables_uri_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX standard_variables_uri_key ON public.standard_variables USING btree (uri);


--
-- Name: temporal_coverage_index_indexed_type_indexed_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX temporal_coverage_index_indexed_type_indexed_id_key ON public.temporal_coverage_index USING btree (indexed_type, indexed_id);


--
-- Name: tsv_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tsv_idx ON public.datasets USING gin (tsv);


--
-- Name: variables_dataset_id_name_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX variables_dataset_id_name_key ON public.variables USING btree (dataset_id, name);


--
-- Name: variables_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX variables_id_key ON public.variables USING btree (id);


--
-- Name: edge edge_insert_rule; Type: RULE; Schema: my_new_topo; Owner: postgres
--

CREATE RULE edge_insert_rule AS
    ON INSERT TO my_new_topo.edge DO INSTEAD  INSERT INTO my_new_topo.edge_data (edge_id, start_node, end_node, next_left_edge, abs_next_left_edge, next_right_edge, abs_next_right_edge, left_face, right_face, geom)
  VALUES (new.edge_id, new.start_node, new.end_node, new.next_left_edge, abs(new.next_left_edge), new.next_right_edge, abs(new.next_right_edge), new.left_face, new.right_face, new.geom);


--
-- Name: relation relation_integrity_checks; Type: TRIGGER; Schema: my_new_topo; Owner: postgres
--

CREATE TRIGGER relation_integrity_checks BEFORE INSERT OR UPDATE ON my_new_topo.relation FOR EACH ROW EXECUTE PROCEDURE topology.relationtrigger('1', 'my_new_topo');


--
-- Name: datasets datasets_tsv_update; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER datasets_tsv_update BEFORE INSERT OR UPDATE ON public.datasets FOR EACH ROW EXECUTE PROCEDURE public.datasets_tsv_trigger();


--
-- Name: edge_data end_node_exists; Type: FK CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.edge_data
    ADD CONSTRAINT end_node_exists FOREIGN KEY (end_node) REFERENCES my_new_topo.node(node_id);


--
-- Name: node face_exists; Type: FK CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.node
    ADD CONSTRAINT face_exists FOREIGN KEY (containing_face) REFERENCES my_new_topo.face(face_id);


--
-- Name: edge_data left_face_exists; Type: FK CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.edge_data
    ADD CONSTRAINT left_face_exists FOREIGN KEY (left_face) REFERENCES my_new_topo.face(face_id);


--
-- Name: edge_data next_left_edge_exists; Type: FK CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.edge_data
    ADD CONSTRAINT next_left_edge_exists FOREIGN KEY (abs_next_left_edge) REFERENCES my_new_topo.edge_data(edge_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: edge_data next_right_edge_exists; Type: FK CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.edge_data
    ADD CONSTRAINT next_right_edge_exists FOREIGN KEY (abs_next_right_edge) REFERENCES my_new_topo.edge_data(edge_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: edge_data right_face_exists; Type: FK CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.edge_data
    ADD CONSTRAINT right_face_exists FOREIGN KEY (right_face) REFERENCES my_new_topo.face(face_id);


--
-- Name: edge_data start_node_exists; Type: FK CONSTRAINT; Schema: my_new_topo; Owner: postgres
--

ALTER TABLE ONLY my_new_topo.edge_data
    ADD CONSTRAINT start_node_exists FOREIGN KEY (start_node) REFERENCES my_new_topo.node(node_id);


--
-- Name: datasets datasets_provenance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.datasets
    ADD CONSTRAINT datasets_provenance_id_fkey FOREIGN KEY (provenance_id) REFERENCES public.provenance(id);


--
-- Name: resources resources_dataset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resources
    ADD CONSTRAINT resources_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id);


--
-- Name: resources resources_provenance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resources
    ADD CONSTRAINT resources_provenance_id_fkey FOREIGN KEY (provenance_id) REFERENCES public.provenance(id);


--
-- Name: resources_variables resources_variables_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resources_variables
    ADD CONSTRAINT resources_variables_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.resources(id);


--
-- Name: resources_variables resources_variables_variable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resources_variables
    ADD CONSTRAINT resources_variables_variable_id_fkey FOREIGN KEY (variable_id) REFERENCES public.variables(id);


--
-- Name: variables variables_dataset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variables
    ADD CONSTRAINT variables_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id);


--
-- Name: variables_standard_variables variables_standard_variables_standard_variable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variables_standard_variables
    ADD CONSTRAINT variables_standard_variables_standard_variable_id_fkey FOREIGN KEY (standard_variable_id) REFERENCES public.standard_variables(id);


--
-- Name: variables_standard_variables variables_standard_variables_variable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.variables_standard_variables
    ADD CONSTRAINT variables_standard_variables_variable_id_fkey FOREIGN KEY (variable_id) REFERENCES public.variables(id);


--
-- PostgreSQL database dump complete
--

