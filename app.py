import streamlit as st
import pandas as pd
import io
import chardet
import matplotlib.pyplot as plt
import seaborn as sns
from openpyxl import Workbook

# 🎯 Басты тақырып
st.title("📚 Оқушылардың оқу жетістіктерін талдау")

# 📂 Файл жүктеу
uploaded_file = st.file_uploader("Файлды жүктеңіз", type=["csv", "xlsx", "xls", "json", "txt"])

# 📥 Файлды оқу функциясы
def load_file(uploaded_file):
    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1]

        if file_type == 'csv':
            raw_data = uploaded_file.read()
            detected_encoding = chardet.detect(raw_data)['encoding']
            df = pd.read_csv(io.BytesIO(raw_data), encoding=detected_encoding, low_memory=False)
        elif file_type in ['xls', 'xlsx']:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        elif file_type == 'json':
            df = pd.read_json(uploaded_file)
        elif file_type == 'txt':
            df = pd.read_csv(uploaded_file, delimiter="\t", encoding="utf-8", low_memory=False)
        else:
            st.error("❌ Қолдау көрсетілмейтін файл форматы!")
            return None
        return df
    return None

# 📊 Орташа баллды есептеу және ұсыныстар беру
def analyze_performance(data):
    numeric_data = data.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    data['Орташа балл'] = numeric_data.mean(axis=1, skipna=True)
    recommendations = []
    
    for score in data['Орташа балл']:
        if pd.isna(score):
            rec = "❓ Мәлімет жоқ"
        elif score >= 9:
            rec = "🌟 Керемет нәтиже! Жалғастыра беріңіз!"
        elif score >= 7:
            rec = "👍 Жақсы! Бірақ одан да жақсартуға болады."
        elif score >= 5:
            rec = "📚 Қосымша дайындалу қажет."
        else:
            rec = "🚀 Тьюторлық немесе қосымша сабақтарды қарастырыңыз."
        recommendations.append(rec)
    
    data['Ұсыныстар'] = recommendations
    return data

# 📥 Excel жүктеу
def download_excel(df):
    output = io.BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    for r_idx, row in enumerate(df.itertuples(index=False), start=1):
        for c_idx, value in enumerate(row, start=1):
            sheet.cell(row=r_idx, column=c_idx, value=value)
    workbook.save(output)
    return output.getvalue()

# 🏁 Егер файл жүктелсе, деректерді өңдеу
if uploaded_file:
    df = load_file(uploaded_file)
    if df is not None:
        result = analyze_performance(df)

        # 📊 Кесте түрінде көрсету
        st.write("📊 **Оқушылардың оқу жетістіктерін талдау:**")
        st.dataframe(result)

        # 📈 Дөңгелек диаграмма (Pie Chart)
        st.subheader("📊 Орташа балл бойынша үлес диаграммасы")
        fig, ax = plt.subplots()
        colors = sns.color_palette("pastel")  # Түрлі түсті палитра
        score_counts = result['Орташа балл'].round(1).value_counts().sort_index()
        
        ax.pie(score_counts, labels=score_counts.index, autopct='%1.1f%%', colors=colors, startangle=140)
        ax.set_title("Орташа балл үлесі")
        st.pyplot(fig)

        # 📥 Excel жүктеу батырмасы
        excel_data = download_excel(result)
        st.download_button(label="📥 Excel форматында жүктеу",
                           data=excel_data,
                           file_name="recommendations.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
