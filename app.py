
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
import io
from datetime import datetime

st.set_page_config(page_title="CarService Manager", layout="centered")
st.title("🚗 CarService Manager - Registro Ore e Km")

if "data" not in st.session_state:
    st.session_state.data = []

with st.form("inserimento_dati"):
    st.subheader("📋 Inserisci dati giornalieri")
    nome = st.text_input("Nome operaio")
    targa = st.text_input("Targa macchina")
    data = st.date_input("Data", value=datetime.today())
    ora_inizio = st.time_input("Ora inizio")
    ora_fine = st.time_input("Ora fine")
    pausa_inizio = st.time_input("Inizio pausa")
    pausa_fine = st.time_input("Fine pausa")
    km_inizio = st.number_input("Km iniziali", min_value=0)
    km_fine = st.number_input("Km finali", min_value=0)
    guadagno = st.number_input("Guadagno €", min_value=0.0, step=0.5)
    contratto = st.selectbox("Tipo di contratto (ore/mese)", [40, 100, 160])
    note = st.text_area("Note (opzionale)", max_chars=200)

    aggiungi = st.form_submit_button("Aggiungi giornata")

    if aggiungi and nome and km_fine >= km_inizio:
        ore_lavorate = (datetime.combine(datetime.today(), ora_fine) - datetime.combine(datetime.today(), ora_inizio)).seconds / 3600
        pausa = (datetime.combine(datetime.today(), pausa_fine) - datetime.combine(datetime.today(), pausa_inizio)).seconds / 3600
        ore_totali = round(ore_lavorate - pausa, 2)
        km_totali = km_fine - km_inizio
        settimana = data.isocalendar()[1]
        mese = data.strftime('%B')
        st.session_state.data.append({
            "Data": data.strftime('%Y-%m-%d'),
            "Settimana": settimana,
            "Mese": mese,
            "Nome": nome,
            "Targa": targa,
            "Ore lavorate": ore_totali,
            "Pausa": pausa,
            "Km percorsi": km_totali,
            "Guadagno": guadagno,
            "Contratto": contratto,
            "Note": note
        })
        st.success(f"Giornata aggiunta per {nome} ✅")

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    st.subheader("📊 Riepilogo mensile")
    st.dataframe(df)

    st.subheader("📈 Grafico ore fatte vs target")
    df_group = df.groupby("Nome").agg({"Ore lavorate": "sum", "Contratto": "max"}).reset_index()
    df_group["Target mensile"] = df_group["Contratto"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df_group["Nome"], df_group["Target mensile"], alpha=0.5, label="Target")
    ax.bar(df_group["Nome"], df_group["Ore lavorate"], label="Ore fatte")
    ax.set_ylabel("Ore")
    ax.legend()
    st.pyplot(fig)

    st.subheader("📄 Esporta PDF")
    def genera_pdf(dataframe):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Riepilogo CarService", ln=True, align='C')
        pdf.ln(10)
        for _, row in dataframe.iterrows():
            pdf.multi_cell(0, 10, f"{row['Data']} - {row['Nome']} - Targa: {row['Targa']} - Ore: {row['Ore lavorate']} - Km: {row['Km percorsi']} - €: {row['Guadagno']}")
        buffer = io.BytesIO()
        pdf.output(buffer)
        return buffer.getvalue()

    pdf_bytes = genera_pdf(df)
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="riepilogo_carservice.pdf">📥 Scarica PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    st.info("Inserisci almeno una giornata per vedere il riepilogo.")
