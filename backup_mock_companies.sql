--
-- PostgreSQL database dump
--

\restrict fhHCA1ddHLwrlmSuNwog8AHr2Q784LKZTFsgcdj9XxLfDGJBOXfH16qqHLxgQuZ

-- Dumped from database version 16.11 (Debian 16.11-1.pgdg12+1)
-- Dumped by pg_dump version 16.11 (Debian 16.11-1.pgdg12+1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: mock_companies; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.mock_companies (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    industry character varying(100),
    revenue_millions numeric(10,2),
    employees integer,
    founded_year integer,
    website character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.mock_companies OWNER TO admin;

--
-- Name: mock_companies_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.mock_companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mock_companies_id_seq OWNER TO admin;

--
-- Name: mock_companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.mock_companies_id_seq OWNED BY public.mock_companies.id;


--
-- Name: mock_companies id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.mock_companies ALTER COLUMN id SET DEFAULT nextval('public.mock_companies_id_seq'::regclass);


--
-- Data for Name: mock_companies; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.mock_companies (id, name, industry, revenue_millions, employees, founded_year, website, created_at) FROM stdin;
1	Global Group 60	Retail	220.02	926	2000	www.globalgroup60.org	2025-12-22 07:58:00.599809
2	Blue Solutions	Manufacturing	348.31	4738	2018	www.bluesolutions.org	2025-12-22 07:58:00.599809
3	Global Corp	Manufacturing	262.96	786	1961	www.globalcorp.net	2025-12-22 07:58:00.599809
4	Tech Holdings	Transportation	369.25	2827	1975	www.techholdings.org	2025-12-22 07:58:00.599809
5	Alpha Inc	Energy	282.90	1078	1965	www.alphainc.com	2025-12-22 07:58:00.599809
6	Future Solutions	Finance	234.61	577	1998	www.futuresolutions.co	2025-12-22 07:58:00.599809
7	Future Ltd 42	Healthcare	178.20	2756	2008	www.futureltd42.com	2025-12-22 07:58:00.599809
8	Tech Inc	Retail	445.19	879	1999	www.techinc.org	2025-12-22 07:58:00.599809
9	Tech Corp	Energy	271.29	2723	1966	www.techcorp.io	2025-12-22 07:58:00.599809
10	Smart Inc	Finance	81.02	2717	2002	www.smartinc.org	2025-12-22 07:58:00.599809
11	Tech Systems 98	Healthcare	433.25	94	1992	www.techsystems98.co	2025-12-22 07:58:00.599809
12	Alpha Inc	Manufacturing	79.54	4010	2011	www.alphainc.io	2025-12-22 07:58:00.599809
13	Tech Solutions	Retail	331.06	4149	1966	www.techsolutions.com	2025-12-22 07:58:00.599809
14	Green Enterprises	Transportation	278.13	1625	2023	www.greenenterprises.com	2025-12-22 07:58:00.599809
15	Smart Systems	Energy	400.71	541	1985	www.smartsystems.org	2025-12-22 07:58:00.599809
16	Prime Corp	Energy	486.50	2147	2010	www.primecorp.io	2025-12-22 07:58:00.599809
17	Tech Technologies	Manufacturing	485.21	360	2013	www.techtechnologies.org	2025-12-22 07:58:00.599809
18	Global Technologies	Energy	27.25	1781	1999	www.globaltechnologies.org	2025-12-22 07:58:00.599809
19	Global Systems 72	Transportation	88.67	1156	1955	www.globalsystems72.com	2025-12-22 07:58:00.599809
20	Next Solutions	Finance	367.04	3846	1974	www.nextsolutions.net	2025-12-22 07:58:00.599809
21	Blue Innovations	Energy	45.33	778	2023	www.blueinnovations.com	2025-12-22 07:58:00.599809
22	Red Ltd	Real Estate	150.52	3162	1962	www.redltd.com	2025-12-22 07:58:00.599809
23	Red Ltd 75	Energy	198.83	2568	1996	www.redltd75.io	2025-12-22 07:58:00.599809
24	Smart Enterprises	Manufacturing	16.40	3470	1995	www.smartenterprises.com	2025-12-22 07:58:00.599809
25	Global Systems	Energy	61.47	2782	1963	www.globalsystems.net	2025-12-22 07:58:00.599809
26	Blue Systems	Energy	50.54	959	1955	www.bluesystems.com	2025-12-22 07:58:00.599809
27	Red Corp	Manufacturing	234.09	3197	1979	www.redcorp.com	2025-12-22 07:58:00.599809
28	Next Inc 32	Healthcare	235.79	2892	1956	www.nextinc32.io	2025-12-22 07:58:00.599809
29	Ultra Group	Healthcare	151.45	2471	2017	www.ultragroup.net	2025-12-22 07:58:00.599809
30	Prime Group	Technology	295.30	4557	1970	www.primegroup.net	2025-12-22 07:58:00.599809
31	Alpha Technologies	Energy	381.83	4906	1951	www.alphatechnologies.com	2025-12-22 07:58:00.599809
32	Prime Corp	Energy	182.77	1417	1952	www.primecorp.org	2025-12-22 07:58:00.599809
33	Future Ltd	Retail	381.35	4248	1960	www.futureltd.net	2025-12-22 07:58:00.599809
34	Blue Innovations	Transportation	208.50	3673	1953	www.blueinnovations.net	2025-12-22 07:58:00.599809
35	Future Inc	Healthcare	165.31	1048	1955	www.futureinc.io	2025-12-22 07:58:00.599809
36	Alpha Solutions	Transportation	491.64	4927	1963	www.alphasolutions.org	2025-12-22 07:58:00.599809
37	Red Enterprises	Healthcare	396.64	3580	2021	www.redenterprises.net	2025-12-22 07:58:00.599809
38	Alpha Holdings	Real Estate	150.73	4428	2005	www.alphaholdings.co	2025-12-22 07:58:00.599809
39	Smart Holdings 29	Real Estate	225.71	1333	1981	www.smartholdings29.co	2025-12-22 07:58:00.599809
40	Smart Corp	Finance	321.08	2363	2004	www.smartcorp.co	2025-12-22 07:58:00.599809
41	Tech Inc 73	Energy	103.99	3804	2001	www.techinc73.net	2025-12-22 07:58:00.599809
42	Smart Ltd	Real Estate	109.31	2127	1985	www.smartltd.com	2025-12-22 07:58:00.599809
43	Red Innovations	Retail	472.53	2096	1963	www.redinnovations.net	2025-12-22 07:58:00.599809
44	Tech Corp	Manufacturing	301.92	584	1954	www.techcorp.com	2025-12-22 07:58:00.599809
45	Ultra Holdings	Healthcare	95.09	1959	2010	www.ultraholdings.co	2025-12-22 07:58:00.599809
46	Smart Corp 96	Manufacturing	150.34	1640	1969	www.smartcorp96.io	2025-12-22 07:58:00.599809
47	Omega Solutions	Real Estate	219.25	3466	1983	www.omegasolutions.com	2025-12-22 07:58:00.599809
48	Prime Enterprises	Real Estate	11.34	3268	1973	www.primeenterprises.io	2025-12-22 07:58:00.599809
49	Omega Group	Real Estate	322.90	2554	1984	www.omegagroup.io	2025-12-22 07:58:00.599809
50	Alpha Innovations	Energy	499.16	1071	1969	www.alphainnovations.com	2025-12-22 07:58:00.599809
51	Alpha Technologies	Energy	83.13	1382	2016	www.alphatechnologies.com	2025-12-22 07:58:00.599809
52	Green Solutions	Finance	396.63	2937	1958	www.greensolutions.org	2025-12-22 07:58:00.599809
53	Global Innovations	Manufacturing	374.57	2373	1963	www.globalinnovations.net	2025-12-22 07:58:00.599809
54	Red Enterprises	Transportation	206.91	629	1952	www.redenterprises.org	2025-12-22 07:58:00.599809
55	Red Enterprises	Technology	264.84	3148	1999	www.redenterprises.co	2025-12-22 07:58:00.599809
56	Future Innovations	Technology	37.83	200	2009	www.futureinnovations.com	2025-12-22 07:58:00.599809
57	Green Holdings	Manufacturing	340.41	2244	2010	www.greenholdings.com	2025-12-22 07:58:00.599809
58	Blue Corp	Finance	93.63	3280	1981	www.bluecorp.org	2025-12-22 07:58:00.599809
59	Next Ltd	Real Estate	318.41	4981	1990	www.nextltd.com	2025-12-22 07:58:00.599809
60	Omega Inc	Healthcare	259.88	1894	2011	www.omegainc.co	2025-12-22 07:58:00.599809
61	Alpha Enterprises	Retail	19.55	1807	2021	www.alphaenterprises.io	2025-12-22 07:58:00.599809
62	Ultra Solutions	Technology	490.11	3879	1968	www.ultrasolutions.org	2025-12-22 07:58:00.599809
63	Future Technologies	Healthcare	286.97	959	1970	www.futuretechnologies.io	2025-12-22 07:58:00.599809
64	Prime Holdings	Manufacturing	151.30	3013	1985	www.primeholdings.com	2025-12-22 07:58:00.599809
65	Future Innovations 36	Manufacturing	55.05	1886	1991	www.futureinnovations36.io	2025-12-22 07:58:00.599809
66	Prime Technologies	Manufacturing	270.21	4575	1957	www.primetechnologies.io	2025-12-22 07:58:00.599809
67	Omega Group	Transportation	156.54	1892	2010	www.omegagroup.co	2025-12-22 07:58:00.599809
68	Tech Ltd	Manufacturing	158.05	3663	1980	www.techltd.net	2025-12-22 07:58:00.599809
69	Blue Group	Healthcare	486.05	1632	1992	www.bluegroup.io	2025-12-22 07:58:00.599809
70	Global Group 8	Real Estate	473.03	1960	1980	www.globalgroup8.org	2025-12-22 07:58:00.599809
71	Omega Holdings	Transportation	312.44	1140	1982	www.omegaholdings.co	2025-12-22 07:58:00.599809
72	Global Holdings	Energy	437.59	750	1984	www.globalholdings.co	2025-12-22 07:58:00.599809
73	Tech Enterprises	Transportation	408.18	2647	1968	www.techenterprises.org	2025-12-22 07:58:00.599809
74	Global Solutions	Transportation	422.81	2206	2018	www.globalsolutions.org	2025-12-22 07:58:00.599809
75	Prime Corp	Real Estate	182.93	2895	1962	www.primecorp.io	2025-12-22 07:58:00.599809
76	Smart Enterprises	Healthcare	300.07	506	2021	www.smartenterprises.com	2025-12-22 07:58:00.599809
77	Red Technologies	Finance	306.03	641	1958	www.redtechnologies.co	2025-12-22 07:58:00.599809
78	Prime Holdings	Real Estate	178.27	3254	1975	www.primeholdings.co	2025-12-22 07:58:00.599809
79	Future Solutions	Transportation	239.92	2187	2013	www.futuresolutions.net	2025-12-22 07:58:00.599809
80	Global Enterprises 39	Technology	485.50	1936	2003	www.globalenterprises39.com	2025-12-22 07:58:00.599809
81	Blue Inc	Healthcare	118.29	1517	1965	www.blueinc.com	2025-12-22 07:58:00.599809
82	Tech Technologies	Healthcare	397.99	3049	2011	www.techtechnologies.io	2025-12-22 07:58:00.599809
83	Red Corp	Retail	44.23	4859	1952	www.redcorp.net	2025-12-22 07:58:00.599809
84	Next Systems	Technology	35.80	4856	2017	www.nextsystems.io	2025-12-22 07:58:00.599809
85	Smart Holdings	Energy	134.80	3606	1967	www.smartholdings.io	2025-12-22 07:58:00.599809
86	Ultra Group	Finance	259.42	1399	1994	www.ultragroup.com	2025-12-22 07:58:00.599809
87	Ultra Inc	Real Estate	399.37	4287	1970	www.ultrainc.io	2025-12-22 07:58:00.599809
88	Future Inc	Manufacturing	59.64	4995	1957	www.futureinc.co	2025-12-22 07:58:00.599809
89	Global Technologies	Transportation	124.56	2420	2018	www.globaltechnologies.co	2025-12-22 07:58:00.599809
90	Blue Inc	Real Estate	127.22	2603	1996	www.blueinc.org	2025-12-22 07:58:00.599809
91	Blue Technologies	Finance	153.03	4501	1955	www.bluetechnologies.net	2025-12-22 07:58:00.599809
92	Alpha Enterprises	Transportation	204.62	4470	2019	www.alphaenterprises.co	2025-12-22 07:58:00.599809
93	Tech Solutions 28	Energy	69.08	4543	1970	www.techsolutions28.org	2025-12-22 07:58:00.599809
94	Ultra Systems 92	Manufacturing	28.02	4060	1967	www.ultrasystems92.co	2025-12-22 07:58:00.599809
95	Ultra Systems	Energy	12.64	1474	2017	www.ultrasystems.net	2025-12-22 07:58:00.599809
96	Next Group 56	Retail	472.24	3415	1970	www.nextgroup56.io	2025-12-22 07:58:00.599809
97	Alpha Ltd	Healthcare	258.27	4185	1987	www.alphaltd.net	2025-12-22 07:58:00.599809
98	Prime Innovations	Healthcare	217.74	2885	1966	www.primeinnovations.net	2025-12-22 07:58:00.599809
99	Alpha Corp	Finance	380.48	4489	1976	www.alphacorp.com	2025-12-22 07:58:00.599809
100	Omega Inc	Healthcare	315.27	3354	1994	www.omegainc.com	2025-12-22 07:58:00.599809
\.


--
-- Name: mock_companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.mock_companies_id_seq', 100, true);


--
-- Name: mock_companies mock_companies_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.mock_companies
    ADD CONSTRAINT mock_companies_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict fhHCA1ddHLwrlmSuNwog8AHr2Q784LKZTFsgcdj9XxLfDGJBOXfH16qqHLxgQuZ

