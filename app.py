import streamlit as st
import requests
import json
from datetime import datetime
# Yeni kütüphane: Sayfanın otomatik yenilenmesi için
try:
    from streamlit_autorefresh import st_autorefresh
except ImportWarning:
    st.info("Lütfen GitHub deponuza 'requirements.txt' dosyası ekleyip içine 'streamlit-autorefresh' yazın.")

# Senin güncel Firebase URL'n
URL = "https://ailechat-166f6-default-rtdb.europe-west1.firebasedatabase.app/.json"

st.set_page_config(page_title="Bizim Aile Chat", page_icon="💬", layout="centered")

# Sayfayı her 10 saniyede bir sessizce yenile (Yeni mesajları yakalamak için)
# Bu satır karşı tarafın ekranının güncellenmesini sağlar
st_autorefresh(interval=10000, key="chat_refresh")

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
            yeni_veri = {
                "user": st.session_state.kullanici_adi,
                "text": input_mesaj,
                "time": datetime.now().strftime("%H:%M")
            }
            requests.post(URL, data=json.dumps(yeni_veri))
            st.rerun()

    # 3. ADIM: Mesajları Çekme ve Ses Mantığı
    st.divider()
    st.subheader("💬 Sohbet Geçmişi")
    
    try:
        r = requests.get(URL)
        mesajlar = r.json()
        
        if mesajlar and isinstance(mesajlar, dict):
            # Mevcut mesaj sayısını kontrol et
            current_count = len(mesajlar)
            
            # Eğer yeni mesaj gelmişse (ve sayfayı ilk açan biz değilsek) ses çal
            if "last_count" in st.session_state:
                if current_count > st.session_state.last_count:
                    # SES ÇALMA BİLEŞENİ
                    st.components.v1.html(
                        """
                        <audio autoplay>
                            <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
                        </audio>
                        """,
                        height=0,
                    )
            
            # Son mesaj sayısını güncelle
            st.session_state.last_count = current_count

            # Mesajları ekrana yazdır
            for m_id in reversed(list(mesajlar.keys())):
                m = mesajlar[m_id]
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
            st.session_state.last_count = 0
            
    except Exception as e:
        st.error("Mesajlar şu an yüklenemiyor.")

    if st.button("🔄 Manuel Güncelle"):
        st.rerun()
