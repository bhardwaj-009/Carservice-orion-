import streamlit as st
import pandas as pd
import datetime as dt
from streamlit_option_menu import option_menu

st.set_page_config(page_title="CarService ORION", layout="wide")

# Inizializzazione dati
if "dati" not in st.session_state:
    st.session_state.dati = []

# Tema moderno con navbar laterale
with st.sidebar:
    selected = option_menu("Navigazione", ["Login", "Dashboard", "Inserimento"],
        icons=["person-circle", "bar-chart", "pencil-square"],
        menu_icon="tools", default_index=0)

st.markdown("""
    <style>
        .main { background-color: #f9f9f9; }
        .block-container { padding: 2rem 2rem 2rem 2rem; }
    </style>
""", unsafe_allow_html=True)

# Login page
if selected == "Login":
    st.title("🔐 Accesso Operatori e Amministratori")
    username = st.text_input("Nome utente")
    password = st.text_input("Password", type="password")
    utenti = {"admin": "admin123", "operaio1": "pwd1", "operaio2": "pwd2"}

    if st.button("Login"):
        if utenti.get(username) == password:
            st.session_state["utente"] = username
            st.success(f"Benvenuto {username}!")
        else:
            st.error("Credenziali non valide")

# Inserimento giornata lavoro
elif selected == "Inserimento" and "utente" in st.session_state:
    st.title("📝 Inserimento Giornata di Lavoro")
    with st.form("inserimento"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.selectbox("Nome Operaio", ["Marco", "Saeed", "Qasim", "Najib", "Hikmat", "Musa", "Khalil", "Ashraf", "Sumit", "Khalid"])
            targa = st.text_input("Targa Macchina")
            data = st.date_input("Data", dt.date.today())
            ora_inizio = st.time_input("Ora Inizio")
            ora_fine = st.time_input("Ora Fine")
        with col2:
            pausa_inizio = st.time_input("Inizio Pausa")
            pausa_fine = st.time_input("Fine Pausa")
            km_inizio = st.number_input("Km Inizio", min_value=0)
            km_fine = st.number_input("Km Fine", min_value=0)
            guadagno = st.number_input("Guadagno (€)", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Salva Giornata")

        if submitted:
            delta_ore = (dt.datetime.combine(dt.date.today(), ora_fine) - dt.datetime.combine(dt.date.today(), ora_inizio))
            delta_pausa = (dt.datetime.combine(dt.date.today(), pausa_fine) - dt.datetime.combine(dt.date.today(), pausa_inizio))
            ore_lavorate = (delta_ore - delta_pausa).total_seconds() / 3600
            km_percorsi = km_fine - km_inizio

            st.session_state.dati.append({
                "Data": data,
                "Nome": nome,
                "Targa": targa,
                "Ore Lavorate": round(ore_lavorate, 2),
                "Km": km_percorsi,
                "Guadagno": guadagno
            })
            st.success("✅ Giornata salvata con successo!")

# Dashboard riepilogo
elif selected == "Dashboard" and "utente" in st.session_state:
    st.title("📊 Dashboard Operativa")

    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        contratti = {
            "Marco": 160, "Saeed": 160, "Qasim": 100, "Najib": 160, "Hikmat": 160,
            "Musa": 160, "Khalil": 160, "Ashraf": 40, "Sumit": 160, "Khalid": 40
        }

        totali = df.groupby("Nome").agg({
            "Ore Lavorate": "sum",
            "Km": "sum",
            "Guadagno": "sum"
        }).reset_index()
        totali["Target Ore"] = totali["Nome"].map(lambda x: contratti.get(x, 0))
        totali["Stato"] = totali.apply(lambda x: "✅ OK" if abs(x["Ore Lavorate"] - x["Target Ore"]) < 1 else ("🔺 Sopra" if x["Ore Lavorate"] > x["Target Ore"] else "🔻 Sotto"), axis=1)

        st.dataframe(totali.style.format({
            "Ore Lavorate": "{:.2f}", "Km": "{:.0f}", "Guadagno": "€{:.2f}"
        }))

        st.subheader("📈 Grafico Ore Lavorate vs Target")
        chart_data = totali[["Nome", "Ore Lavorate", "Target Ore"]].set_index("Nome")
        st.bar_chart(chart_data)

        csv_data = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Scarica Dati in Excel (CSV)",
    data=csv_data,
    file_name="report_carservice.csv",
    mime="text/csv"
)

from fpdf import FPDF
import io

def genera_pdf(df_totali):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Report CarService ORION", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Data generazione: {dt.date.today().strftime('%d/%m/%Y')}", ln=True)

    pdf.ln(5)
    for _, row in df_totali.iterrows():
        pdf.cell(0, 8, f"{row['Nome']}: {row['Ore Lavorate']} ore, {row['Km']} km, €{row['Guadagno']:.2f} - Stato: {row['Stato']}", ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

pdf_bytes = genera_pdf(totali)
st.download_button(
    label="⬇️ Scarica PDF Riepilogo",
    data=pdf_bytes,
    file_name="report_carservice.pdf",
    mime="application/pdf"
)

else:
    st.info("🔐 Accedi dal menu per iniziare.")
