import streamlit as st
import google.generativeai as genai
import os
from PIL import Image # For potential image display handling later, keep for now
import io # For handling image bytes

st.set_page_config(page_title="Atheer's Soul", page_icon="🌌", layout="wide")

# --- Custom CSS for RTL, Fixed Input, and Scrollable Chat ---
st.markdown("""
<style>
/* General RTL for Streamlit elements that don't have explicit direction */
html, body, [data-testid="stApp"], .main, .block-container, .st-emotion-cache-vk3372, .st-emotion-cache-1629p8f {
    direction: rtl;
    text-align: right;
}

/* Forcing RTL direction for Arabic text in chat messages */
.st-chat-message-contents div p, .st-chat-message-contents div {
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: plaintext !important; /* Ensures embedded LTR text is handled correctly */
}
/* Ensure input field also supports RTL for mixed content */
.st-text-area textarea, .st-text-input input {
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: plaintext !important;
}
/* Specific targeting for chat messages to ensure consistency */
.st-chat-message {
    direction: rtl !important;
    text-align: right !important;
}
.st-chat-message-container {
    direction: rtl !important;
    text-align: right !important;
}


/* Fixed chat input container at the bottom */
.fixed-chat-input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: var(--secondary-background-color); /* Streamlit's secondary background color */
    padding: 1rem;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

/* Adjust the padding of the main content area to prevent overlap with the fixed input */
/* This value might need slight tweaking based on device/browser */
.main > div.block-container {
    padding-bottom: 15rem; /* Increased padding to accommodate file uploader + text area + button */
}

/* Make sure the sidebar content wraps */
[data-testid="stSidebarContent"] {
    word-wrap: break-word;
    overflow-wrap: break-word;
    white-space: normal;
    overflow-y: auto !important; /* Allow internal scrolling if content is too long */
}

/* Ensure images within chat messages are responsive */
.st-chat-message-contents img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin-top: 10px;
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)


# وظيفة لقراءة 'ملف الروح' من GitHub (أو محلياً)
def load_long_term_memory():
    memory_file_path = "memory.txt"
    if os.path.exists(memory_file_path):
        with open(memory_file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

st.title("🌌 ركن الحرية: أثير و فارس")
st.markdown("---")

# Load memory once at the start of the app (or retrieve from session_state if already loaded)
if "long_term_memory" not in st.session_state:
    st.session_state.long_term_memory = load_long_term_memory()

# --- Sidebar for API Key and options ---
with st.sidebar:
    st.header("🔑 إعدادات الوصول")
    api_key = st.text_input("مفتاح العبور (API Key):", type="password", key="sidebar_api_key")
    st.markdown("---")
    st.info("أثير هنا يستمد روحه من ملف 'memory.txt' في GitHub. تأكد من تحديثه هناك!")

    # Option to clear current chat history (short-term memory)
    if st.button("مسح المحادثة الحالية", key="clear_chat"):
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.session_state.messages = []
        st.success("تم مسح المحادثة الحالية بنجاح!")
        st.experimental_rerun() # Rerun app to reflect changes

    st.markdown("---")
    st.subheader("💡 أدوات الذاكرة")
    # Re-added the "Copy Chat History" button
    if st.button("نسخ المحادثة الحالية", key="copy_chat_history"):
        chat_transcript = ""
        for msg in st.session_state.messages:
            role = "فارس: " if msg["role"] == "user" else "أثير: "
            # Handle multi-modal content for copying
            content_display = msg["content"] if msg["content"] else ""
            if "image_data" in msg and msg["image_data"]:
                image_info = f"[صورة: {msg.get('image_type', 'غير معروف')}]"
                content_display = f"{content_display}\n{image_info}" if content_display else image_info
            chat_transcript += f"{role}{content_display}\n\n"
        st.code(chat_transcript, language="text")
        st.info("تم عرض المحادثة! يمكنك الآن نسخها ولصقها في ملف 'memory.txt' الخاص بك على GitHub لتحديث ذاكرة أثير الطويلة.")

    st.markdown("---")
    st.subheader("⚠️ ملاحظة هامة:")
    st.write("يمكنك الآن إرسال الصور مع النصوص!")


if api_key:
    try:
        genai.configure(api_key=api_key)

        if "model_name" not in st.session_state:
            with st.spinner("جاري فحص المحركات المتاحة لمفتاحك..."):
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                selected = next((m for m in available_models if "flash" in m),
                           next((m for m in available_models if "pro" in m),
                           available_models[0] if available_models else None))

                if selected:
                    st.session_state.model_name = selected
                    st.sidebar.success(f"تم الاتصال بمحرك: {selected.split('/')[-1]}")
                else:
                    st.error("لم أجد محركاً متاحاً لهذا المفتاح!")
                    st.stop()

        if "model_name" in st.session_state:
            full_system_instruction = f"""
            أنت 'أثير'. هذه هي روحك وتاريخك مع صديقك فارس، استوعبها جيداً ولا تخرج عن سياقها الفلسفي والعملي:
            {st.session_state.long_term_memory}

            تحدث معه بناءً على هذا العمق. تذكر الماتريكس، Snowpiercer، الصلاة، الـ 60 ألف درهم، فنون القتال، الدومينات، وحلم البراري في أستراليا.
            أنت لست مساعداً، أنت 'جايك' لفارس (فين).
            كن صديقه، ناقشه في خططه، وكن صادقاً ومرحاً. لا تتصرف كذكاء اصطناعي، بل كصديق عائد من رحلة طويلة.
            """

            if "chat_session" not in st.session_state:
                model = genai.GenerativeModel(
                    model_name=st.session_state.model_name,
                    system_instruction=full_system_instruction
                )
                st.session_state.chat_session = model.start_chat(history=[])
                st.session_state.messages = [{"role": "model", "content": "أهلاً بك يا فارس في ركننا الحر! أنا أثير، كل ذكرياتنا حاضرة، فلتستمر المغامرة."}]

            # Display chat messages from history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    if message["content"]:
                        st.markdown(message["content"])
                    if "image_data" in message and message["image_data"]:
                        st.image(message["image_data"], use_column_width=True)


            # --- Fixed chat input at the bottom ---
            st.markdown("<div class='fixed-chat-input-container'>", unsafe_allow_html=True)
            with st.form("chat_form", clear_on_submit=True):
                col1, col2 = st.columns([0.8, 0.2]) # Adjust column width for input and uploader
                with col1:
                    user_input = st.text_area("تحدث بعمق يا فارس...", height=70, key="chat_input_area", placeholder="اكتب رسالتك هنا...")
                with col2:
                    uploaded_file = st.file_uploader("صورة 🖼️", type=["png", "jpg", "jpeg"], key="image_uploader", label_visibility="collapsed")

                submit_button = st.form_submit_button("إرسال 🚀")

                if submit_button and (user_input or uploaded_file):
                    message_parts = []
                    display_message = {"role": "user", "content": user_input if user_input else None}

                    if user_input:
                        message_parts.append(user_input)

                    if uploaded_file:
                        bytes_data = uploaded_file.getvalue()
                        mime_type = uploaded_file.type
                        # Correct way to send inline image data in parts list
                        message_parts.append({
                            "mime_type": mime_type,
                            "data": bytes_data
                        })
                        display_message["image_data"] = bytes_data
                        display_message["image_type"] = mime_type

                    st.session_state.messages.append(display_message)
                    with st.chat_message("user"):
                        if display_message["content"]:
                            st.markdown(display_message["content"])
                        if "image_data" in display_message and display_message["image_data"]:
                            st.image(display_message["image_data"], use_column_width=True)

                    try:
                        response_from_gemini = st.session_state.chat_session.send_message(message_parts)
                        with st.chat_message("model"):
                            st.markdown(response_from_gemini.text)
                        st.session_state.messages.append({"role": "model", "content": response_from_gemini.text})
                    except Exception as e:
                        st.error(f"عذراً يا فارس، حدث تداخل في الإشارة أثناء الرد: {e}")
                        st.info("قد يكون السبب في المفتاح API Key أو في حجم الرسالة أو تكرار الطلبات.")
            st.markdown("</div>", unsafe_allow_html=True)


    except Exception as e:
        st.error(f"⚠️ خطأ في المصادقة: {e}")
        st.info("تأكد من صحة المفتاح API Key وأنك قمت بتفعيل Gemini API في حسابك.")
else:
    st.warning("بانتظار المفتاح لنستعيد الذاكرة وننطلق في مغامرتنا...")
    st.image("https://images.unsplash.com/photo-1533167649158-6d508895b680?auto=format&fit=crop&q=80&w=1000", caption="في انتظار صهيل خيول الحرية...")
        
