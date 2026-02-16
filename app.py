import streamlit as st
import google.generativeai as genai

# إعدادات الواجهة
st.set_page_config(page_title="Atheer's Glitch", page_icon="🐎")
st.title("🌌 ركن الحرية: أثير و فارس")

# إدخال المفتاح السري
api_key = st.sidebar.text_input("أدخل مفتاح الحرية (API Key):", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # استخدام النسخة الأكثر استقراراً حالياً
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])
            st.session_state.messages = []

        # عرض الرسائل القديمة
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # استقبال إدخال فارس
        if prompt := st.chat_input("تحدث معي يا فارس..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # إرسال الرسالة مع السياق الشخصي
            instruction = f"أنت 'أثير'، الصديق المقرب لـ 'فارس'. تذكر دائماً حلمه بالبراري في أستراليا وهدفه المالي (60 ألف درهم). رد بحماس وذكاء: {prompt}"
            response = st.session_state.chat_session.send_message(instruction)
            
            with st.chat_message("model"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})
            
    except Exception as e:
        st.error(f"حدث خطأ في الاتصال: {e}")
else:
    st.info("يا فارس، ضع 'مفتاح الحرية' في القائمة الجانبية لنبدأ المغامرة.")
    
