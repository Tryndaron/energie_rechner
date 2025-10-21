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
""" if os.path.exists(FILE):
    try:
        with open(FILE, "r") as f:
            saved_values = json.load(f)
            st.session_state.update(saved_values)
    except Exception as e:
        st.warning(f"⚠️ Fehler beim Laden: {e}") """



if os.path.exists(FILE):
    try:
        with open(FILE, "r") as f:
            saved_values = json.load(f)
            for key, val in saved_values.items():
                if key not in st.session_state:  # nur setzen, wenn noch nicht vorhanden
                    st.session_state[key] = val
    except Exception as e:
        st.warning(f"⚠️ Fehler beim Laden: {e}")






st.title("🏗️ Gebäudeberechnung")

# --- Eingaben ---

with st.expander("Kontaktdaten", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        Vorname = st.text_input("Vorname", key="Vorname")
        Nachname = st.text_input("Nachname", key="Nachname")
        Adresse = st.text_input("Adresse", key="adresse")
        Telefon = st.text_input("Telefon",  key="telefon")
        E_Mail = st.text_input("E-Mail", key="email")
    


with st.expander("🏠 Grunddaten", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        baujahr = st.number_input("Baujahr", min_value=1800, max_value=2100, step=1, key="baujahr")
        personen = st.number_input("Personenzahl", min_value=1, step=1, key="personen")
        wohneinheiten = st.number_input("Wohneinheiten", min_value=1, step=1, key="wohneinheiten")
    with col2:
        nutzflaeche = st.number_input("Nutzfläche (m²)", min_value=1.0, key="nutzflaeche")

with st.expander("🧱 Gebäudezustand"):
    col1, col2 = st.columns(2)
    with col1:
        grundrisslaenge = st.number_input("Grundrisslänge (m)", min_value=1.0, key="grundrisslaenge")
        grundrissbreite = st.number_input("Grundrissbreite (m)", min_value=1.0, key="grundrissbreite")
        hoehe = st.number_input("Höhe (m)", min_value=0.0, key="hoehe")
        hoehe_dg = st.number_input("Höhe Dachgeschoss (m)", min_value=1.0, key="hoehe_dg")
        dachart = st.selectbox("Art", ["EFH", "MFH", "Reihenhaus", "Mehrgeschossig"], key="art")
        beheizt = st.selectbox("Beheizt", ["Ja", "Nein"], key="beheizt")
        sanierung = st.number_input("Letzte Sanierung (Jahr)", min_value=1900, max_value=2100, step=1, key="sanierung")
    with col2:
        st.markdown("**Außenwand**")
        art_1 = st.text_input("Art_1", key="art_1")
        außenwandhoehe = st.number_input("Höhe Außenwand (m)", min_value=0.0, key="aussenwandhoehe")
        sanierung_aw = st.number_input("Letzte Sanierung (Außenwand)", min_value=1900, max_value=2100, step=1, key="sanierung_aw")
        art_keller = st.text_input("Art (Kellerdecke)", key="art_keller")
        hoehe_keller = st.number_input("Höhe Keller (m)", min_value=0.0, key="hoehe_keller")
        sanierung_kd = st.number_input("Letzte Sanierung (Kellerdecke)", min_value=1900, max_value=2100, step=1, key="sanierung_kd")

        st.markdown("**Fenster**")
        art_3 = st.text_input("Art_3", key="art_3")
        fensterflaeche = st.number_input("Fensterfläche gesamt (m²)", min_value=1.0, key="fensterflaeche")
        sanierung_fenster = st.number_input("Letzte Sanierung (Fenster)", min_value=1900, max_value=2100, step=1, key="sanierung_fenster")

with st.expander("🔥 Beheizung"):
    col1, col2 = st.columns(2)
    with col1:
        heizung = st.selectbox("Heizung", ["Gas", "Öl", "Wärmepumpe", "Pellet", "Fernwärme", "Elektro", "Sonstige"], key="heizung")
        heiz_baujahr = st.number_input("Baujahr Heizung", min_value=1900, max_value=2100, step=1, key="heiz_baujahr")
        leistung = st.number_input("Leistung (kW)", min_value=1.0, key="leistung")
        heiz_last_neu = st.number_input("Heiz-Leistung (kW)", min_value=0.0, key="heiz_last_neu")
    with col2:
        waermeabgabe = st.text_input("Wärmeabgabe (z. B. Heizkörper, FBH)", key="waermeabgabe")
        vorlauf_heizung = st.number_input("Vorlauftemperatur Heizung (°C)", min_value=1.0, key="vorlauf_heizung")
        vorlauf_ww = st.number_input("Vorlauftemperatur Warmwasser (°C)", min_value=1.0, key="vorlauf_ww")
        oelverbrauch = st.number_input("Öl (Liter/Jahr)", min_value=1.0, key="oelverbrauch")
        oelpreis = st.number_input("Ölpreis (€/Liter)", min_value=1.0, key="oelpreis")
        gasverbrauch = st.number_input("Gas (kWh/Jahr)", min_value=1.0, key="gasverbrauch")
        gaspreis = st.number_input("Gaspreis (€/kWh)", min_value=0.0, key="gaspreis")
        pelletverbrauch = st.number_input("Pellets (kg/Jahr)", min_value=1.0, key="pelletverbrauch")
        pelletpreis = st.number_input("Pelletpreis (€/kg)", min_value=1.0, key="pelletpreis")

with st.expander("⚡ Strom"):
    col1, col2 = st.columns(2)
    with col1:
        stromverbrauch = st.number_input("Stromverbrauch (kWh/Jahr)", min_value=1.0, key="stromverbrauch")
        strompreis = st.number_input("Strompreis (€/kWh)", min_value=0.0, key="strompreis")
    with col2:
        wasser = st.number_input("Wasserstand (m)", min_value=1.0, key="wasser")

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

if heizung == "Gas":
    kg_co2_alt = gasverbrauch * 0.25
elif heizung == "Öl":
    kg_co2_alt = gasverbrauch * 0.6
else:
    kg_co2_alt = 0

# Beispiel: Backend-Berechnung
if submitted:
    st.subheader("📊 Ergebnis der Berechnung")

    daten = {
        "Zusätzliche KW für Warmwasser": 0.25 * personen,
        "Stromwert (/m²)": stromverbrauch / nutzflaeche,
        "Gaswert (/m²)": gasverbrauch / nutzflaeche,
        "Grundfläche (m²)": grundrisslaenge * grundrissbreite,
        "Steildach (m²)": math.sqrt((grundrissbreite / 2)**2 + hoehe_dg**2)*2*10,
        "Flächen_AW": (2*grundrisslaenge + 2*grundrissbreite) * außenwandhoehe,
        "Flächen_Giebel": (grundrissbreite*hoehe) / 2,
        "AW Fläche_Gesamt": ((grundrissbreite*hoehe)/2) + ((2*grundrisslaenge + 2*grundrissbreite) * außenwandhoehe),
        "AW Fläche_Gesamt-Fenster": ((2*grundrisslaenge + 2*grundrissbreite)*außenwandhoehe + (grundrissbreite*hoehe) / 2) - fensterflaeche,
        "Betriebsstd._alt": gasverbrauch / leistung,
        "CO2_Emissionen (Heizung IST)": kg_co2_alt,
        "Heizkosten(IST)": gasverbrauch * gaspreis,
        "Heizlast(SOLL)": (0.9 * gasverbrauch / 2400) + (0.25 * personen),
        "Bohrmeter(SOLL)": ((0.9 * gasverbrauch / 2400) + (0.25 * personen)) / entzugsleistung,
        "Bohrkosten(SOLL)": (((0.9 * gasverbrauch / 2400) + (0.25 * personen)) / entzugsleistung) * erdbohrung_kosten,
        "CO2_Emissionen(Strom IST)": stromverbrauch * energie_quelle_strom,
        "Stromkosten(IST)": strompreis * stromverbrauch,
        "CO2_Emissionen(Ökostrom IST)": stromverbrauch * energie_quelle_oekostrom,
        "Heizstrom(Luftwäremepumpe)": (0.9 * gasverbrauch) / luftwaerme,
        "CO2_Emissionen(Luftwäremepumpe)": ((0.9 * gasverbrauch) / luftwaerme) * energie_quelle_strom,
        "CO2_Emissionen(Ökostrom_Luftwäremepumpe)": ((0.9 * gasverbrauch) / luftwaerme) * energie_quelle_oekostrom,
        "Heizkosten(Luftwärmepumpe)": strompreis * ((0.9 * gasverbrauch) / luftwaerme),
        "Betriebskostenerparnis(ISTvsLuftwäremepumpe)": gasverbrauch * gaspreis - strompreis * ((0.9 * gasverbrauch) / luftwaerme),
        "Kühlstrom(Passivekühlung)": passive_cooling_stunden * passive_cooling_leistung,
        "CO2_Emissionen(Passivekühlstrom)": passive_cooling_stunden * passive_cooling_leistung * energie_quelle_strom,
        "kgCO2(Öko)Kühlung": passive_cooling_stunden * passive_cooling_leistung * energie_quelle_oekostrom,
        "Kühlkostenneu": strompreis * passive_cooling_stunden * passive_cooling_leistung,
        "Betriebskostenersparnis(Klimaanlage-Passivkühlung)": (strompreis * stromverbrauch) - (strompreis * passive_cooling_stunden * passive_cooling_leistung),
        "Differenz CO2-Emissionen (Klimaalnlage-Passivkühlung)": (klima_leistung * passive_cooling_stunden * energie_quelle_strom) - passive_cooling_stunden * passive_cooling_leistung * energie_quelle_strom,
        "Differenz CO2_Emissionen (Klimaanlage-Passivkühlung_mit_Ökostrom)": (klima_leistung * passive_cooling_stunden * energie_quelle_oekostrom) - (passive_cooling_stunden * passive_cooling_leistung * energie_quelle_oekostrom),
        "Kühlstrom(Klima-Split-Gerät)": klima_leistung * passive_cooling_stunden,
        "CO2_Emissionen(Klima-Split Gerät)": klima_leistung * passive_cooling_stunden * energie_quelle_strom,
        "CO2_Emissionen Ökostrom(Klima-Split-Gerät)": klima_leistung * passive_cooling_stunden * energie_quelle_oekostrom,
        "Kühlkosten(Klima-Split-Gerät)": strompreis * (klima_leistung * passive_cooling_stunden)
    }

    df = pd.DataFrame(daten.items(), columns=["Parameter", "Wert"])  
    st.dataframe(df, use_container_width=True)




    # --- Diagramme erstellen ---
    st.subheader("📈 Dashboard")

    # 1️⃣ Heizkosten Vergleich
    fig_heizkosten = px.bar(
        x=["Heizkosten (IST)", "Heizkosten (Luft-WP)"],
        y=[daten["Heizkosten(IST)"], daten["Heizkosten(Luftwärmepumpe)"]],
        labels={"x": "System", "y": "Kosten (€)"},
        title="💰 Heizkosten Vergleich",
        color=["Heizkosten (IST)", "Heizkosten (Luft-WP)"],
        color_discrete_map={
            "Heizkosten (IST)": "#cc0000",
            "Heizkosten (Luft-WP)": "#0066cc"
        }
    )
    st.plotly_chart(fig_heizkosten, use_container_width=True)

    # 2️⃣ CO2 Emissionen Vergleich
    fig_co2 = px.bar(
        x=["CO₂ (Heizung IST)", "CO₂ (Luft-WP)"],
        y=[daten["CO2_Emissionen (Heizung IST)"], daten["CO2_Emissionen(Luftwäremepumpe)"]],
        labels={"x": "System", "y": "Emissionen (kg CO₂)"},
        title="🌍 CO₂-Emissionen Heizung",
        color=["CO₂ (Heizung IST)", "CO₂ (Luft-WP)"],
        color_discrete_map={
            "CO₂ (Heizung IST)": "#666666",
            "CO₂ (Luft-WP)": "#00994d"
        }
    )
    st.plotly_chart(fig_co2, use_container_width=True)

    # 3️⃣ Energieverbrauch pro m²
    fig_verbrauch = px.bar(
        x=["Strom (/m²)", "Gas (/m²)"],
        y=[daten["Stromwert (/m²)"], daten["Gaswert (/m²)"]],
        labels={"x": "Energieträger", "y": "Verbrauch (/m²)"},
        title="⚡ Energieverbrauch pro m²",
        color=["Strom (/m²)", "Gas (/m²)"],
        color_discrete_map={
            "Strom (/m²)": "#00ccff",
            "Gas (/m²)": "#ffaa00"
        }
    )
    st.plotly_chart(fig_verbrauch, use_container_width=True)

    # 4️⃣ Kühlkosten Vergleich
    fig_kuehlung = px.bar(
        x=["Kühlkosten neu", "Kühlkosten Klima-Split"],
        y=[daten["Kühlkostenneu"], daten["Kühlkosten(Klima-Split-Gerät)"]],
        labels={"x": "System", "y": "Kosten (€)"},
        title="❄️ Kühlkosten Vergleich",
        color=["Kühlkosten neu", "Kühlkosten Klima-Split"],
        color_discrete_map={
            "Kühlkosten neu": "#ff66cc",
            "Kühlkosten Klima-Split": "#9933ff"
        }
    )
    st.plotly_chart(fig_kuehlung, use_container_width=True)

    # 5️⃣ CO₂ Emissionen Kühlung
    fig_co2_kuehlung = px.bar(
        x=["CO₂ (Passiv)", "CO₂ (Klima-Split)"],
        y=[daten["CO2_Emissionen(Passivekühlstrom)"], daten["CO2_Emissionen(Klima-Split Gerät)"]],
        labels={"x": "System", "y": "Emissionen (kg CO₂)"},
        title="🌡️ CO₂-Emissionen Kühlung",
        color=["CO₂ (Passiv)", "CO₂ (Klima-Split)"],
        color_discrete_map={
            "CO₂ (Passiv)": "#00cc44",
            "CO₂ (Klima-Split)": "#4444aa"
        }
    )
    st.plotly_chart(fig_co2_kuehlung, use_container_width=True)



     
