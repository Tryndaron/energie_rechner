import streamlit as st
import pandas as pd
import math
import os
import json



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














FILE = "saved_values.json"



if "initialized" not in st.session_state:  # Nur beim ersten Start
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f:
                saved_values = json.load(f)
                st.session_state.update(saved_values)
        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden: {e}")
    st.session_state.initialized = True







st.title("🏗️ Gebäudeberechnung")




# --- Eingaben ---
with st.expander("🏠 Grunddaten", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        baujahr = st.number_input("Baujahr", min_value=1800, max_value=2100, step=1)
        personen = st.number_input("Personenzahl", min_value=1, step=1)
        wohneinheiten = st.number_input("Wohneinheiten", min_value=1, step=1)
    with col2:
        nutzflaeche = st.number_input("Nutzfläche (m²)", min_value=1.0)

with st.expander("🧱 Gebäudezustand"):
    col1, col2 = st.columns(2)
    with col1:
        grundrisslaenge = st.number_input("Grundrisslänge (m)", min_value=1.0)
        grundrissbreite = st.number_input("Grundrissbreite (m)", min_value=1.0)
        hoehe = st.number_input("Höhe (m)", min_value=0.0)
        hoehe_dg = st.number_input("Höhe Dachgeschoss (m)", min_value=0.0)
        art = st.selectbox("Art", ["EFH", "MFH", "Reihenhaus", "Mehrgeschossig"])
        beheizt = st.selectbox("Beheizt", ["Ja", "Nein"])
        sanierung = st.number_input("Letzte Sanierung (Jahr)", min_value=1900, max_value=2100, step=1)
    with col2:
        st.markdown("**Außenwand**")
        art_1 = st.text_input("Art_1")
        außenwandhoehe = st.number_input("Höhe Außenwand (m)", min_value=0.0)
        sanierung_aw = st.number_input("Letzte Sanierung (Außenwand)", min_value=1900, max_value=2100, step=1)
        art_keller = st.text_input("Art (Kellerdecke)")
        hoehe_keller = st.number_input("Höhe Keller (m)", min_value=0.0)
        sanierung_kd = st.number_input("Letzte Sanierung (Kellerdecke)", min_value=1900, max_value=2100, step=1)

        st.markdown("**Fenster**")
        art_3 = st.text_input("Art_3")
        fensterflaeche = st.number_input("Fensterfläche gesamt (m²)", min_value=0.0)
        sanierung_fenster = st.number_input("Letzte Sanierung (Fenster)", min_value=1900, max_value=2100, step=1)

with st.expander("🔥 Beheizung"):
    col1, col2 = st.columns(2)
    with col1:
        heizung = st.selectbox("Heizung", ["Gas", "Öl", "Wärmepumpe", "Pellet", "Fernwärme", "Elektro", "Sonstige"])
        heiz_baujahr = st.number_input("Baujahr Heizung", min_value=1900, max_value=2100, step=1)
        leistung = st.number_input("Leistung (kW)", min_value=0.0)
        heiz_last_neu = st.number_input("Heiz-Leistung (kW)", min_value=0.0)
    with col2:
        waermeabgabe = st.text_input("Wärmeabgabe (z. B. Heizkörper, FBH)")
        vorlauf_heizung = st.number_input("Vorlauftemperatur Heizung (°C)", min_value=0.0)
        vorlauf_ww = st.number_input("Vorlauftemperatur Warmwasser (°C)", min_value=0.0)
        oelverbrauch = st.number_input("Öl (Liter/Jahr)", min_value=0.0)
        oelpreis = st.number_input("Ölpreis (€/Liter)", min_value=0.0)
        gasverbrauch = st.number_input("Gas (kWh/Jahr)", min_value=0.0)
        gaspreis = st.number_input("Gaspreis (€/kWh)", min_value=0.0)
        pelletverbrauch = st.number_input("Pellets (kg/Jahr)", min_value=0.0)
        pelletpreis = st.number_input("Pelletpreis (€/kg)", min_value=0.0)

with st.expander("⚡ Strom"):
    col1, col2 = st.columns(2)
    with col1:
        stromverbrauch = st.number_input("Stromverbrauch (kWh/Jahr)", min_value=0.0)
        strompreis = st.number_input("Strompreis (€/kWh)", min_value=0.0)
    with col2:
        wasser = st.number_input("Wasserstand (m)", min_value=0.0)

# --- Button ---
submitted = st.button("💾 Berechne")









#Fixwerte 
entzugsleistung = 0.04
erdbohrung_kosten = 120
energie_quelle_strom = 0.4
energie_quelle_oekostrom = 0.03
luftwaerme = 2.5
klima_leistung = 2.5
passive_cooling_leistung = 0.4
passive_cooling_stunden = 900




if heizung == "Gas":
    kg_co2_alt = gasverbrauch * 0.3
elif heizung == "Öl":
    kg_co2_alt = gasverbrauch * 0.6


FIELDS = ["baujahr", "personen", "wohneinheiten", "nutzflaeche", 
          "grundrisslaenge", "grundrissbreite", "heizung", "stromverbrauch"]

if submitted:
    values_to_save = {k: st.session_state[k] for k in FIELDS if k in st.session_state}
    with open(FILE, "w") as f:
        json.dump(values_to_save, f)






# Beispiel: Backend-Berechnung (hier Platzhalter – du kannst hier alles definieren)
if submitted:

    st.subheader("📊 Ergebnis der Berechnung")


    # Beispiel-Dictionary aus Eingaben (hier kannst du beliebige Berechnungen einfügen!)
    daten = {
        "zusätzl. KW (WW)": 0.25 * personen,
        "Stromwert (/m²)": stromverbrauch / nutzflaeche,
        "Gaswert (/m²)": gasverbrauch / nutzflaeche,
        "Grundfläche (m²)": grundrisslaenge * grundrissbreite,
        "Steildach (m²)": math.sqrt((grundrissbreite / 2)**2 + hoehe_dg * hoehe_dg)*2*10 ,
        "Flächen_AW": (2*grundrisslaenge + 2*grundrissbreite) * außenwandhoehe,
        "Flächen_Giebel": (grundrissbreite*hoehe) / 2,
        "AW Fläche_Gesamt": (2*grundrisslaenge + 2*grundrissbreite)*außenwandhoehe + (grundrissbreite*hoehe_dg) / 2,
        "AW Fläche_Gesamt-Fenster": ((2*grundrisslaenge + 2*grundrissbreite)*außenwandhoehe + (grundrissbreite*hoehe) / 2) - fensterflaeche,
        "Betriebsstd._alt": gasverbrauch / leistung,
        "kg CO2_alt": kg_co2_alt,
        "Heizkosten_alt": gasverbrauch * gaspreis,
        "Heizlast_neu": (0.9 * gasverbrauch / 2400) + (0.25 * personen),
        "Bohrmeter_neu": heiz_last_neu / entzugsleistung,
        "Bohrkosten_neu": (heiz_last_neu / entzugsleistung) * erdbohrung_kosten,
        "Strom_kg CO2 (alt)": stromverbrauch * energie_quelle_strom,
        "Stromkosten_alt": strompreis * stromverbrauch,
        "Strom_kg CO2 (alt) Öko": stromverbrauch * energie_quelle_oekostrom,
        "Heizstrom neu": (0.9 * gasverbrauch) / luftwaerme,
        "kg CO2": ((0.9 * gasverbrauch) / luftwaerme) * energie_quelle_strom,
        "kg CO2 (Öko)": ((0.9 * gasverbrauch) / luftwaerme) * energie_quelle_oekostrom,
        "Heizkosten neu": strompreis * ((0.9 * gasverbrauch) / luftwaerme),
        "Betr.kosten alt vs neu": gasverbrauch * gaspreis - strompreis * ((0.9 * gasverbrauch) / luftwaerme),
        "Kühlstrom neu": passive_cooling_stunden * passive_cooling_leistung,
        "kg CO2 Kühlung": passive_cooling_stunden * passive_cooling_leistung * energie_quelle_strom,
        "kg CO2 (Öko) Kühlung": passive_cooling_stunden * passive_cooling_leistung * energie_quelle_oekostrom,
        "Kühlkosten neu": strompreis * passive_cooling_stunden * passive_cooling_leistung,
        "Betr.kosten vs Klima": (strompreis * stromverbrauch) - (strompreis * passive_cooling_stunden * passive_cooling_leistung),
        "kg CO2 vs Klima": (klima_leistung * passive_cooling_stunden * energie_quelle_strom) - passive_cooling_stunden * passive_cooling_leistung * energie_quelle_strom,
        "kg CO2 vs Klima (Öko)": (klima_leistung * passive_cooling_stunden * energie_quelle_strom) - (passive_cooling_stunden * passive_cooling_leistung * energie_quelle_oekostrom),
        "Stromverbrauch Klima": klima_leistung * passive_cooling_stunden,
        "kg CO2 Strom Klima": klima_leistung * passive_cooling_stunden * energie_quelle_strom,
        "kg CO2 (Öko) Strom Klima": klima_leistung * passive_cooling_stunden * energie_quelle_oekostrom,
        "Stromkosten": strompreis * stromverbrauch
    }


    df = pd.DataFrame(daten.items(), columns=["Parameter", "Wert"])
    st.dataframe(df, use_container_width=True)
