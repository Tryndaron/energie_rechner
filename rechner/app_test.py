import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import math

from fixwerte import (SATTELDACH_DB_AUSGEBAUT, SATTELDACH_DB_NICHTAUSGEBAUT, 
                      OGD_DACH_AUSGEBAUT, OGD_DACH_NICHTAUSGEBAUT,
                      WAENDE_UND_DECKEN_ZU_ABSEITEN)



st.markdown(
    """
    <style>
    /* Gesamter App-Hintergrund */
    .stApp {
        background-color: #f1f8f4;  /* leichtes Grün */
        color: #000000;              /* schwarze Schrift im Hauptbereich */
    }

    /* Sidebar Hintergrund + Schrift */
    section[data-testid="stSidebar"] {
        background-color: #e4f3ea;
        color: #000000 !important;   /* schwarze Schrift in Sidebar */
    }

    /* Sidebar Labels, Überschriften, Inputs */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p {
        color: #000000 !important;   /* alle Texte schwarz */
    }

    /* Buttons */
    div.stButton > button {
        background-color: #0066cc;
        color: white;                /* Schrift bleibt weiß */
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-weight: 600;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #004a99;
    }

    /* Karten / Container */
    div[data-testid="metric-container"],
    div[data-testid="stExpander"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        color: #000000;              /* schwarze Schrift */
    }

    /* Expander Überschrift */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #000000 !important;   /* schwarz */
    }

    /* Überschriften */
    h1, h2, h3 {
        color: #000000;              /* schwarz */
    }

    /* Text im Hauptteil */
    div[data-testid="stMarkdownContainer"] {
        color: #000000;              /* schwarz */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================
# FIXWERTE
# =====================================================










# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Gebäudeenergieberechnung",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# SESSION FILE
# =====================================================
FILE = "saved_values.json"

if os.path.exists(FILE):
    try:
        with open(FILE, "r") as f:
            saved = json.load(f)
            for k, v in saved.items():
                if k not in st.session_state:
                    st.session_state[k] = v
    except:
        pass

# =====================================================
# SIDEBAR – EINGABEN
# =====================================================
with st.sidebar:
    st.title("🏠 Gebäuderechner")
    
    navigation = st.radio(
        "Navigation",
        ["📋 Eingaben", "📊 Ergebnisse", "📄 PDF"]
    )

    st.markdown("---")

    with st.expander("👤 Kontaktdaten", expanded=True):
        Vorname = st.text_input("Vorname", key="Vorname")
        Nachname = st.text_input("Nachname", key="Nachname")
        Adresse = st.text_input("Adresse", key="adresse")
        Telefon = st.text_input("Telefon",  key="telefon")
        E_Mail = st.text_input("E-Mail", key="email")

    with st.expander("🏗️ Allgemein"):
        baujahr = st.selectbox(
            "Baujahr",
            ["bis 1918", "ab 1919", "ab 1949", "ab 1958",
             "ab 1969", "ab 1979", "ab 1984", "ab 1995", "ab 2003"]
        )
        wohnflaeche = st.number_input("Wohnfläche (m²)", min_value=1.0, key="wohnflaeche")
        grundrisslaenge = st.number_input("Grundrisslänge (m)", min_value=1.0, key="grundrisslaenge")
        grundrissbreite = st.number_input("Grundrissbreite (m)", min_value=1.0, key="grundrissbreite")
        freistehend = st.selectbox("Freistehend", ["Ja", "1-Seitig angebaut", "2-Seitig angebaut"], key="freistehend")
        personen = st.number_input("Personenzahl", min_value=1, step=1, key="personen")

    with st.expander("🏠 Dach + Dachgeschoss"):
        Art = st.text_input("Art", key="dach_art")
        dachneigung = st.number_input("Dachneigung (°)", 0.0, 90.0, key="dachneigung")
        dach_hoehe = st.number_input("Dachhöhe (m)", min_value=1.0, key="dach_hoehe")
        dach_dicke = st.number_input("Dachdicke (m)", min_value=0.0, key="dach_dicke")
        letzte_sanierung_dach = st.number_input("Letzte Sanierung (Dach)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_dach")
        beheizt = st.selectbox("Beheizt", ["Ja", "Nein"], key="dach_beheizt")
        Hoehe_dachboden = st.number_input("Höhe Dachboden (m)", min_value=1.0, key="hoehe_dachboden")
        hoehe_dachgeschoss = st.number_input("Höhe Dachgeschoss (m)", min_value=1.0, key="hoehe_dachgeschoss")
        ogd_gedämmt = st.selectbox("Oberste Geschossdecke gedämmt", ["Ja", "Nein"], key="ogd_gedämmt")
        kniestochhoehe = st.number_input("Kniestockhöhe (m)", min_value=0.0, key="kniestockhoehe")

    with st.expander("Gauben"):
        gauben_wand_breite = st.number_input("Breite (m)", min_value=1.0, key="gaube_breite")
        gauben_wand_hoehe = st.number_input("Höhe (m)", min_value=1.0, key="hoehe_gaube")
        gauben_wand_tiefe = st.number_input("Tiefe (m)", min_value=1.0, key="gaube_tiefe")


    with st.expander("Außenwand Nord (Falls die Außenwände alle gleich sind, die Gesamtlänge aller Außenwände hier eintragen"):
        Hoehe_außenwand_nord = st.number_input("Höhe (m)", min_value=0.0, key="hoehe_aussenwand")
        Laenge_außenwand_nord = st.number_input("Länge (m)", min_value=1.0, key="laenge_aussenwand_nord")
        dicke_außenwand_nord = st.number_input("Dicke (m)", min_value=0.0, key="dicke_aussenwand_nord")
        letzte_sanierung_außenwand_nord = st.number_input("Letzte Sanierung (Außenwand 1)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_außenwand_nord")
        luftschicht_vorhanden_nord = st.selectbox("Luftschicht vorhanden", ["Ja", "Nein"], key="luftschicht_vorhanden_nord")

    with st.expander("Außenwand Ost"):
        Hoehe_außenwand_ost = st.number_input("Höhe (m)", min_value=0.0, key="hoehe_aussenwand_ost")
        Laenge_außenwand_ost = st.number_input("Länge (m)", min_value=0.0, key="laenge_aussenwand_ost")
        dicke_außenwand_ost = st.number_input("Dicke (m)", min_value=0.0, key="dicke_aussenwand_ost")
        letzte_sanierung_außenwand_ost = st.number_input("Letzte Sanierung (Außenwand 2)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_außenwand_ost")
        luftschicht_vorhanden_ost = st.selectbox("Luftschicht vorhanden", ["Ja", "Nein"], key="luftschicht_vorhanden_ost")


    with st.expander("Außenwand Süd"):
        Hoehe_außenwand_sued = st.number_input("Höhe (m)", min_value=0.0, key="hoehe_aussenwand Süd")
        Laenge_außenwand_sued = st.number_input("Länge (m)", min_value=0.0, key="laenge_aussenwand sued")
        dicke_außenwand_sued = st.number_input("Dicke (m)", min_value=0.0, key="dicke_aussenwand sued")
        letzte_sanierung_sued = st.number_input("Letzte Sanierung (Außenwand 2)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_außenwand sued")
        luftschicht_sued = st.selectbox("Luftschicht vorhanden", ["Ja", "Nein"], key="luftschicht_vorhandensued")

    with st.expander("Außenwand West"):
        Hoehe_außenwand_west = st.number_input("Höhe (m)", min_value=0.0, key="hoehe_aussenwand West")
        Laenge_außenwand_west = st.number_input("Länge (m)", min_value=0.0, key="laenge_aussenwand West")
        dicke_außenwand_west = st.number_input("Dicke (m)", min_value=0.0, key="dicke_aussenwand West")
        letzte_sanierung_west = st.number_input("Letzte Sanierung (Außenwand West)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_außenwand_west")
        luftschicht_west = st.selectbox("Luftschicht vorhanden", ["Ja", "Nein"], key="luftschicht_vorhanden_west")

    with st.expander("Kellerdecke"):
        art_kellerdecke = st.text_input("Art", key="art_kellerdecke")
        Hoehe_kellergeschoß = st.number_input("Höhe Kellergeschoss (m)", min_value=0.0, key="hoehe_kellergeschoss")
        letzte_sanierung_kellerdecke = st.number_input("Letzte Sanierung (Kellerdecke)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_kellerdecke")

    with st.expander("Fenster"):
        art_fenster = st.text_input("Art", key="art_fenster")
        fenster_flaeche = st.number_input("Fensterfläche gesamt (m²)", min_value=1.0, key="fensterflaeche_allg")
        letzte_sanierung_fenster = st.number_input("Letzte Sanierung (Fenster)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_fenster")

    with st.expander("Dachfester"):
        art_dachfenster = st.text_input("Art", key="art_dachfenster")
        dachfenster_flaeche = st.number_input("Dachfensterfläche gesamt (m²)", min_value=0.0, key="dachfenster_flaeche")
        letzte_sanierung_dachfenster = st.number_input("Letzte Sanierung (Dachfenster)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_dachfenster")

    with st.expander("Außentüren"):
        tuerflaeche_gesamt = st.number_input("Türfläche gesamt (m²)", min_value=1.0, key="tuerflaeche_gesamt")
        letzte_sanierung_tueren = st.number_input("Letzte Sanierung (Türen)", min_value=1900, max_value=2100, step=1, key="letzte_sanierung_tueren")

    with st.expander("Keller (Kellerräume wenn sie beheizt sind)"):
        kelleraußenwand_Breite = st.number_input("Kelleraußenwand Breite (m)", min_value=0.0, key="kelleraußenwand_breite")
        kellerinnenwand_Breite = st.number_input("Kellerinnenwand Höhe (m)", min_value=0.0, key="kellerinnenwand_breite")
        keller_geschoss_hoehe = st.number_input("Kellergeschoss Höhe (m)", min_value=0.0, key="kellergeschoss_hoehe")
        #beheizte_kellerflaeche = st.number_input("Beheizte Kellerfläche (m²)", min_value=0.0, key="beheizte_kellerflaeche")
        kellertuer_fläche = st.number_input("Kellertür Fläche (m²)", min_value=0.0, key="kellertuer_flaeche")
        kellerfenster_flaeche = st.number_input("Kellerfenster Fläche (m²)", min_value=0.0, key="kellerfenster_flaeche")







    with st.expander("🔥 Heizung"):
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
        stromverbrauch = st.number_input("Stromverbrauch (kWh/Jahr)", min_value=1.0, key="stromverbrauch")
        strompreis = st.number_input("Strompreis (€/kWh)", min_value=0.0, key="strompreis")
        wasserverbrauch = st.number_input("Wasserverbrauch (m)", min_value=1.0, key="wasserverbrauch")



    st.markdown("---")
    submitted = st.button("💾 Berechnen", use_container_width=True)

# =====================================================
# SAVE STATE
# =====================================================
if submitted:
    with open(FILE, "w") as f:
        json.dump(st.session_state.to_dict(), f)

# =====================================================
# MAIN CONTENT
# =====================================================
st.title("📊 Gebäudeberechnung")

if not submitted:
    st.info("⬅️ Bitte links alle Eingaben ausfüllen und **Berechnen** klicken.")
    st.stop()

# =====================================================
# >>>>> HIER BEGINNT DEINE BESTEHENDE BERECHNUNGSLOGIK <<<<<
# (Beispiel – ersetze nichts, füge nur ein)
# =====================================================

DACHFLAECHE = grundrisslaenge * grundrissbreite
HEIZLAST_ALT = 19.6
HEIZLAST_NEU = 6.8
EFF_ALT = 185
EFF_NEU = 78
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


if submitted:
    DACH = {
        "Satteldach": math.sqrt((grundrissbreite /2)**2 + dach_hoehe**2) * grundrisslaenge * 2,
        "Gaubendach": gauben_wand_breite * gauben_wand_tiefe,
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
   GESAMTVERLUST_DACH_ALT = {
        "Dach_alt":  int(SATTELDACH_DB_AUSGEBAUT) * 0.8 * int(DACH["Satteldach"]),
        
        "Gaubendach_alt":  int(SATTELDACH_DB_AUSGEBAUT) * 0.8 * int(DACH["Gaubendach"]),
        
        "Oberste Geschossdecke_alt": (int(OGD_DACH_AUSGEBAUT) * 0.6 * int(DACH["Oberste Geschossdecke"])
                                      if beheizt == "Ja"
                                        else int(OGD_DACH_NICHTAUSGEBAUT) * df_u_werte.loc[3, f'{baujahr}'] * int(DACH["Oberste Geschossdecke"])),
        
        "AUßenwand_alt":  int(AUẞENWAENDE["Außenwand Nord"]),
        
        "Giebelwand_alt":  int(AUẞENWAENDE["Giebelwand"]),
        
        "Gaubenwand_alt":   int(AUẞENWAENDE["Gaubenwand"]),
        
        "Dachfenster_alt":  2.7 * int(FENSTER_TUEREN["Dachfenster"]),
        
        "Fenster_alt":  2.7 * int(FENSTER_TUEREN["Fenster"]),
        
        "Außentueren_alt":  3.5 * int(FENSTER_TUEREN["Türen"]),
        
        "Kellerdecke_alt":  int(Hoehe_kellergeschoß),
        
        "Kelleraußenwand_alt": 0,
        
        "Kellerinnenwand_alt": 0,
        
        "Kellerfenster_alt": 0,
        
        "Kellerboden_alt": 0,
    }
   
if submitted:
    GESAMTVERLUST_DACH_NEU = {
        "Dach_neu":  int(SATTELDACH_DB_AUSGEBAUT) * 0.14 * int(DACH["Satteldach"]),
        "Gaubendach_neu":  int(SATTELDACH_DB_AUSGEBAUT) * 0.14 * int(DACH["Gaubendach"]),
        "Oberste Geschossdecke_neu": int(OGD_DACH_AUSGEBAUT) * 0.14 * int(DACH["Oberste Geschossdecke"]),
        "AUßenwand_neu":  0.2 * int(AUẞENWAENDE["Außenwand Nord"]),
        "Giebelwand_neu":  0.2 * int(AUẞENWAENDE["Giebelwand"]),
        "Gaubenwand_neu": 0.2 * int(AUẞENWAENDE["Gaubenwand"]),
        "Dachfenster_neu":   int(FENSTER_TUEREN["Dachfenster"]),
        "Fenster_neu":  0.95 * int(FENSTER_TUEREN["Fenster"]),
        "Außentueren_neu": 1.3 * int(FENSTER_TUEREN["Türen"]),
        "Kellerdecke_neu": 0.25 * int(Hoehe_kellergeschoß),
        "Kelleraußenwand_neu": 0,
        "Kellerinnenwand_neu": 0,
        "Kellerfenster_neu": 0,
        "Kellerboden_neu": 0,
    }

if submitted:
    GESAMTWAERMEVERLUST = {
        "Gesamtwaermeverlust_alt": sum(GESAMTVERLUST_DACH_ALT.values()),
        "Gesamtwaermeverlust_neu": sum(GESAMTVERLUST_DACH_NEU.values()),
    }


#print(GESAMTVERLUST_DACH["Dach_alt"])

if submitted:
    TRANSMISSIONSWAERMEVERLUSTE = {
        "Dach_transmissions_waermeverlust_alt": 30 * int(GESAMTVERLUST_DACH_ALT["Dach_alt"]) * 4000 / 1000, #* int(SATTELDACH_DB_AUSGEBAUT) * df_u_werte.loc[2, f'{baujahr}'] * int(DACH["Satteldach"]),
        "Dach_transmissions_waermeverlust_neu": 30 * int(GESAMTVERLUST_DACH_NEU["Dach_neu"]) * 2500 / 1000,
        "Gaubendach_transmissions_waermeverlust_alt": 30 * int(GESAMTVERLUST_DACH_ALT["Gaubendach_alt"]) * 4000 / 1000,
        "Gaubendach_transmissions_waermeverlust_neu": 30 * int(GESAMTVERLUST_DACH_NEU["Gaubendach_neu"]) * 2400 / 1000,
        "Oberste_Geschossdecke_transmissions_waermeverlust_alt": 30 * int(GESAMTVERLUST_DACH_ALT["Oberste Geschossdecke_alt"]) * 3000 / 1000,
        "Oberste_Geschossdecke_transmissions_waermeverlust_neu": 30 * int(GESAMTVERLUST_DACH_NEU["Oberste Geschossdecke_neu"]) * 1500 / 1000,
        "Außenwaende_transmissions_waermeverlust_alt": 30 * int(GESAMTVERLUST_DACH_ALT["AUßenwand_alt"]) * 3500 / 1000,
        "Außenwaende_transmissions_waermeverlust_neu": 30 * int(GESAMTVERLUST_DACH_NEU["AUßenwand_neu"]) * 1200 / 1000,
        "Giebelwand_transmissions_waermeverlust_alt": 30 * int(GESAMTVERLUST_DACH_ALT["Giebelwand_alt"]) * 2400 / 1000,
        "Gaubenwand_transmissions_waermeverlust_alt": 30 * int(GESAMTVERLUST_DACH_ALT["Gaubenwand_alt"]) * 4000 / 1000,
        "Gaubenwand_transmissions_waermeverlust_neu": 30 * int(GESAMTVERLUST_DACH_NEU["Gaubenwand_neu"]) * 2400 / 1000,
        "Dachfenster_transmissions_waermeverlust_alt": 30 * int(GESAMTVERLUST_DACH_ALT["Dachfenster_alt"]) * 2700 / 1000,
        "Fenster_transmissions_waermeverlust_alt": 30 * int(GESAMTVERLUST_DACH_ALT["Fenster_alt"]) * 2700 / 1000,
        "Außentueren_transmissions_waermeverlust_alt": 30 * int(GESAMTVERLUST_DACH_ALT["Außentueren_alt"]) * 4000 / 1000,
        "Außentueren_transmissions_waermeverlust_neu": 30 * int(GESAMTVERLUST_DACH_NEU["Außentueren_neu"]) * 2400 / 1000,
        "Kellerdecke_transmissions_waermeverlust_alt": 30 * int(GESAMTVERLUST_DACH_ALT["Kellerdecke_alt"]) * 4000 / 1000,
        "Kellerdecke_transmissions_waermeverlust_neu": 30 * int(GESAMTVERLUST_DACH_NEU["Kellerdecke_neu"]) * 2400 / 1000,

        "Kelleraußenwand_transmissions_waermeverlust_alt": 0,
        "Kelleraußenwand_transmissions_waermeverlust_neu": 0,
        "Kellerinnenwand_transmissions_waermeverlust_alt": 0,
        "Kellerinnenwand_transmissions_waermeverlust_neu": 0,
        "Kellerboden_transmissions_waermeverlust_alt": 0,
        "Kellerboden_transmissions_waermeverlust_neu": 0,



        #"Dach_transmissionswaermeverlust": TRANSMISSIONSWAERMEVERLUSTE["Dach_waermeverlust"] * 30 * 4000 / 1000,
        #"Gaubendach_waermeverlust": 0.8 * GESAMTVERLUST_DACH["Gaubendach_alt"],
        #"Gaubendach_transmissionswaermeverlust": TRANSMISSIONSWAERMEVERLUSTE["Gaubendach_waermeverlust"] * 30 * 4000 / 1000,
    }


if submitted:
    Dämmschichtdicke = {
        "Dach_dämmung": 0.035 * 7.14,
        "Gaubendach_dämmung": 0.035 * 7.14,
        "Oberste_Geschossdecke_dämmung": 0.035 * 7.14,
        "Außenwand_dämmung": 0.035 * 5.0,
        "Giebelwand_dämmung": 0.035 * 5.0,
        "Gaubenwand_dämmung": 0.035 * 5.0,
        "Dachfenster_dämmung": 1.0,
        "Fenster_dämmung": 0.95,
        "Außentueren_dämmung": 1.3,
        "Kellerdecke_dämmung": 0.035 * 0.25,
        "Kelleraußenwand_dämmung": 0.035 * 0.25,
        "Kellerinnenwand_dämmung": 0.035 * 0.25,
        "Kellerfenster_dämmung": 0.95,
        "Kellerboden_dämmung": 0.035 * 0.25,
    }



if submitted:
    WB_ZUSCHLAG = {
        "Waermebrückenzuschlag 1_alt": 0.1 * GESAMTWAERMEVERLUST["Gesamtwaermeverlust_alt"],
        "Waermebrückenzuschlag 1_neu": 0.1 * GESAMTWAERMEVERLUST["Gesamtwaermeverlust_neu"],
        "Waermebrückenzuschlag 2_alt": 0.05 * GESAMTWAERMEVERLUST["Gesamtwaermeverlust_alt"],
        "Waermebrückenzuschlag 2_neu": 0.05 * GESAMTWAERMEVERLUST["Gesamtwaermeverlust_neu"],
        "Waermebrückenzuschlag 3_alt": 0.03 * GESAMTWAERMEVERLUST["Gesamtwaermeverlust_alt"],
        "Waermebrückenzuschlag 3_neu": 0.03 * GESAMTWAERMEVERLUST["Gesamtwaermeverlust_neu"],
    }

if submitted:
    GESAMTTRANSMISSIONSWAERMEVERLUST = {
        "Gesamttransmissionswäremverlust 1_alt": WB_ZUSCHLAG["Waermebrückenzuschlag 1_alt"] + GESAMTWAERMEVERLUST["Gesamtwaermeverlust_alt"],
        "Gesamttransmissionswäremverlust 1_neu": WB_ZUSCHLAG["Waermebrückenzuschlag 1_neu"] + GESAMTWAERMEVERLUST["Gesamtwaermeverlust_neu"],
        "Gesamttransmissionswäremverlust 2_alt": WB_ZUSCHLAG["Waermebrückenzuschlag 2_alt"] + GESAMTWAERMEVERLUST["Gesamtwaermeverlust_alt"],
        "Gesamttransmissionswäremverlust 2_neu": WB_ZUSCHLAG["Waermebrückenzuschlag 2_neu"] + GESAMTWAERMEVERLUST["Gesamtwaermeverlust_neu"],
        "Gesamttransmissionswäremverlust 3_alt": WB_ZUSCHLAG["Waermebrückenzuschlag 3_alt"] + GESAMTWAERMEVERLUST["Gesamtwaermeverlust_alt"],
        "Gesamttransmissionswäremverlust 3_neu": WB_ZUSCHLAG["Waermebrückenzuschlag 3_neu"] + GESAMTWAERMEVERLUST["Gesamtwaermeverlust_neu"],
    }

if submitted:
    SPEZIFISCHER_TRANSMISSIONSWAERMEVERLUST = {
        "Spezifischer Transmissionswärmeverlust 1_alt": GESAMTTRANSMISSIONSWAERMEVERLUST["Gesamttransmissionswäremverlust 1_alt"] / GEBAEUDEGESAMTFLAECHE["Beheizte Fläche"],
        "Spezifischer Transmissionswärmeverlust 1_neu": GESAMTTRANSMISSIONSWAERMEVERLUST["Gesamttransmissionswäremverlust 1_neu"] / GEBAEUDEGESAMTFLAECHE["Beheizte Fläche"],
        "Spezifischer Transmissionswärmeverlust 2_alt": GESAMTTRANSMISSIONSWAERMEVERLUST["Gesamttransmissionswäremverlust 2_alt"] / GEBAEUDEGESAMTFLAECHE["Beheizte Fläche"],
        "Spezifischer Transmissionswärmeverlust 2_neu": GESAMTTRANSMISSIONSWAERMEVERLUST["Gesamttransmissionswäremverlust 2_neu"] / GEBAEUDEGESAMTFLAECHE["Beheizte Fläche"],
        "Spezifischer Transmissionswärmeverlust 3_alt": GESAMTTRANSMISSIONSWAERMEVERLUST["Gesamttransmissionswäremverlust 3_alt"] / GEBAEUDEGESAMTFLAECHE["Beheizte Fläche"],
        "Spezifischer Transmissionswärmeverlust 3_neu": GESAMTTRANSMISSIONSWAERMEVERLUST["Gesamttransmissionswäremverlust 3_neu"] / GEBAEUDEGESAMTFLAECHE["Beheizte Fläche"],
    }

if submitted:
    HUELLFLAECHENVERLUST = {

    }


if submitted:
    ENERGIEVERBRAUCH_HEIZUNG = {

    }


if submitted:
    JAHRESPRIMAERENERGIEBEDARF_VERBRAUCH = {
        "Qh": Gas,
        "Qw": Gas * 0.18,
    }



if submitted:
    EFFIZIENZKLASSE = {
        "Effiziensklasse_alt": GEBAEUDEGESAMTFLAECHE["Hüllfläche schrägdach"] * 30 * 3170 / 1000 / (GEBAEUDEGESAMTFLAECHE["Beheizte Fläche"] + 31),
        "Effiziensklasse_neu": (GESAMTTRANSMISSIONSWAERMEVERLUST["Gesamttransmissionswäremverlust 3_neu"] * 2400 * 30) / (GEBAEUDEGESAMTFLAECHE["Nutzfläche"] * 1000),
    }

if submitted:
    ENERGIEBEDARF_DES_GEBAEUDES = {}

if submitted:
    GESAMTHEIZLAST_IN_KW = {}


# =====================================================
# NAVIGATION – EINGABEN
# =====================================================
if navigation == "📋 Eingaben":

    st.subheader("📋 Zusammenfassung")

    df_inputs = pd.DataFrame({
        "Parameter": [
            "Vorname", "Nachname", "Adresse", "Baujahr",
            "Wohnfläche", "Heizung"
        ],
        "Wert": [
            Vorname, Nachname, Adresse, baujahr,
            wohnflaeche, heizung_typ
        ]
    })

    st.dataframe(df_inputs, use_container_width=True)

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


    st.subheader("Wärmeverluste dach Alt")
    st.dataframe(GESAMTVERLUST_DACH_ALT , use_container_width=True)

    st.subheader("Wärmeverluste dach Neu")
    st.dataframe(GESAMTVERLUST_DACH_NEU , use_container_width=True)

    st.subheader("Gesamtwärmeverlust")
    st.dataframe(GESAMTWAERMEVERLUST , use_container_width=True)

    st.subheader("Transmissionswärmeverluste")
    st.dataframe(TRANSMISSIONSWAERMEVERLUSTE , use_container_width=True)


    st.subheader("Dämmschichtdicke")
    st.dataframe(Dämmschichtdicke , use_container_width=True)

    
    st.subheader("Wärmebrückenzuschlag")
    st.dataframe(WB_ZUSCHLAG , use_container_width=True)


    st.subheader("Gesamttransmissionswärmeverlust")
    st.dataframe(GESAMTTRANSMISSIONSWAERMEVERLUST , use_container_width=True)


    st.subheader("Spezifischer Transmissionswärmeverlust")
    st.dataframe(SPEZIFISCHER_TRANSMISSIONSWAERMEVERLUST , use_container_width=True)


    st.subheader("Hüllflächenverlust")
    st.dataframe(HUELLFLAECHENVERLUST , use_container_width=True)


    st.subheader("Effizienzklasse")
    st.dataframe(EFFIZIENZKLASSE , use_container_width=True)


    st.subheader("Energiebedarf des Gebäudes")
    st.dataframe(ENERGIEBEDARF_DES_GEBAEUDES , use_container_width=True)


    st.subheader("Gesamtheizlast in kW")
    st.dataframe(GESAMTHEIZLAST_IN_KW , use_container_width=True)


    st.subheader("Energiebedarf Heizung")
    #st.dataframe(ENERGIEBEDARF_HEIZUNG , use_container_width=True)


    st.subheader("Energieverbrauch Heizung")
    #st.dataframe(ENERGIEVERBRAUCH_HEIZUNG , use_container_width=True)


    st.subheader("Jahresprimärenergiebedarf Verbrauch")
    #st.dataframe(JAHRESPRIMAERENERGIEBEDARF_VERBRAUCH , use_container_width=True)


    st.subheader("Jahresprimärenergiebedarf Bedarf")
    #st.dataframe(JAHRESPRIMAERENERGIEBEDARF_BEDARF , use_container_width=True)





# =====================================================
# NAVIGATION – ERGEBNISSE
# =====================================================
if navigation == "📊 Ergebnisse":

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Effizienz ALT", f"{EFF_ALT} kWh/m²a")
    c2.metric("Effizienz NEU", f"{EFF_NEU} kWh/m²a")
    c3.metric("Heizlast ALT", f"{HEIZLAST_ALT} kW")
    c4.metric("Heizlast NEU", f"{HEIZLAST_NEU} kW")

    st.markdown("---")

    df_plot = pd.DataFrame({
        "Zustand": ["Alt", "Neu"],
        "Energiebedarf": [EFF_ALT, EFF_NEU]
    })

    fig = px.bar(
        df_plot,
        x="Zustand",
        y="Energiebedarf",
        title="Energiebedarf Vergleich",
        color="Zustand"
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# NAVIGATION – PDF
# =====================================================
if navigation == "📄 PDF":

    st.subheader("📄 PDF Bericht")

    st.success("PDF-Modul vorbereitet")

    st.markdown("""
    **Inhalt:**
    - Kundendaten  
    - Energiekennzahlen  
    - Diagramme  
    - Empfehlungen  
    """)

    st.download_button(
        "📥 PDF herunterladen",
        data=b"PDF_PLACEHOLDER",
        file_name="Energiebericht.pdf"
    )
