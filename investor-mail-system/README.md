# Yatırımcı Mail Sistemi

Gmail entegrasyonlu, Streamlit tabanlı yatırımcı mail sistemi.

## Kurulum

1. **Gerekli paketleri yükle:**
```bash
pip install -r requirements.txt
```

2. **Uygulamayı başlat:**
```bash
streamlit run app.py
```

3. **Tarayıcıda aç:** http://localhost:8501

## Gmail Ayarları

Gmail ile kullanmak için **Uygulama Şifresi** gerekiyor:

1. Gmail > Hesabı Yönet > Güvenlik
2. 2 Adımlı Doğrulama'yı aç
3. Uygulama Şifreleri > Yeni şifre oluştur
4. Oluşan 16 haneli şifreyi uygulamada kullan

## Özellikler

- 📧 Gmail SMTP entegrasyonu
- 👥 TXT/CSV/Excel ile yatırımcı yükleme
- 📝 HTML mail şablonları
- 📤 Toplu/seçici mail gönderimi
- 📊 Dashboard ve istatistikler
- 📜 Gönderim geçmişi

## Dosya Yapısı

```
investor-mail-system/
├── app.py              # Ana uygulama
├── config.py           # Ayarlar
├── database.py         # SQLite işlemleri
├── mail_sender.py      # Gmail SMTP
├── template_engine.py  # Şablon motoru
├── data/               # Veritabanı
├── templates/          # Mail şablonları
└── uploads/            # Geçici yüklemeler
```
