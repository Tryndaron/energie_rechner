import pandas as pd





entzugsleistung = 0.04
erdbohrung_kosten = 120
energie_quelle_strom = 0.4
energie_quelle_oekostrom = 0.03
luftwaerme = 2.5
klima_leistung = 2.5
passive_cooling_leistung = 0.4
passive_cooling_stunden = 900



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

}

#U-Werte

df_u_werte = pd.read_excel("/home/tryndaron/Schreibtisch/software_projekte/python_projectyx/energie_rechner/rechner/Aaron 16.10.25.xlsx", sheet_name="U-Werte")

print(df_u_werte.columns)


df_u_werte = df_u_werte [ [" ", "bis 1918", "ab 1919", "ab 1949", "ab 1958", "ab 1969", "ab 1979", "ab 1984", "ab 1995", 2003]]
df_u_werte = df_u_werte.iloc[0:28]

print(df_u_werte)











#print(DACHNEIGUNG_WERTE[15])


""" if heizung == "Gas":
    kg_co2_alt = gasverbrauch * 0.25
elif heizung == "Öl":
    kg_co2_alt = gasverbrauch * 0.6
else:
    kg_co2_alt = 0 """