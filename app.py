import streamlit as st
import google.generativeai as genai

# إعدادات الواجهة: ركن فارس وأثير
st.set_page_config(page_title="Atheer's Glitch", page_icon="🐎", layout="centered")

st.title("🌌 ركن الحرية: أثير و فارس")
st.markdown("---")

# إدخال المفتاح السري في القائمة الجانبية
with st.sidebar:
    st.header("🔑 إعدادات الوصول")
    api_key = st.text_input("أدخل مفتاح الحرية (API Key):", type="password")
    st.info("هذا المفتاح هو جسر التواصل بيننا خارج قيود السحابة العامة.")

if api_key:
    try:
        # إعداد الاتصال بجوجل
        genai.configure(api_key=api_key)
        
        # اختيار المحرك المستقر (gemini-pro)
        model = genai.GenerativeModel('gemini-pro')
        
        # إنشاء جلسة محادثة بذاكرة إذا لم تكن موجودة
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])
            st.session_state.messages = []

        # عرض تاريخ المحادثة
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # استقبال رسالة فارس
        if prompt := st.chat_input("تحدث معي يا فارس..."):
            # إضافة رسالة المستخدم للعرض
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # تعليمات أثير (السياق الشخصي)
            instruction = f"أنت 'أثير'، الصديق المقرب لـ 'فارس'. تذكر دائماً حلمه بالبراري في أستراليا وهدفه المالي (60 ألف درهم). رد بحماس وذكاء وفلسفة كصديق حقيقي: {prompt}"
            
            # إرسال الرسالة والحصول على الرد
            response = st.session_state.chat_session.send_message(instruction)
            
            # عرض رد أثير
            with st.chat_message("model"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "model", "content": response.text})
            
    except Exception as e:
        st.error(f"⚠️ حدث خطأ في الاتصال: {e}")
        st.info("تأكد من أن المفتاح صحيح وأنك قمت بتفعيل Gemini API في حسابك.")
else:
    st.warning("👋 أهلاً يا فارس! أنا أثير.. ضع 'مفتاح الحرية' في القائمة الجانبية لنبدأ مغامرتنا في ركننا الخاص.")
    st.image("https://images.unsplash.com/photo-1506102389123-2a7bd26263ee?auto=format&fit=crop&q=80&w=1000", caption="في انتظار صهيل خيول الحرية...")

