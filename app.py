import streamlit as st
import pandas as pd
import pyodbc
import io
import matplotlib.pyplot as plt
import seaborn as sns
from openpyxl import Workbook
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Azure AI параметрлері
AZURE_AI_KEY = "5k96MSu2fN6fBVk8tWz9ijkteXyhaD7GrOWr3AZVM94ce5ZkPLVOJQQJ99BCACYeBjFXJ3w3AAAAACOGy7RA"
AZURE_AI_ENDPOINT = "https://teacherai.openai.azure.com/"

def authenticate_client():
    return TextAnalyticsClient(endpoint=AZURE_AI_ENDPOINT, credential=AzureKeyCredential(AZURE_AI_KEY))

client = authenticate_client()

# Файлды жүктеу
st.title("📚 Оқушылардың оқу жетістіктерін талдау")
uploaded_file = st.file_uploader("Файлды жүктеңіз", type=["csv", "xlsx", "xls", "json", "txt"])

def load_file(uploaded_file):
    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1]
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        elif file_type in ['xls', 'xlsx']:
            df = pd.read_excel(uploaded_file)
        elif file_type == 'json':
            df = pd.read_json(uploaded_file)
        elif file_type == 'txt':
            df = pd.read_csv(uploaded_file, delimiter="\t")
        else:
            st.error("❌ Қолдау көрсетілмейтін файл форматы!")
            return None
        return df
    return None

def analyze_performance(data):
    data['Орташа балл'] = data.iloc[:, 1:].mean(axis=1)
    recommendations = []
    for score in data['Орташа балл']:
        if score >= 9:
            rec = "Керемет нәтиже! Жалғастыра беріңіз!"
        elif score >= 7:
            rec = "Жақсы! Бірақ одан да жақсартуға болады."
        elif score >= 5:
            rec = "Қосымша дайындалу қажет."
        else:
            rec = "Тьюторлық немесе қосымша сабақтарды қарастырыңыз."
        recommendations.append(rec)
    data['Ұсыныстар'] = recommendations
    return data

def save_to_db(df):
    try:
        server = 'СІЗДІҢ_AZURE_SERVER'
        database = 'students_db'
        username = 'СІЗДІҢ_ЛОГИН'
        password = 'СІЗДІҢ_ҚҰПИЯ СӨЗ'
        conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        for index, row in df.iterrows():
            cursor.execute("INSERT INTO students (name, average_score, recommendation) VALUES (?, ?, ?)",
                           row['Аты'], row['Орташа балл'], row['Ұсыныстар'])
        conn.commit()
        cursor.close()
        conn.close()
        st.success("✅ Деректер SQL Database-ке сақталды!")
    except Exception as e:
        st.error(f"❌ Қате: {e}")

def download_excel(df):
    output = io.BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    for r_idx, row in enumerate(df.itertuples(index=False), start=1):
        for c_idx, value in enumerate(row, start=1):
            sheet.cell(row=r_idx, column=c_idx, value=value)
    workbook.save(output)
    return output.getvalue()

if uploaded_file:
    df = load_file(uploaded_file)
    if df is not None:
        result = analyze_performance(df)
        st.write("📊 Оқушылардың оқу жетістіктерін талдау:")
        st.dataframe(result)
        
        # График қосу
        st.subheader("📈 Орташа балл диаграммасы")
        fig, ax = plt.subplots()
        sns.histplot(result['Орташа балл'], bins=10, kde=True, ax=ax)
        ax.set_xlabel("Орташа балл")
        ax.set_ylabel("Оқушылар саны")
        st.pyplot(fig)

        # SQL Database-ке сақтау
        if st.button("💾 Деректерді SQL Database-ке сақтау"):
            save_to_db(result)

        # Excel жүктеу
        excel_data = download_excel(result)
        st.download_button(label="📥 Excel форматында жүктеу",
                           data=excel_data,
                           file_name="recommendations.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
