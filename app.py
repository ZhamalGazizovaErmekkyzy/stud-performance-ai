import streamlit as st
import pandas as pd
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# 🔹 Azure AI параметрлері
AZURE_AI_KEY = "5k96MSu2fN6fBVk8tWz9ijkteXyhaD7GrOWr3AZVM94ce5ZkPLVOJQQJ99BCACYeBjFXJ3w3AAAAACOGy7RA"
AZURE_AI_ENDPOINT = "https://teacherai.openai.azure.com/"

def authenticate_client():
    return TextAnalyticsClient(endpoint=AZURE_AI_ENDPOINT, credential=AzureKeyCredential(AZURE_AI_KEY))

client = authenticate_client()

# 🔹 Оқушылардың үлгерімін талдау функциясы
def analyze_performance(data):
    data['Орташа балл'] = data.iloc[:, 1:].mean(axis=1)

    recommendations = []
    for score in data['Орташа балл']:
        if score >= 9:
            rec = "Жарайсың! Осындай жоғары деңгейде жалғастыр!"
        elif score >= 7:
            rec = "Жақсы нәтиже! Бірақ қосымша тәжірибелік тапсырмалар орындау ұсынылады."
        elif score >= 5:
            rec = "Қосымша оқу және тәжірибелік жұмыстар қажет."
        else:
            rec = "Ойын арқылы оқыту әдістерін пайдалану ұсынылады."
        recommendations.append(rec)

    data['Ұсыныстар'] = recommendations
    return data

# 🔹 Streamlit интерфейсі
st.title("📚 Мұғалімдерге арналған виртуалды көмекші")
st.write("Оқушылардың бағалары жазылған CSV файлын жүктеңіз")

uploaded_file = st.file_uploader("CSV файлды таңдаңыз", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    result = analyze_performance(df)
    st.write("🔍 Оқушылардың үлгерімін талдау нәтижелері:")
    st.dataframe(result)

    st.download_button("Ұсыныстарды жүктеу", result.to_csv(index=False).encode('utf-8'), "recommendations.csv", "text/csv")
