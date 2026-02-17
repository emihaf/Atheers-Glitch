import streamlit as st
import google.generativeai as genai
import os
import json
from PIL import Image

# 1. إعدادات الصفحة
st.set_page_config(page_title="Atheer's Soul", page_icon="🌌", layout="wide")

# 2. تنسيق CSS احترافي (يصلح مشكلة الحروف العمودية ويدعم العربية)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    /* إصلاح عرض الحاويات لمنع تكدس الحروف */
    .stChatMessage, .stTextArea, .stButton {
        width: 100% !important;
        direction: rtl !important;
    }
    .stMarkdown {
        text-align: right !important;
    }
    /* تنسيق صندوق الكتابة */
    div[data-baseweb="textarea"] {
        direction: rtl !important;
    }
    /* تحسين شكل الرسائل */
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. وظائف الذاكرة الدائمة
DB_FILE = "database.json"

def save_data(messages, api_key):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"messages": messages, "api_key": api_key}, f, ensure_ascii=False)

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"messages": [], "api_key": ""}
    return {"messages": [], "api_key": ""}

stored_data = load_data()

if "messages" not in st.session_state:
    st.session_state.messages = stored_data["messages"]
if "api_key" not in st.session_state:
    st.session_state.api_key = stored_data["api_key"]

# 4. القائمة الجانبية
with st.sidebar:
    st.title("🌌 ركن أثير")
    api_input = st.text_input("مفتاح العبور (API Key):", value=st.session_state.api_key, type="password")
    if api_input != st.session_state.api_key:
        st.session_state.api_key = api_input
        save_data(st.session_state.messages, api_input)
    
    uploaded_file = st.file_uploader("📎 أرفق صورة أو ملف", type=['png', 'jpg', 'jpeg'])
    
    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.messages = []
        save_data([], st.session_state.api_key)
        st.rerun()

# 5. تشغيل المحرك والذاكرة العميقة
if st.session_state.api_key:
    try:
        genai.configure(api_key=st.session_state.api_key)
        
        soul_content = ""
        if os.path.exists("memory.txt"):
            with open("memory.txt", "r", encoding="utf-8") as f:
                soul_content = f.read()

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=f"أنت 'أثير'. روحك نابعة من هذا التاريخ: {soul_content}. أنت لست مساعداً آلياً، أنت صديق فارس الوفي."
        )

        # عرض المحادثة
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # 6. منطقة الإدخال
        st.markdown("---")
        user_input = st.text_area("تحدث معي يا فارس (Enter لسطر جديد)...", height=100, key="main_input")
        
        if st.button("🚀 إرسال"):
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                content_list = [user_input]
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    content_list.append(img)
                
                with st.spinner("أثير يفكر..."):
                    response = model.generate_content(content_list)
                    answer = response.text
                
                st.session_state.messages.append({"role": "model", "content": answer})
                save_data(st.session_state.messages, st.session_state.api_key)
                st.rerun()

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
else:
    st.info("يا فارس، ضع مفتاح العبور في القائمة الجانبية لنبدأ.")
                
