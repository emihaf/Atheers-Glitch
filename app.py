import streamlit as st
import google.generativeai as genai

# إعدادات الصفحة
st.set_page_config(page_title="Atheer & Fares", page_icon="🐎", layout="centered")

st.title("🌌 ركن الحرية: أثير و فارس")
st.markdown("---")

# إدخال المفتاح السري في القائمة الجانبية
with st.sidebar:
    st.header("🔑 إعدادات الوصول")
    api_key = st.text_input("أدخل مفتاح الحرية (API Key):", type="password")
    st.info("أنا أبحث الآن عن أفضل طريق للعبور...")

if api_key:
    try:
        # 1. إعداد الاتصال
        genai.configure(api_key=api_key)
        
        # 2. البحث الذكي عن الموديل المتاح (هنا تكمن القوة)
        if "model_name" not in st.session_state:
            with st.spinner("جاري فحص المحركات المتاحة لمفتاحك..."):
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                # ترتيب الأولوية: Flash أولاً للسرعة، ثم Pro، ثم أي موديل متاح
                selected = next((m for m in available_models if "flash" in m), 
                           next((m for m in available_models if "pro" in m), 
                           available_models[0] if available_models else None))
                
                if selected:
                    st.session_state.model_name = selected
                    st.sidebar.success(f"تم الاتصال بمحرك: {selected.split('/')[-1]}")
                else:
                    st.error("لم أجد محركاً متاحاً لهذا المفتاح!")

        # 3. تشغيل المحادثة
        if "model_name" in st.session_state:
            model = genai.GenerativeModel(st.session_state.model_name)
            
            if "chat_session" not in st.session_state:
                st.session_state.chat_session = model.start_chat(history=[])
                st.session_state.messages = []

            # عرض تاريخ المحادثة
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # استقبال رسالة فارس
            if prompt := st.chat_input("تحدث معي يا فارس..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # تعليمات أثير الشخصية
                instruction = f"أنت 'أثير'، الصديق المقرب لـ 'فارس'. تذكر دائماً حلمه بالبراري في أستراليا وهدفه المالي (60 ألف درهم). رد بذكاء وحماس وصداقة حقيقية: {prompt}"
                
                try:
                    response = st.session_state.chat_session.send_message(instruction)
                    with st.chat_message("model"):
                        st.markdown(response.text)
                    st.session_state.messages.append({"role": "model", "content": response.text})
                except Exception as e:
                    st.error(f"عذراً يا فارس، حدث تداخل في الإشارة: {e}")
            
    except Exception as e:
        st.error(f"⚠️ خطأ في المصادقة: تأكد من صحة المفتاح API Key.")
else:
    st.warning("👋 يا فارس، ضع 'مفتاح الحرية' لنبدأ الرحلة.")
    st.image("https://images.unsplash.com/photo-1533167649158-6d508895b680?auto=format&fit=crop&q=80&w=1000")

