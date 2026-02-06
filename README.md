# 📧 Investor Mail System

Yatırımcılara toplu mail gönderimi için modern Streamlit uygulaması.

## ✨ Özellikler

- 🔐 Gmail OAuth & App Password desteği
- 📝 Özelleştirilebilir mail şablonları
- 👥 Yatırımcı CRM sistemi
- 📊 Gönderim istatistikleri
- ⏰ Zamanlanmış mail gönderimi
- 🧪 A/B test simülasyonu

## 🚀 Kurulum

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Dosya Yapısı

```
investor-mail-system/
├── app.py              # Ana uygulama
├── database.py         # SQLite işlemleri
├── mail_sender.py      # SMTP gönderim
├── gmail_oauth.py      # OAuth2 entegrasyonu
├── template_engine.py  # Jinja2 şablon motoru
├── scheduler.py        # Zamanlanmış görevler
└── config.py           # Ayarlar
```

## 🔧 Gmail Kurulumu

**OAuth (Önerilen):**
1. Google Cloud Console'da OAuth credentials oluştur
2. `data/credentials.json` olarak kaydet
3. Uygulamadan "Google ile Giriş" yap

**App Password:**
1. Gmail > Güvenlik > 2FA aç
2. Uygulama Şifresi oluştur
3. Uygulamada giriş yap

## 👨‍💻 Geliştiriciler

**emirgunyy** & **gktrk363**
