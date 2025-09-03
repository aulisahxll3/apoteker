import streamlit as st
import google.generativeai as genai
import os

# --- KONFIGURASI APLIKASI STREAMLIT ---
# Set judul halaman dan ikon
st.set_page_config(
    page_title="Apoteker Gemini 💊",
    page_icon="💊",
    layout="wide"
)

# Judul utama aplikasi
st.title("Apoteker Gemini 💊")
st.markdown("Tanyakan seputar obat, dan saya akan memberikan informasi yang relevan.")
st.markdown("---")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Mengambil API Key dari secrets Streamlit untuk keamanan
# Pastikan Anda telah menambahkan 'API_KEY' ke secrets di Streamlit Cloud.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ API Key tidak ditemukan. Harap tambahkan 'GEMINI_API_KEY' di Streamlit Secrets.")
    st.stop() # Hentikan eksekusi jika API Key tidak ada

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Saya adalah seorang apoteker. Berikan pertanyaan tentang obat. Jawaban singkat. Tolak pertanyaan selain tentang obat."]
    },
    {
        "role": "model",
        "parts": ["Baik! Saya akan menjawab pertanyaan Anda tentang Obat."]
    }
]

# ==============================================================================
# FUNGSI UTAMA CHATBOT
# ==============================================================================

# Konfigurasi Gemini API
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Kesalahan saat mengkonfigurasi API Key: {e}")
    st.stop()

# Inisialisasi model
@st.cache_resource
def get_model():
    """Menginisialisasi model Gemini dan menyimpannya (caching)."""
    return genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )

model = get_model()

# Mengelola riwayat chat di Session State Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Tambahkan konteks awal ke riwayat chat
    for message in INITIAL_CHATBOT_CONTEXT:
        st.session_state.messages.append(message)
        
# Tampilkan riwayat chat
for message in st.session_state.messages:
    # Gunakan st.chat_message untuk antarmuka yang lebih baik
    if message["role"] in ["user", "model"]:
        with st.chat_message(message["role"]):
            st.markdown(message["parts"][0])
            
# Input pengguna dari antarmuka Streamlit
if prompt := st.chat_input("Tanyakan sesuatu tentang obat..."):
    # Tambahkan prompt pengguna ke riwayat
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim riwayat chat ke model
    chat = model.start_chat(history=st.session_state.messages)
    
    with st.spinner("Apoteker sedang memikirkan jawabannya..."):
        try:
            response = chat.send_message(prompt, request_options={"timeout": 60})
            
            if response and response.text:
                full_response = response.text
                # Tambahkan respons model ke riwayat
                st.session_state.messages.append({"role": "model", "parts": [full_response]})
                with st.chat_message("model"):
                    st.markdown(full_response)
            else:
                st.error("Maaf, terjadi kesalahan saat mendapatkan respons. Silakan coba lagi.")
        
        except Exception as e:
            st.error(f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
