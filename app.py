import streamlit as st
import requests
import json
from datetime import datetime

# Senin güncel Firebase URL'n
URL = "https://ailechat-166f6-default-rtdb.europe-west1.firebasedatabase.app/.json"

st.set_page_config(page_title="Bizim Aile Chat", page_icon="💬", layout="centered")

# Başlık tasarımı
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
            # Firebase'e mesajı gönder
            yeni_veri = {
                "user": st.session_state.kullanici_adi,
                "text": input_mesaj,
                "time": datetime.now().strftime("%H:%M")
            }
            requests.post(URL, data=json.dumps(yeni_veri))

            # --- SES BİLDİRİMİ ---
            # Mesaj gönderildiğinde 'bip' sesi çalar
            st.components.v1.html(
                """
                <audio autoplay>
                    <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
                </audio>
                """,
                height=0,
            )
            # ---------------------
            
            st.rerun()

    # 3. ADIM: Mesajları Listeleme
    st.divider()
    st.subheader("💬 Sohbet Geçmişi")
    
    try:
        r = requests.get(URL)
        mesajlar = r.json()
        
        # Veritabanı boş değilse ve düzgün bir formatta ise oku
        if mesajlar and isinstance(mesajlar, dict):
            for m_id in reversed(list(mesajlar.keys())):
                m = mesajlar[m_id]
                
                # Sadece doğru formattaki (sözlük) mesajları göster
                if isinstance(m, dict):
                    kisi = m.get("user", "Anonim")
                    icerik = m.get("text", "")
                    saat = m.get("time", "--:--")
                    
                    if kisi == st.session_state.kullanici_adi:
                        st.success(f"**Sen**: {icerik}  \n*(saat: {saat})*")
                    else:
                        st.info(f"**{kisi}**: {icerik}  \n*(saat: {saat})*")
        else:
            st.write("Henüz mesaj yok. İlk mesajı sen yaz! 😊")
            
    except Exception as e:
        st.error("Mesajlar şu an yüklenemiyor, lütfen sayfayı yenileyin.")

    # Manuel Yenileme Butonu
    if st.button("🔄 Mesajları Güncelle"):
        st.rerun()

# Sayfayı her 15 saniyede bir otomatik yenile (Karşı tarafın ekranı güncellensin diye)
count = st_autorefresh(interval=15000, key="frefresher")

# Mesaj sayısını kontrol edip ses çalma mantığı
if "last_msg_count" not in st_session_state:
    st_session_state.last_msg_count = len(mesajlar) if mesajlar else 0

current_msg_count = len(mesajlar) if mesajlar else 0

# Eğer mesaj sayısı artmışsa ve mesajı yazan sen değilsen ses çal
if current_msg_count > st_session_state.last_msg_count:
    st.components.v1.html(
        """
        <audio autoplay>
            <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
        </audio>
        """,
        height=0,
    )
    st_session_state.last_msg_count = current_msg_count
