import pandas as pd

entzugsleistung = 0.04
erdbohrung_kosten = 120
energie_quelle_strom = 0.4
energie_quelle_oekostrom = 0.03
luftwaerme = 2.5
klima_leistung = 2.5
passive_cooling_leistung = 0.4
passive_cooling_stunden = 900


#Korrekturwerte Trans.HT

SATTELDACH_DB_AUSGEBAUT = 1.00
SATTELDACH_DB_NICHTAUSGEBAUT = 0.9
OGD_DACH_AUSGEBAUT = 1.0
OGD_DACH_NICHTAUSGEBAUT = 0.8
WAENDE_UND_DECKEN_ZU_ABSEITEN = 0.8
WAENDE_UND_DECKEN_ZU_UNBEHEIZTEN_RAEUMEN = 0.5
WAENDE_UND_DECKEN_ZU_NIEDDRIGBEHEIZTEN_RAEUMEN = 0.35
KELLERDECKE_KG_UNBEHEIZT = 0.5
KELLERDECKE_KG_BEHEIZT = 0.9
KELLERBODEN_UNBEHEIZT = 0.6
KELLERBODEN_BEHEIZT = 0.6     # Ben nochmal fragen , da hier beheizt und unbeheizt gleich sind






#Energiequellen

STROM = 0.4
OEKOSTROM = 0.03
ERDGAS = 0.06
HEIZOEL = 0.6
PELLETS = 0.10

#Dachneigung werte paar

DACHNEIGUNG_WERTE =  {
10:	1.0154,
11:	1.0187,
12: 1.0223,
13	:1.0263,
14	:1.0306,
15	:1.0352,
16	:1.0402,
17	:1.0456,
18	:1.0514,
19	:1.0576,
20	:1.0641,
21	:1.0711,
22	:1.0785,
23	:1.0863,
24	:1.0946,
25	:1.1033,
26	:1.1126,
27	:1.1223,
28	:1.1325,
29	:1.1433,
30	:1.1547,
31	:1.1666,
32	:1.1791,
33	:1.1923,
34	:1.2062,
35	:1.2207,

36	:1.236,
37	:1.2521,
38	:1.2684,
39	:1.2858,
40	:1.3040,
41	:1.3230,
42	:1.3429,
43	:1.3637,
44	:1.3854,
45	:1.4080,
46	:1.4316,
47	:1.4562,
48	:1.4818,
49	:1.5085,
50	:1.5363,
51  :1.589,
52    :1.6242,
53    :1.6616,
54    :1.7013,
55    :1.7433,
56    :1.7882,
57    :1.836,
58    :1.8867,
59    :1.9416,
60    :2.0,
61    :2.0626,
62    :2.13,
63    :2.203,
64    :2.2811,
65    :2.3666,
66    :2.4585,
67    :2.5593,
68    :2.6694,
69    :2.7904,
70    :2.9238,
}


#Korrekturwerte 












#print(DACHNEIGUNG_WERTE[15])