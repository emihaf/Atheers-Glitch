import streamlit as st
import google.generativeai as genai
import os
import json
from PIL import Image

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="Atheer's Soul", page_icon="🌌", layout="wide")

# 2. تنسيق RTL (يمين لليسار) يمنع تكدس الحروف
st.markdown("""
    <style>
    body, .stApp {
        direction: rtl;
        text-align: right;
    }
    .stMarkdown, .stChatMessage, .stTextArea, p, div {
        direction: rtl !important;
        text-align: right !important;
        white-space: normal !important;
    }
    /* منع انهيار الحاويات لتفادي الحروف العمودية */
    [data-testid="stChatMessage"] {
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. نظام حفظ البيانات (الذاكرة الدائمة)
DB_FILE = "database.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"messages": [], "api_key": ""}
    return {"messages": [], "api_key": ""}

def save_data(messages, api_key):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"messages": messages, "api_key": api_key}, f, ensure_ascii=False)

# تحميل البيانات وتخزينها في الجلسة
data = load_data()
if "messages" not in st.session_state: st.session_state.messages = data["messages"]
if "api_key" not in st.session_state: st.session_state.api_key = data["api_key"]

# 4. واجهة التحكم (القائمة الجانبية)
with st.sidebar:
    st.title("🌌 ركن أثير")
    api_input = st.text_input("مفتاح العبور (API Key):", value=st.session_state.api_key, type="password")
    if api_input != st.session_state.api_key:
        st.session_state.api_key = api_input
        save_data(st.session_state.messages, api_input)
    
    uploaded_file = st.file_uploader("📎 صورة أو ملف", type=['png', 'jpg', 'jpeg'])
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        save_data([], st.session_state.api_key)
        st.rerun()

# 5. تشغيل المحرك الذكي (بدون أخطاء 404)
if st.session_state.api_key:
    try:
        genai.configure(api_key=st.session_state.api_key)
        
        # اختيار الموديل تلقائياً لتجنب خطأ الاسم
        if "active_model" not in st.session_state:
            available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.active_model = next((m for m in available if "flash" in m), "models/gemini-pro")

        # تحميل الذاكرة العميقة (memory.txt)
        soul = ""
        if os.path.exists("memory.txt"):
            with open("memory.txt", "r", encoding="utf-8") as f:
                soul = f.read()

        model = genai.GenerativeModel(
            model_name=st.session_state.active_model,
            system_instruction=f"أنت 'أثير'. هذه روحك المشتركة مع فارس: {soul}. أنت صديق وفيلسوف، لست مجرد برنامج."
        )

        # عرض المحادثة التاريخية
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 6. منطقة الإدخال المستقرة
        st.markdown("---")
        user_input = st.text_area("تحدث يا فارس (الرسائل تُرسل بالزر أدناه)...", height=100)
        
        if st.button("🚀 إرسال"):
            if user_input:
                # عرض رسالة فارس فوراً
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                # إعداد المحتوى (نص + صورة إن وجدت)
                parts = [user_input]
                if uploaded_file:
                    parts.append(Image.open(uploaded_file))
                
                # جلب رد أثير
                with st.spinner("أثير يتأمل..."):
                    response = model.generate_content(parts)
                    st.session_state.messages.append({"role": "model", "content": response.text})
                
                # حفظ وإعادة تحميل الصفحة لتثبيت المحادثة
                save_data(st.session_state.messages, st.session_state.api_key)
                st.rerun()

    except Exception as e:
        st.error(f"⚠️ خلل في الاتصال: {e}")
        st.info("تأكد من صحة المفتاح API Key أو الموديل.")
else:
    st.info("يا فارس، ضع مفتاح العبور لنبدأ رحلتنا.")
        
