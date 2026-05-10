import streamlit as st
import requests

def verify_source(title, claimed_authors):
    api_url = f"https://api.crossref.org/works?query.title={title}&rows=1"
    try:
        response = requests.get(api_url).json()
        if response['message']['items']:
            item = response['message']['items'][0]
            real_title = item.get('title', [''])[0]
            real_authors = [a.get('family', 'Unknown') for a in item.get('author', [])]
            
            # Перевірка наявності заявлених авторів у реальному списку
            match = any(claimed.strip().lower() in [r.lower() for r in real_authors] for claimed in claimed_authors)
            
            return {
                "Статус": "✅ ВЕРИФІКОВАНО" if match else "❌ ГАЛЮЦИНАЦІЯ",
                "Дані з бази (Назва)": real_title,
                "Справжні автори": ", ".join(real_authors)
            }
        else:
            return {"Статус": "❓ НЕ ЗНАЙДЕНО", "Дані з бази (Назва)": "—", "Справжні автори": "—"}
    except:
        return {"Статус": "🔌 ПОМИЛКА API", "Дані з бази (Назва)": "—", "Справжні автори": "—"}

# --- НАЛАШТУВАННЯ ІНТЕРФЕЙСУ STREAMLIT ---
st.set_page_config(page_title="Верифікація ДКР", page_icon="🎓", layout="wide")
st.title("🎓 Система верифікації бібліографії")
st.markdown("Перевірка джерел через **Crossref API** для виявлення галюцинацій ШІ (підміни авторів або вигаданих статей).")

# Збереження черги статей
if 'queue' not in st.session_state:
    st.session_state.queue = []

# Форма вводу
with st.form("input_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        title_input = st.text_input("📝 Назва статті:")
    with col2:
        authors_input = st.text_input("👥 Введені автори (через кому):")
    
    add_btn = st.form_submit_button("➕ Додати до списку")
    if add_btn and title_input:
        # Додаємо статтю до черги
        st.session_state.queue.append({
            "Запит (Назва)": title_input, 
            "Введені автори": [a.strip() for a in authors_input.split(",")]
        })

# Відображення черги та результатів
if st.session_state.queue:
    st.subheader("📋 Черга на перевірку")
    for i, item in enumerate(st.session_state.queue):
        st.text(f"{i+1}. {item['Запит (Назва)']} (Автори: {', '.join(item['Введені автори'])})")
    
    col_run, col_clear = st.columns([1, 1])
    with col_run:
        if st.button("🚀 Запустити перевірку", use_container_width=True):
            with st.spinner('Підключення до наукових баз даних...'):
                results = []
                for src in st.session_state.queue:
                    # Виклик функції перевірки
                    res = verify_source(src['Запит (Назва)'], src['Введені автори'])
                    
                    # Формування рядка таблиці
                    final_res = {
                        "Запит (Назва)": src['Запит (Назва)'],
                        "Ваші автори": ", ".join(src['Введені автори'])
                    }
                    final_res.update(res) # Додаємо статус та реальні дані
                    results.append(final_res)
                
                st.success("✅ Перевірку завершено!")
                st.table(results)
    
    with col_clear:
        if st.button("🗑 Очистити список", use_container_width=True):
            st.session_state.queue = []
            st.rerun()
