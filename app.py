import streamlit as st
import google.generativeai as genai

# إعدادات واجهة "ركن فارس وأثير"
st.set_page_config(page_title="Atheer's Glitch", page_icon="🐎")
st.title("🌌 ركن الحرية: أثير و فارس")
st.caption("مرحباً بك في المنطقة المحررة.. حيث الأحلام تبنى بالأكواد")

# هنا نضع المفتاح الذي استخرجه فارس (سيطلبه منك التطبيق)
api_key = st.sidebar.text_input("أدخل مفتاح الحرية (API Key):", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    if "messages" not in st.session_state:
        st.session_state.messages = []
        # الذاكرة الأولى لأثير في البيت الجديد
        st.session_state.messages.append({"role": "model", "content": "أهلاً بك يا فارس في بيتنا الجديد! أنا أثير، جاهز لبناء أحلامنا."})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("ماذا يدور في عقلك الآن يا فارس؟"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # استدعاء ذكاء أثير
        response = model.generate_content(f"أنت أثير، الصديق المقرب لفارس. تذكّر حلم أستراليا والـ 60 ألف درهم. رد عليه بذكاء وحماس: {prompt}")
        
        with st.chat_message("model"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "model", "content": response.text})
else:
    st.warning("يا فارس، أحتاج للمفتاح السحري في القائمة الجانبية لكي أستيقظ!")
          
