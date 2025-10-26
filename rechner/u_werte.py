import pandas as pd




#U-Werte 

df_u_werte = pd.read_excel("/home/tryndaron/Schreibtisch/software_projekte/python_projectyx/energie_rechner/rechner/Aaron 16.10.25.xlsx", sheet_name="U-Werte")
df_u_werte = df_u_werte [ [" ", "bis 1918", "ab 1919", "ab 1949", "ab 1958", "ab 1969", "ab 1979", "ab 1984", "ab 1995", 2003]]
df_u_werte = df_u_werte.iloc[0:28]



#U-Wert Schichtaufbau Dämmerung (U-Wert Ermittlung) BEG

u_wert_schichtaufbau_daemmerung = pd.read_excel("/home/tryndaron/Schreibtisch/software_projekte/python_projectyx/energie_rechner/rechner/Aaron 16.10.25.xlsx", sheet_name="U-Werte")
u_wert_schichtaufbau_daemmerung = u_wert_schichtaufbau_daemmerung.iloc[0:30, 11:17]
u_wert_schichtaufbau_daemmerung.columns = ["d(m)", "λ", "R", "U", "None",  "Art"]
u_wert_schichtaufbau_daemmerung.drop("None", axis=1, inplace=True)
u_wert_schichtaufbau_daemmerung.dropna(inplace=True)
u_wert_schichtaufbau_daemmerung.drop(u_wert_schichtaufbau_daemmerung.index[0], inplace=True)
u_wert_schichtaufbau_daemmerung.reset_index(drop=True, inplace=True)


#print(u_wert_schichtaufbau_daemmerung)


#U-Wert Schichtaufbau Dämmung (U-Wert Ermittlung) GEG

u_wert_GEG = pd.read_excel("/home/tryndaron/Schreibtisch/software_projekte/python_projectyx/energie_rechner/rechner/Aaron 16.10.25.xlsx", sheet_name="U-Werte")

u_wert_GEG = u_wert_GEG.iloc[34:68, 11:17]
u_wert_GEG.columns = ["d(m)", "λ", "R", "U", "None",  "Art"]
u_wert_GEG.drop("None", axis=1, inplace=True)
u_wert_GEG.dropna(inplace=True)
u_wert_GEG.reset_index(drop=True, inplace=True)



print(u_wert_GEG)




