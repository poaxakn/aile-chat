import streamlit as st
import requests
import json
from datetime import datetime

# Firebase Realtime Database URL
# Sonuna /.json eklemeyi unutma
URL = "https://ailechat-166f6-default-rtdb.firebaseio.com/.json"

st.set_page_config(page_title="Bizim Aile Chat", page_icon="💬", layout="centered")

# Sayfa Başlığı
st.markdown("<h2 style='text-align: center; color: #4CAF50;'>🏠 Aile Meclisi Sohbet</h2>", unsafe_allow_html=True)

# 1. ADIM: Kullanıcı İsmini Kaydetme
if "kullanici_adi" not in st.session_state:
    st.info("Sohbete katılmak için lütfen isminizi yazın.")
    isim = st.text_input("Adınız:", placeholder="Örn: Caner, Annem, Babam...")
    if st.button("Giriş Yap"):
        if isim:
            st.session_state.kullanici_adi = isim
            st.rerun()
        else:
            st.warning("Lütfen bir isim girin!")
else:
    # 2. ADIM: Mesaj Gönderme Alanı
    st.write(f"Hoş geldin, **{st.session_state.kullanici_adi}**!")
    
    with st.form("mesaj_gonder_form", clear_on_submit=True):
        input_mesaj = st.text_input("Mesajınız:", placeholder="Bir şeyler yazın...")
        gonder_btn = st.form_submit_button("Gönder 🚀")
        
        if gonder_btn and input_mesaj:
            # Firebase'e gidecek veri yapısı
            yeni_veri = {
                "user": st.session_state.kullanici_adi,
                "text": input_mesaj,
                "time": datetime.now().strftime("%H:%M") # Saat ekleme
            }
            requests.post(URL, data=json.dumps(yeni_veri))
            st.rerun()

    # 3. ADIM: Mesajları Listeleme
    st.divider()
    st.subheader("💬 Sohbet Geçmişi")
    
    try:
        r = requests.get(URL)
        mesajlar = r.json()
        
        if mesajlar:
            # En son mesajın en üstte görünmesi için listeyi ters çeviriyoruz
            for m_id in reversed(list(mesajlar.keys())):
                m = mesajlar[m_id]
                kisi = m.get("user", "Anonim")
                icerik = m.get("text", "")
                saat = m.get("time", "--:--")
                
                # Mesaj balonu tasarımı
                if kisi == st.session_state.kullanici_adi:
                    st.success(f"**Sen**: {icerik}  \n*(saat: {saat})*")
                else:
                    st.info(f"**{kisi}**: {icerik}  \n*(saat: {saat})*")
        else:
            st.write("Henüz mesaj yok. İlk mesajı sen yaz!")
            
    except Exception as e:
        st.error(f"Veriler çekilemedi: {e}")

    # Manuel Yenileme Butonu
    if st.button("🔄 Mesajları Güncelle"):
        st.rerun()