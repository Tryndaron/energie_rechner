import streamlit as st
import pandas as pd
import math
import os
import json
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile
import plotly.express as px
import plotly.graph_objects as go
import fixwerte  # Importiere Fixwerte aus separater Datei
from fixwerte import df_u_werte



# --- Styling direkt einbinden ---
def local_css(css: str):
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

local_css("""
/* Hintergrundfarben */
body {
    background-color: #f8f9fa;
    color: #212529;
}

/* Buttons */
div.stButton > button {
    background-color: #0066cc;
    color: white;
    border-radius: 8px;
    padding: 0.6em 1.2em;
    font-weight: 600;
    border: none;
}
div.stButton > button:hover {
    background-color: #004a99;
}

/* Überschriften */
h1, h2, h3 {
    color: #0066cc;
    font-family: "Segoe UI", sans-serif;
}

/* Eingabefelder */
input, select, textarea {
    border-radius: 6px !important;
    border: 1px solid #ccc !important;
    padding: 0.4em !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-weight: 600;
    color: #0066cc;
}
""")


def safe_text(text: str) -> str:
    return text.encode("latin-1", "replace").decode("latin-1")



# Datei für gespeicherte Werte
FILE = "saved_values.json"

# --- gespeicherte Werte laden ---


if os.path.exists(FILE):
    try:
        with open(FILE, "r") as f:
            saved_values = json.load(f)
            for key, val in saved_values.items():
                if key not in st.session_state:  # nur setzen, wenn noch nicht vorhanden
                    st.session_state[key] = val
    except Exception as e:
        st.warning(f"⚠️ Fehler beim Laden: {e}")






st.title(" Gebäudeberechnung")

# --- Eingaben ---

with st.expander("Kontaktdaten", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        Vorname = st.text_input("Vorname", key="Vorname")
        Nachname = st.text_input("Nachname", key="Nachname")
        Adresse = st.text_input("Adresse", key="adresse")
        Telefon = st.text_input("Telefon",  key="telefon")
        E_Mail = st.text_input("E-Mail", key="email")
    


with st.expander("Allgemein"):
    col1, col2 = st.columns(2)
    with col1:
        baujahr =  st.selectbox("Baujahr", [" ", "bis 1918", "ab 1919", "ab 1949", "ab 1958", "ab 1969", "ab 1979", "ab 1984", "ab 1995", 2003] )   #st.number_input("Baujahr", min_value=1800, max_value=2100, step=1, key="baujahr")
        personen = st.number_input("Personenzahl", min_value=1, step=1, key="personen")
        wohneinheiten = st.number_input("Wohneinheiten", min_value=1, step=1, key="wohneinheiten")
        wohnflaeche = st.number_input("Wohnfläche (m²)", min_value=1.0, key="wohnflaeche")
        grundrisslaenge = st.number_input("Grundrisslänge (m) (Auch für weitere Rechnungen wichtig !)", min_value=1.0, key="grundrisslaenge_allg")
        grundrissbreite = st.number_input("Grundrissbreite (m)", min_value=1.0, key="grundrissbreite_allg")
        freistehend = st.selectbox("Freistehend", ["Ja", "1-Seitig angebaut", "2-Seitig angebaut"], key="freistehend")
    

with st.expander("Dach + Dachgeschoss"):
    col1, col2 = st.columns(2)
    with col1:
        Art = st.text_input("Art", key="dach_art")
        dachneigung = st.number_input("Dachneigung (°)", min_value=0.0, max_value=90.0, key="dachneigung")
        dach_hoehe = st.number_input("Dachhöhe (m)", min_value=1.0, key="dach_hoehe")
        dach_dicke = st.number_input("Dachdicke (m)", min_value=0.0, key="dach_dicke")
        letzte_sanierung_dach = st.number_input("Letzte Sanierung (Dach)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_dach")
        beheizt = st.selectbox("Beheizt", ["Ja", "Nein"], key="dach_beheizt")
        Hoehe_dachboden = st.number_input("Höhe Dachboden (m)", min_value=1.0, key="hoehe_dachboden")
        hoehe_dachgeschoss = st.number_input("Höhe Dachgeschoss (m)", min_value=1.0, key="hoehe_dachgeschoss")
        ogd_gedämmt = st.selectbox("Oberste Geschossdecke gedämmt", ["Ja", "Nein"], key="ogd_gedämmt")
        kniestochhoehe = st.number_input("Kniestockhöhe (m)", min_value=0.0, key="kniestockhoehe")

with st.expander("Gauben"):
    col1, col2 = st.columns(2)
    with col1:
        gauben_wand_breite = st.number_input("Breite (m)", min_value=1.0, key="gaube_breite")
        gauben_wand_hoehe = st.number_input("Höhe (m)", min_value=1.0, key="hoehe_gaube")
        gauben_wand_tiefe = st.number_input("Tiefe (m)", min_value=1.0, key="gaube_tiefe")


with st.expander("Außenwand Nord (Falls die Außenwände alle gleich sind, die Gesamtlänge aller Außenwände hier eintragen)"):
    col1, col2 = st.columns(2)
    with col1:
        Hoehe_außenwand_nord = st.number_input("Höhe (m)", min_value=0.0, key="hoehe_aussenwand")
        Laenge_außenwand_nord = st.number_input("Länge (m)", min_value=1.0, key="laenge_aussenwand_nord")
        dicke_außenwand_nord = st.number_input("Dicke (m)", min_value=0.0, key="dicke_aussenwand_nord")
        letzte_sanierung_außenwand_nord = st.number_input("Letzte Sanierung (Außenwand 1)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_außenwand_nord")
        luftschicht_vorhanden_nord = st.selectbox("Luftschicht vorhanden", ["Ja", "Nein"], key="luftschicht_vorhanden_nord")


with st.expander("Außenwand Ost"):
    col1, col2 = st.columns(2)
    with col1:
        Hoehe_außenwand_ost = st.number_input("Höhe (m)", min_value=0.0, key="hoehe_aussenwand_ost")
        Laenge_außenwand_ost = st.number_input("Länge (m)", min_value=0.0, key="laenge_aussenwand_ost")
        dicke_außenwand_ost = st.number_input("Dicke (m)", min_value=0.0, key="dicke_aussenwand_ost")
        letzte_sanierung_außenwand_ost = st.number_input("Letzte Sanierung (Außenwand 2)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_außenwand_ost")
        luftschicht_vorhanden_ost = st.selectbox("Luftschicht vorhanden", ["Ja", "Nein"], key="luftschicht_vorhanden_ost")

with st.expander("Außenwand Süd"):
    col1, col2 = st.columns(2)
    with col1:
        Hoehe_außenwand_sued = st.number_input("Höhe (m)", min_value=0.0, key="hoehe_aussenwand Süd")
        Laenge_außenwand_sued = st.number_input("Länge (m)", min_value=0.0, key="laenge_aussenwand sued")
        dicke_außenwand_sued = st.number_input("Dicke (m)", min_value=0.0, key="dicke_aussenwand sued")
        letzte_sanierung_sued = st.number_input("Letzte Sanierung (Außenwand 2)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_außenwand sued")
        luftschicht_sued = st.selectbox("Luftschicht vorhanden", ["Ja", "Nein"], key="luftschicht_vorhandensued")

with st.expander("Außenwand West"):
    col1, col2 = st.columns(2)
    with col1:
        Hoehe_außenwand_west = st.number_input("Höhe (m)", min_value=0.0, key="hoehe_aussenwand West")
        Laenge_außenwand_west = st.number_input("Länge (m)", min_value=0.0, key="laenge_aussenwand West")
        dicke_außenwand_west = st.number_input("Dicke (m)", min_value=0.0, key="dicke_aussenwand West")
        letzte_sanierung_west = st.number_input("Letzte Sanierung (Außenwand West)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_außenwand_west")
        luftschicht_west = st.selectbox("Luftschicht vorhanden", ["Ja", "Nein"], key="luftschicht_vorhanden_west")

with st.expander("Kellerdecke"):
    col1, col2 = st.columns(2)
    with col1:
        art_kellerdecke = st.text_input("Art", key="art_kellerdecke")
        Hoehe_kellergeschoß = st.number_input("Höhe Kellergeschoss (m)", min_value=0.0, key="hoehe_kellergeschoss")
        letzte_sanierung_kellerdecke = st.number_input("Letzte Sanierung (Kellerdecke)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_kellerdecke")

with st.expander("Fenster"):
    col1, col2 = st.columns(2)
    with col1:
        art_fenster = st.text_input("Art", key="art_fenster")
        fenster_flaeche = st.number_input("Fensterfläche gesamt (m²)", min_value=1.0, key="fensterflaeche_allg")
        letzte_sanierung_fenster = st.number_input("Letzte Sanierung (Fenster)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_fenster")


with st.expander("Dachfenster"):
    col1, col2 = st.columns(2)
    with col1:
        art_dachfenster = st.text_input("Art", key="art_dachfenster")
        dachfenster_flaeche = st.number_input("Dachfensterfläche gesamt (m²)", min_value=0.0, key="dachfenster_flaeche")
        letzte_sanierung_dachfenster = st.number_input("Letzte Sanierung (Dachfenster)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_dachfenster")


with st.expander("Außentüren"):
    col1, col2 = st.columns(2)
    with col1:
        tuerflaeche_gesamt = st.number_input("Türfläche gesamt (m²)", min_value=1.0, key="tuerflaeche_gesamt")
        letzte_sanierung_tueren = st.number_input("Letzte Sanierung (Türen)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_tueren")


with st.expander("Keller (Kellerräume wenn sie beheizt sind)"):
    col1, col2 = st.columns(2)
    with col1:
        kelleraußenwand_Breite = st.number_input("Kelleraußenwand Breite (m)", min_value=0.0, key="kelleraußenwand_breite")
        kellerinnenwand_Breite = st.number_input("Kellerinnenwand Höhe (m)", min_value=0.0, key="kellerinnenwand_breite")
        keller_geschoss_hoehe = st.number_input("Kellergeschoss Höhe (m)", min_value=0.0, key="kellergeschoss_hoehe")
        #beheizte_kellerflaeche = st.number_input("Beheizte Kellerfläche (m²)", min_value=0.0, key="beheizte_kellerflaeche")
        kellertuer_fläche = st.number_input("Kellertür Fläche (m²)", min_value=0.0, key="kellertuer_flaeche")
        kellerfenster_flaeche = st.number_input("Kellerfenster Fläche (m²)", min_value=0.0, key="kellerfenster_flaeche")


with st.expander("Heizung"):
    col1, col2 = st.columns(2)
    with col1:
        heizung_typ = st.selectbox("Heizungstyp", ["Gas", "Öl", "Wärmepumpe", "Pellet", "Fernwärme", "Elektro", "Sonstige"], key="heizung_typ")
        heizung_baujahr = st.number_input("Baujahr Heizung", min_value=1900, max_value=2100, step=1, key="heizung_baujahr")
        heizung_leistung = st.number_input("Leistung (kW)", min_value=1.0, key="heizung_leistung")
        waermeabgabe = st.selectbox("Wäremabgabe", ["1-fach", "2-fach (standard)", "3-fach (selten)", "4-fach(sehr selten)"], key="waermeabgabe_typ")
        vorlauftemperatur_heizung = st.number_input("Vorlauftemperatur Heizung (°C)", min_value=1.0, key="vorlauftemperatur_heizung")
        vorlauftemperatur_warmwasser = st.number_input("Vorlauftemperatur Warmwasser (°C)", min_value=1.0, key="vorlauftemperatur_warmwasser")
        Oel = st.number_input("Öl (Liter/Jahr)", min_value=1.0, key="oel_verbrauch")
        Oel_preis = st.number_input("Ölpreis (€/Liter)", min_value=1.0, key="oel_preis")
        Gas = st.number_input("Gas (kWh/Jahr)", min_value=1.0, key="gas_verbrauch")
        Gas_preis = st.number_input("Gaspreis (€/kWh)", min_value=0.0, key="gas_preis")
        Pellet = st.number_input("Pellets (kg/Jahr)", min_value=1.0, key="pellet_verbrauch")
        Pellet_preis = st.number_input("Pelletpreis (€/kg)", min_value=1.0, key="pellet_preis")
        Kohle = st.number_input("Kohle (kg/Jahr)", min_value=1.0, key="kohle_verbrauch")
        Kohle_preis = st.number_input("Kohlepreis (€/kg)", min_value=1.0, key="kohle_preis")



with st.expander("Strom"):
    col1, col2 = st.columns(2)
    with col1:
        stromverbrauch = st.number_input("Stromverbrauch (kWh/Jahr)", min_value=1.0, key="stromverbrauch")
        strompreis = st.number_input("Strompreis (€/kWh)", min_value=0.0, key="strompreis")
    with col2:
        wasserverbrauch = st.number_input("Wasserverbrauch (m)", min_value=1.0, key="wasserverbrauch")

# --- Button ---
submitted = st.button("💾 Berechne")

# --- Speichern, wenn Button gedrückt ---
if submitted:
    with open(FILE, "w") as f:
        json.dump(st.session_state.to_dict(), f)

# --- Fixwerte 
entzugsleistung = 0.04
erdbohrung_kosten = 120
energie_quelle_strom = 0.4
energie_quelle_oekostrom = 0.03
luftwaerme = 2.5
klima_leistung = 2.5
passive_cooling_leistung = 0.4
passive_cooling_stunden = 900

faktor = 1.0
freistehend_faktor = 1.0

if freistehend == "Ja":
    freistehend_faktor = 1.0
elif freistehend == "1-Seitig angebaut":
    freistehend_faktor = 2
else:
    faktor = 0

    




# Beispiel: Backend-Berechnung
if submitted:
    

    DACH = {
        "Satteldach": math.sqrt((grundrissbreite /2)**2 + dach_hoehe**2) * grundrisslaenge * 2,
        "Flachdach": grundrisslaenge * grundrissbreite,
        "Oberste Geschossdecke": grundrisslaenge * grundrissbreite - 0.5 * (grundrisslaenge - 2*1) * (1 / (math.tan(math.radians(dachneigung)))),  # Annahme: Kniestockhöhe wirkt sich auf die Fläche aus
        "Oberste Geschossdecke mit Dachschrägenbereich": grundrisslaenge * grundrissbreite + 2 * (grundrisslaenge * (grundrissbreite/2 - 1)) * math.tan(math.radians(dachneigung)) ,  #* (grundrissbreite/(2 - 1)) * math.tan(math.radians(dachneigung)),
        "Dachschrägenbereich": (grundrisslaenge * grundrissbreite + 2 * (grundrisslaenge * (grundrissbreite/2 - 1)) * math.tan(math.radians(dachneigung))) - (grundrisslaenge * grundrissbreite - 0.5 * (grundrisslaenge - 2*1) * (1 / (math.tan(math.radians(dachneigung))))),           
    }


if submitted:

    AUẞENWAENDE = {
        "Außenwand Nord": ((2*grundrisslaenge + 2*grundrissbreite) * (Hoehe_außenwand_nord + kniestochhoehe)) - fenster_flaeche - tuerflaeche_gesamt,
        "Außenwand Ost": Laenge_außenwand_ost * Hoehe_außenwand_ost,
        "Außenwand Süd": Laenge_außenwand_sued * Hoehe_außenwand_sued,
        "Außenwand West": Laenge_außenwand_west * Hoehe_außenwand_west,
        "Giebelwand": faktor * ((grundrissbreite * dach_hoehe) / freistehend_faktor),
        "Gaubenwand": (gauben_wand_tiefe * gauben_wand_hoehe),        
    }

if submitted:
    FENSTER_TUEREN = {
        "Dachfenster": dachfenster_flaeche,
        "Fenster": fenster_flaeche,
        "Türen": tuerflaeche_gesamt,
    }

if submitted:
    KELLER = {
        "Kellerdecke": grundrisslaenge * grundrissbreite,
        "Kelleraußenwand_fläche": kelleraußenwand_Breite * keller_geschoss_hoehe, 
        "Kellerinnenwandfläche": kellerinnenwand_Breite * keller_geschoss_hoehe,
        "Kellertür Fläche": kellertuer_fläche,
        "Kellerfenster Fläche": kellerfenster_flaeche,
    }             

if submitted:
    GEBAEUDEGESAMTFLAECHE = {
        "Grundfläche": grundrisslaenge * grundrissbreite,
        "Hüllfläche oberste Gesfchossdecke": DACH["Oberste Geschossdecke mit Dachschrägenbereich"] + AUẞENWAENDE["Außenwand Nord"] + AUẞENWAENDE["Giebelwand"] + AUẞENWAENDE["Gaubenwand"] + KELLER["Kelleraußenwand_fläche"] + KELLER["Kellerinnenwandfläche"],
        "Hüllfläche schrägdach": DACH["Dachschrägenbereich"] + AUẞENWAENDE["Außenwand Nord"] + AUẞENWAENDE["Außenwand Ost"] + AUẞENWAENDE["Außenwand Süd"] + AUẞENWAENDE["Außenwand West"] + AUẞENWAENDE["Giebelwand"] + AUẞENWAENDE["Gaubenwand"] + KELLER["Kelleraußenwand_fläche"] + KELLER["Kellerinnenwandfläche"],
        "Beheizte Fläche": wohnflaeche,
        "Nutzfläche": wohnflaeche + ((2*grundrisslaenge + 2*grundrissbreite) * dicke_außenwand_nord ),
    }

if submitted:
    WAERMEVERLUSTE_ALT = {
        #"Dach": DACH["Satteldach"] * df_u_werte.loc[df_u_werte[" "] == "Dach", f"{baujahr}"].values[0],
    }

if submitted:
    WAERMEVERLUSTE_NEU = {
        #"Dach": DACH["Satteldach"] * df_u_werte.loc[df_u_werte[" "] == "Dach", f"{baujahr}"].values[0],
    }

if submitted:
    TRANSMISSIONSWAERMEVERLUSTE_ALT = {}

if submitted:
    TRANSMISSIONSWAERMEVERLUSTE_NEU = {}

if submitted:
    SPEZIFISCHER_TRANSMISSIONSWAERMEVERLUST_ALT = {}


if submitted:
    SPEZIFISCHER_TRANSMISSIONSWAERMEVERLUST_NEU = {}


if submitted:
    HUELLFLAECHENVERLUST_ALT = {}

if submitted:
    HUELFLAECHENVERLUST_NEU = {}


if submitted:
    WAERMEVERLUSTE_IN_KWH_ALT = {}

if submitted:
    WAERMEVERLUSTE_IN_KWH_NEU = {}

if submitted:
    EFFIZIENZKLASSE_ALT = {}

if submitted:
    EFFIZIENZKLASSE_NEU = {}

if submitted:
    PRIMÄRENERGIEBEDARF_ALT = {}

if submitted:
    PRIMÄRENERGIEBEDARF_NEU = {}





    df_dach = pd.DataFrame(DACH.items(), columns=["Parameter", "Wert"])
    df_außenwaende = pd.DataFrame(AUẞENWAENDE.items(), columns=["Parameter", "Wert"])
    st.subheader(" Dachflächen")  
    st.dataframe(DACH, use_container_width=True)
    st.subheader("Außenwände")
    st.dataframe(AUẞENWAENDE, use_container_width=True)
    st.subheader("Fenster und Türen")
    st.dataframe(FENSTER_TUEREN, use_container_width=True)
    st.subheader("Keller")
    st.dataframe(KELLER, use_container_width=True)
    st.subheader("Gebäudegesamtfläche")
    st.dataframe(GEBAEUDEGESAMTFLAECHE, use_container_width=True)
    st.subheader("Wärmeverluste")
    st.dataframe(WAERMEVERLUSTE_ALT, use_container_width=True)
    st.subheader("Wärmeverluste")
    st.dataframe(WAERMEVERLUSTE_NEU, use_container_width=True)




  



     
