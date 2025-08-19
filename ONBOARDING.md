# JobGenius — VS Code & Çalışma Akışı Rehberi

Aşağıdaki adımlar, VS Code'u yeniden açtığında hızlıca projeyi çalıştırman ve geliştirmeye devam etmen için hazırlanmıştır. PowerShell (Windows) örnek komutları içerir.

Ön koşullar
- Python 3.8+
- Git yüklü
- VS Code yüklü

1) VS Code ile projeyi aç
- VS Code'u aç → File → Open Folder → seç: `C:\Users\birli\Documents\GitHub\JobGenius`
- Entegre terminali aç: Ctrl+`

2) Sanal ortam (öneri)
- İlk kez veya izole bir ortam istiyorsan proje kökünde bir venv oluştur:
  - python -m venv .venv
- Aktifleştir (PowerShell):
  - .\.venv\Scripts\Activate.ps1
- Sanal ortam aktifse komut satırında `(.venv)` görürsün.

3) Gerekli paketleri yükle
- Hızlı kurulum:
  - pip install --upgrade pip; pip install streamlit pandas python-dotenv requests
- İleride requirements.txt oluşturmak istersen:
  - pip freeze > requirements.txt

4) Ortam değişkenleri / .env
- `.env` dosyası proje kökünde bulunmalı (commit etmeyin).
- İçerik örneği:
  - HUGGINGFACE_API_TOKEN=your_token_here
- Alternatif: terminalde geçici olarak:
  - $env:HUGGINGFACE_API_TOKEN = "your_token_here"

5) Veritabanı tablolarını oluştur (ilk kullanım)
- db yardımcı fonksiyonunu çağırarak tabloları oluştur:
  - python -c "import db; db.create_tables()"
- Bu komut `jobgenius.db` dosyasını oluşturacaktır (eğer yoksa).

6) Uygulamayı çalıştır
- Streamlit ile başlat:
  - python -m streamlit run JobGenius.py
- Tarayıcı açılmazsa terminaldeki URL'yi (http://localhost:8501) kullan.
- Uygulamayı durdurmak için terminalde Ctrl+C.

7) Hızlı test akışı
- Uygulamada CSV yükle veya metin yapıştır → `Process pasted text` butonu ile parse et.
- Uygulama parse edip DB'ye kayıt ekliyorsa proje kökünde `jobgenius.db` oluşur.
- DB içeriğini görmek için:
  - python -c "import db; print(db.list_jobs())"

8) Git / GitHub günlük iş akışı
- Çalışmaya başlamadan önce değişiklikleri çek:
  - git pull origin main
- Yeni özellik için branch oluştur:
  - git checkout -b feature/isim
- Değişiklik yap → git add . → git commit -m "Açıklama"
- Branch’i push et:
  - git push -u origin feature/isim
- GitHub üzerinden PR aç ve merge işlemlerini oradan yap.

9) Hata/geri alma ipuçları (VS Code)
- Yanlışlıkla kapattın → File → Reopen Closed Editor.
- Kaydedilmemiş değişiklikler için Ctrl+Z geri al.
- Dosyanın geçmişini görmek için Explorer içinde dosyaya sağ-tık → Open Timeline (varsa).
- Local History eklentisi kurulursa ek kurtarma sağlar.

10) Debug & sık karşılaşılan sorunlar
- "Hugging Face token not set" hatası → .env içindeki `HUGGINGFACE_API_TOKEN` kontrol et.
- HF çağrıları hata veriyorsa Streamlit terminalindeki traceback'i kontrol et. Uygulama içinde de hata mesajı gösteriliyor.
- Delimiter/encoding sorunları için uygulamada DEBUG alanı var (detected encoding / detected delimiter / sample).

11) Önerilen VS Code eklentileri
- Python (Microsoft)
- Pylance
- SQLite (Alexcvzz veya benzeri)
- GitLens
- DotENV

12) Kapanış ve iyi uygulamalar
- Hassas bilgileri (`.env`, API token) repoya commit etmeyin.
- DB dosyasını commit etmeyin (local cache olarak kalsın).
- Küçük değişiklikleri anlamlı commit mesajlarıyla sık sık commit edin.
- Büyük işleri feature branch’te yapıp PR ile birleştirin.

Hızlı komut özet (PowerShell — proje kökünde):
- .venv oluştur ve aktif et:
  python -m venv .venv; .\.venv\Scripts\Activate.ps1
- Paketler:
  pip install streamlit pandas python-dotenv requests
- DB tabloları:
  python -c "import db; db.create_tables()"
- Streamlit çalıştır:
  python -m streamlit run JobGenius.py
- Git commit ve push:
  git add .; git commit -m "mesaj"; git push

Bu rehberi repoya ekledim. Eğer istersen bunu daha kısa bir checklist veya VS Code görev (tasks.json) hâline getirebilirim.
