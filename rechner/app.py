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
from fixwerte import (SATTELDACH_DB_AUSGEBAUT, SATTELDACH_DB_NICHTAUSGEBAUT, 
                      OGD_DACH_AUSGEBAUT, OGD_DACH_NICHTAUSGEBAUT,
                      WAENDE_UND_DECKEN_ZU_ABSEITEN)
from u_werte import df_u_werte



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
   GESAMTVERLUST_DACH = {
        "Dach_alt":  int(SATTELDACH_DB_AUSGEBAUT) * df_u_werte.loc[2, f'{baujahr}'] * int(DACH["Satteldach"]),
        "Dach_neu":  int(SATTELDACH_DB_AUSGEBAUT) * 0.14 * int(DACH["Satteldach"]),# 0.14 bezeichnet den Uwert von 2025 der noch nachgetragen werden muss
        "Gaubendach_alt":  int(SATTELDACH_DB_AUSGEBAUT) * df_u_werte.loc[2, f'{baujahr}'] * int(DACH["Gaubendach"]),
        "Gaubendach_neu":  int(SATTELDACH_DB_AUSGEBAUT) * 0.14 * int(DACH["Gaubendach"]), # 0.14 bezeichnet den Uwert von 2025 der noch nachgetragen werden muss
        "Oberste Geschossdecke_alt": (int(OGD_DACH_AUSGEBAUT) * df_u_werte.loc[3, f'{baujahr}'] * int(DACH["Oberste Geschossdecke"])
                                      if beheizt == "Ja"
                                        else int(OGD_DACH_NICHTAUSGEBAUT) * df_u_werte.loc[3, f'{baujahr}'] * int(DACH["Oberste Geschossdecke"])), 
        "AUßenwand_alt": int(WAENDE_UND_DECKEN_ZU_ABSEITEN) * df_u_werte.loc[7, f'{baujahr}'] * int(AUẞENWAENDE["Außenwand Nord"]),
                                        
    }



if submitted:
    TRANSMISSIONSWAERMEVERLUSTE = {}


if submitted:
    Dämmschichtdicke = {}



if submitted:
    WB_ZUSCHLAG = {}

if submitted:
    GESAMTTRANSMISSIONSWAERMEVERLUST = {}

if submitted:
    SPEZIFISCHER_TRANSMISSIONSWAERMEVERLUST = {}

if submitted:
    HUELLFLAECHENVERLUST = {}

if submitted:
    EFFIZIENZKLASSE = {}

if submitted:
    ENERGIEBEDARF_DES_GEBAEUDES = {}

if submitted:
    GESAMTHEIZLAST_IN_KW = {}

###################################################################
#Heizung Berechnungen
###################################################################

if submitted:
    ENERGIEBEDARF_HEIZUNG = {}

if submitted:
    ENERGIEVERBRAUCH_HEIZUNG = {}

if submitted:
    JAHRESPRIMAERENERGIEBEDARF_VERBRAUCH = {}

if submitted:
    JAHRESPRIMAERENERGIEBEDARF_BEDARF = {}


####################################################################
#Invest Berechnungen 
####################################################################
















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
    st.subheader("Wärmeverluste dach alt")
    st.dataframe(GESAMTVERLUST_DACH , use_container_width=True)
    #st.subheader("Wärmeverluste ")
    #st.dataframe(WAERMEVERLUSTE_NEU, use_container_width=True)






#Ende der App bisher 






import streamlit as st
import pandas as pd
import plotly.express as px
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.pdfgen import canvas


# === Farbpalette & Schrift ===
PRIMARY_COLOR = colors.HexColor("#004C99")
SECONDARY_COLOR = colors.HexColor("#E6EEF7")
TEXT_COLOR = colors.HexColor("#333333")


# === Kopf- und Fußzeilenfunktion ===
def header_footer(canvas, doc):
    canvas.saveState()

    # Kopfzeile
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(PRIMARY_COLOR)
    canvas.drawString(2 * cm, 28 * cm, "Energieanalyse & Gebäudebewertung")
    try:
        canvas.drawImage("assets/logo.png", 16 * cm, 27.5 * cm, width=3*cm, height=1*cm, mask='auto')
    except:
        pass

    # Fußzeile
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.5 * cm, f"© {pd.Timestamp.now().year} EnergieRechner GmbH – Alle Rechte vorbehalten")
    canvas.drawRightString(19 * cm, 1.5 * cm, f"Seite {doc.page}")

    canvas.restoreState()


# === Beispiel-Daten ===
df_flaechen = pd.DataFrame({
    "Kategorie": ["Dach", "Außenwände", "Keller", "Fenster/Türen"],
    "Fläche (m²)": [120, 240, 100, 60]
})

df_verluste = pd.DataFrame({
    "Bauteil": ["Dach", "Wände", "Fenster/Türen", "Keller"],
    "Verlust (kWh/a)": [4500, 7200, 2300, 1800]
})

# === Diagramme ===
fig1 = px.bar(
    df_flaechen, x="Kategorie", y="Fläche (m²)",
    title="Flächenverteilung Gebäudehülle",
    color="Kategorie",
    color_discrete_sequence=["#004C99", "#0066CC", "#3385FF", "#66A3FF"]
)
fig1.write_image("flaechen.png")

fig2 = px.pie(
    df_verluste, values="Verlust (kWh/a)", names="Bauteil",
    title="Anteile am Wärmeverlust",
    color_discrete_sequence=["#004C99", "#0066CC", "#3385FF", "#66A3FF"]
)
fig2.write_image("verluste.png")



# === Streamlit-Anzeige ===
selected_categories = st.multiselect(
    "Wähle Bauteile für die Anzeige:",
    df_flaechen["Kategorie"].unique(),
    default=list(df_flaechen["Kategorie"].unique())
)

filtered_df = df_flaechen[df_flaechen["Kategorie"].isin(selected_categories)]
fig1_filtered = px.bar(
    filtered_df, x="Kategorie", y="Fläche (m²)",
    title="Gefilterte Flächenverteilung",
    color="Kategorie",
    color_discrete_sequence=["#004C99", "#0066CC", "#3385FF", "#66A3FF"]
)

st.plotly_chart(fig1_filtered, use_container_width=True)

















# === PDF-Erstellung ===
def generate_pdf(vorname, nachname, adresse, email):
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2 * cm, leftMargin=2 * cm,
                            topMargin=3 * cm, bottomMargin=2 * cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SectionTitle', fontSize=14, textColor=PRIMARY_COLOR, leading=16, spaceAfter=12))
    #styles.add(ParagraphStyle(name='BodyText', fontSize=10, textColor=TEXT_COLOR, leading=14))

    elements = []

    # Titel
    elements.append(Paragraph("Gebäudeberechnung – Analysebericht", styles['Title']))
    elements.append(Spacer(1, 0.5 * cm))

    # Kundendaten
    kontakt = f"<b>Erstellt für:</b><br/>{vorname} {nachname}<br/>{adresse}<br/>{email}"
    elements.append(Paragraph(kontakt, styles['BodyText']))
    elements.append(Spacer(1, 0.8 * cm))

    # Abschnitt 1 – Flächen
    elements.append(Paragraph("1. Flächenanalyse", styles['SectionTitle']))

    table_data = [df_flaechen.columns.to_list()] + df_flaechen.values.tolist()
    table = Table(table_data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), SECONDARY_COLOR),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Image("flaechen.png", width=14*cm, height=7*cm))
    elements.append(PageBreak())

    # Abschnitt 2 – Wärmeverluste
    elements.append(Paragraph("2. Wärmeverluste", styles['SectionTitle']))

    table_data2 = [df_verluste.columns.to_list()] + df_verluste.values.tolist()
    table2 = Table(table_data2, hAlign='LEFT')
    table2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), SECONDARY_COLOR),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))
    elements.append(table2)
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Image("verluste.png", width=14*cm, height=7*cm))

    pdf.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)
    return buffer


# === Streamlit UI ===
st.title("📘 Professioneller Energiebericht")

vorname = st.text_input("Vorname", "Max")
nachname = st.text_input("Nachname", "Mustermann")
adresse = st.text_input("Adresse", "Beispielstraße 1, 12345 Musterstadt")
email = st.text_input("E-Mail", "max@mustermann.de")

if st.button("📄 Bericht erzeugen"):
    buffer = generate_pdf(vorname, nachname, adresse, email)
    st.download_button("📥 PDF herunterladen", buffer, "Energiebericht.pdf", "application/pdf")













     
