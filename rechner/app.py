import streamlit as st
import pandas as pd
import math

st.title("🏗️ Gebäudeberechnung")

# Eingabeformulare
with st.form("input_form"):
    st.subheader("🔢 Gebäudeparameter")

    Grunddaten, Gebäudezustand, Beheizung, Strom = st.columns(4)
    with Grunddaten:
        st.markdown("### 🏠 Grunddaten")
        baujahr = st.number_input("Baujahr", min_value=1800, max_value=2100, step=1)
        personen = st.number_input("Personenzahl", min_value=1, step=1)
        wohneinheiten = st.number_input("Wohneinheiten", min_value=1, step=1)
        nutzflaeche = st.number_input("Nutzfläche (m²)", min_value=1.0)
        

    with Gebäudezustand:
        st.markdown("### 🧱 Gebäudezustand")
        grundrisslaenge = st.number_input("Grundrisslänge (m)", min_value=1.0)
        grundrissbreite = st.number_input("Grundrissbreite (m)", min_value=1.0)

        st.markdown("### Dach + DG")
        art = st.selectbox("Art (z. B. EFH, MFH, etc.)", ["EFH", "MFH", "Reihenhaus", "Mehrgeschossig"])
        hoehe = st.number_input("Höhe (m)", min_value=0.0)
        sanierung = st.number_input("Letzte Sanierung (Jahr)", min_value=1900, max_value=2100, step=1)
        beheizt = st.selectbox("Beheizt", ["Ja", "Nein"])
        hoehe_dg = st.number_input("Höhe Dachgeschoss (m)", min_value=0.0)

        st.markdown("Außenwand")
        art_1 = st.text_input("Art_1")
        dachhoehe = st.number_input("Höhe_2 (m)", min_value=0.0)
        sanierung_aw = st.number_input("Letzte Sanierung (Außenwand)", min_value=1900, max_value=2100, step=1)
        art_keller = st.text_input("Art (Kellerdecke)")
        hoehe_keller = st.number_input("Höhe Keller (m)", min_value=0.0)
        sanierung_kd = st.number_input("Letzte Sanierung (Kellerdecke)", min_value=1900, max_value=2100, step=1)

        st.markdown("### Fenster")
        art_3 = st.text_input("Art_3")
        fensterflaeche = st.number_input("Fensterfläche gesamt (m²)", min_value=0.0)
        sanierung_fenster = st.number_input("Letzte Sanierung (Fenster)", min_value=1900, max_value=2100, step=1)
        

    with Beheizung:
        st.markdown("### 🔥 Beheizung")
        heizung = st.selectbox("Heizung", ["Gas", "Öl", "Wärmepumpe", "Pellet", "Fernwärme", "Elektro", "Sonstige"])
        heiz_baujahr = st.number_input("Baujahr Heizung", min_value=1900, max_value=2100, step=1)
        leistung = st.number_input("Leistung (kW)", min_value=0.0)
        waermeabgabe = st.text_input("Wärmeabgabe (z. B. Heizkörper, FBH)")
        vorlauf_heizung = st.number_input("Vorlauftemperatur Heizung (°C)", min_value=0.0)
        vorlauf_ww = st.number_input("Vorlauftemperatur Warmwasser (°C)", min_value=0.0)
        oelverbrauch = st.number_input("Öl (Liter/Jahr)", min_value=0.0)
        oelpreis = st.number_input("Ölpreis (€/Liter)", min_value=0.0)
        gasverbrauch = st.number_input("Gas (kWh/Jahr)", min_value=0.0)
        gaspreis = st.number_input("Gaspreis (€/kWh)", min_value=0.0)
        pelletverbrauch = st.number_input("Pellets (kg/Jahr)", min_value=0.0)
        pelletpreis = st.number_input("Pelletpreis (€/kg)", min_value=0.0)

    with Strom:
        st.markdown("### ⚡ Strom")
        stromverbrauch = st.number_input("Strom(m)", min_value=0.0)
        strompreis = st.number_input("Strompreis (Jahr)", min_value=0.0)
        wasser = st.number_input("Wasserstand (m)", min_value=0.0)

    submitted = st.form_submit_button("Berechne")

# Beispiel: Backend-Berechnung (hier Platzhalter – du kannst hier alles definieren)
if submitted:
    st.subheader("📊 Ergebnis der Berechnung")

    # Beispiel-Dictionary aus Eingaben (hier kannst du beliebige Berechnungen einfügen!)
    daten = {
        "zusätzl. KW (WW)": 0.25 * personen,
        "Stromwert (/m²)": stromverbrauch / nutzflaeche,
        "Gaswert (/m²)": gaspreis / nutzflaeche,
        "Grundfläche (m²)": grundrisslaenge * grundrissbreite,
        "Steildach (m²)": math.sqrt((grundrissbreite / 2)**2 + hoehe_dg * hoehe_dg)*2*10 ,
        "Flächen_AW": (2*grundrisslaenge + 2*grundrissbreite)*hoehe,
        "Flächen_Giebel": (grundrissbreite*hoehe_dg) / 2,
        "AW Fläche_Gesamt": (2*grundrisslaenge + 2*grundrissbreite)*hoehe + (grundrissbreite*hoehe_dg) / 2,
        "AW Fläche_Gesamt-Fenster": ((2*grundrisslaenge + 2*grundrissbreite)*hoehe + (grundrissbreite*hoehe_dg) / 2) - fensterflaeche,
        "Betriebsstd._alt": gasverbrauch / leistung,
        "Bohrmeter_alt": None,
        "Bohrkosten_alt": None,
        "kg CO2_alt": None,
        "Heizkosten_alt": gasverbrauch * gaspreis,
        "Heizlast_neu": None,
        "Bohrmeter_neu": None,
        "Bohrkosten_neu": None,
        "Strom_kg CO2 (alt)": None,
        "Stromkosten_alt": strompreis * stromverbrauch,
        "Strom_kg CO2 (alt) Öko": None,
        "Stromkosten_alt Öko": None,
        "Heizstrom neu": None,
        "kg CO2": None,
        "kg CO2 (Öko)": None,
        "Heizkosten neu": strompreis * heizstromneu,
        "Betr.kosten alt vs neu": gasverbrauch * gaspreis - strompreis * heizstromneu,
        "kg CO2 alt vs neu": kg_co2_alt - kg_co2 ,
        "kg CO2 alt vs neu (Öko)": kg_co2_alt - kog_co2_neu_oeko,
        "Kühlstrom neu": None,
        "kg CO2 Kühlung": None,
        "kg CO2 (Öko) Kühlung": None,
        "Kühlkosten neu": strompreis * kühlstrom_neu,
        "Betr.kosten vs Klima": stromkosten - (strompreis * kühlstrom_neu),
        "kg CO2 vs Klima": kg_co2_klima - kg_co2,
        "kg CO2 vs Klima (Öko)": kg_co2_oeko_klima - kg_co2_oeko,
        "Stromverbrauch": None,
        "kg CO2 Strom": None,
        "kg CO2 (Öko) Strom": None,
        "Stromkosten": strompreis * stromverbrauch
    }


    df = pd.DataFrame(daten.items(), columns=["Parameter", "Wert"])
    st.dataframe(df, use_container_width=True)
