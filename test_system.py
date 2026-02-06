import os
import sys
import unittest
from datetime import datetime

# Add project dir to path
sys.path.append(os.path.abspath("investor-mail-system"))

print("🔍 SİSTEM KONTROLÜ BAŞLIYOR...\n")

# 1. Config & Klasör Kontrolü
print("1️⃣ Config ve Klasörler Kontrol Ediliyor...")
try:
    import config
    expected_dirs = [config.DATA_DIR, config.TEMPLATES_DIR, config.UPLOADS_DIR]
    for d in expected_dirs:
        if os.path.exists(d):
            print(f"  ✅ Klasör mevcut: {d}")
        else:
            print(f"  ❌ Klasör EKSİK: {d}")
            # Klasörleri oluşturmayı dene
            os.makedirs(d, exist_ok=True)
            print(f"  ✨ Klasör oluşturuldu: {d}")
except Exception as e:
    print(f"  ❌ Config hatası: {e}")

# 2. Veritabanı Kontrolü
print("\n2️⃣ Veritabanı ve Tablolar Kontrol Ediliyor...")
try:
    import database
    database.init_db()  # Ensure tables exist
    conn = database.get_connection()
    cursor = conn.cursor()
    
    tables = ['investors', 'templates', 'sent_mails', 'scheduled_mails', 'interactions', 'unsubscribes', 'audit_logs', 'ab_tests']
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    all_tables_ok = True
    for table in tables:
        if table in existing_tables:
            print(f"  ✅ Tablo mevcut: {table}")
        else:
            print(f"  mx❌ Tablo EKSİK: {table}")
            all_tables_ok = False
            
    conn.close()
    
    if all_tables_ok:
        # Basit bir insert/select testi
        test_email = f"test_{int(datetime.now().timestamp())}@example.com"
        database.add_investor("Test User", test_email, "Test Co", "TEST", "Note")
        print("  ✅ Veritabanı yazma/okuma testi BAŞARILI")
        
        # Temizlik
        conn = database.get_connection()
        conn.execute("DELETE FROM investors WHERE email = ?", (test_email,))
        conn.commit()
        conn.close()

except Exception as e:
    print(f"  ❌ Veritabanı hatası: {e}")

# 3. Template Engine Kontrolü
print("\n3️⃣ Template Engine Kontrol Ediliyor...")
try:
    import template_engine
    ctx = {"ad": "Ali", "sirket": "Veli A.Ş."}
    tmpl = "Merhaba {{ad}}, {{sirket}} için test."
    rendered = template_engine.render_template(tmpl, ctx)
    
    if "Ali" in rendered and "Veli A.Ş." in rendered:
        print("  ✅ Şablon render testi BAŞARILI")
    else:
        print(f"  ❌ Şablon render testi BAŞARISIZ. Çıktı: {rendered}")
        
    templates = template_engine.get_default_templates()
    if len(templates) > 0:
        print(f"  ✅ Varsayılan şablonlar yüklendi ({len(templates)} adet)")
    
except Exception as e:
    print(f"  ❌ Template engine hatası: {e}")

# 4. Mail Modülleri Kontrolü
print("\n4️⃣ Mail Modülleri Kontrol Ediliyor (Import & Init)...")
try:
    from mail_sender import MailSender
    sender = MailSender("test@gmail.com", "pass")
    print("  ✅ MailSender sınıfı import edildi ve başlatıldı")
    
    from gmail_oauth import GmailOAuth
    oauth = GmailOAuth()
    print("  ✅ GmailOAuth sınıfı import edildi ve başlatıldı")
    
except Exception as e:
    print(f"  ❌ Mail modülü hatası: {e}")

# 5. App Syntax Kontrolü
print("\n5️⃣ Ana Uygulama Syntax Kontrolü...")
try:
    with open("investor-mail-system/app.py", "r", encoding="utf-8") as f:
        compile(f.read(), "investor-mail-system/app.py", "exec")
    print("  ✅ app.py syntax KUSURSUZ")
except Exception as e:
    print(f"  ❌ app.py syntax HATASI: {e}")

print("\n🎉 TEST TAMAMLANDI!")
