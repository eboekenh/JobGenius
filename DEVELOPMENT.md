# JobGenius — Geliştirme Dokümantasyonu

Bu doküman projede şu ana kadar yapılanları, kısa/orta/uzun vadede yapılması gerekenleri ve uygulanabilir adımları içerir. Hedef: CSV/TSV içindeki `Requirements` sütununu ayrıştırmak, Hugging Face üzerinden analizler üretip kaydetmek, job-tracker ile ilan takibi ve ileride kullanıcı-beceri eşleştirmesi ve referans/cover letter üretimi.

## Özet
- Amaç: İş ilanı/basvuru verilerinden gereksinimleri çıkarmak, AI destekli analizler üretmek, sonuçları kalıcı tutmak ve iş ilanlarını takip etmek.
- Teknoloji: Streamlit, pandas, requests (Hugging Face), python-dotenv, SQLite (öneri), ileride embedding/FAISS veya dış DB.

## Mevcut durum (yapıldı)
- `JobGenius.py`:
  - Dosya yükleme (`st.file_uploader`) ve metin yapıştırma (`st.text_area`) eklendi.
  - Encoding ve delimiter tespiti ile debug örneği gösteriliyor.
  - `parse_requirements` fonksiyonu eklendi; paragraf/satır/virgül bazlı ayırma yapıyor.
  - Pasted text ve uploaded file işleme akışı eklendi; sonuçları UI'da gösteriyor.
  - Hugging Face çağrısı için `ask_hf` fonksiyonu eklendi (token `.env` içinde `HUGGINGFACE_API_TOKEN`).
- `README.md` eklendi ve temel kullanım yönergeleri yazıldı.

## Hızlı test / bilinen sorunlar
- HF çağrısı çalışmıyorsa:
  - `.env` içindeki token doğru mu kontrol edin.
  - Ağ, timeout veya HF model erişimi engellenmiş olabilir.
- Yapıştırılan CSV’de `Requirements` sütunu yoksa uygulama bu sütunu bulamadığını bildirir.
- Streamlit otomatik reload dev modunda dosya kaydetme gerektirir; kaydetmeden test etme beklenen sonucu vermez.

## Öncelikli (kısa vadeli) yapılacaklar
1. HF çağrı güvenilirliğini artır: retry/backoff ve okunur hata mesajları ekle.
2. Analiz sonuçlarını kalıcı kaydet (SQLite önerisi).
3. Pasted-text akışında parse → job kaydet → requirement satırlarını kaydet akışı ekle.
4. HF butonu ile yapılan analizlerin `analyses` tablosuna eklenmesi.

## Orta vadeli yapılacaklar
1. Basit Job Tracker UI: kayıtlı job’ları listele, detay göster, status güncelle.
2. Kullanıcı beceri profili ve eşleştirme: requirement ↔ skills karşılaştırması (basit token set veya daha sonra embedding).
3. Referans mektubu ve cover-letter generator: HF prompt şablonları ile otomatik üretim.

## Uzun vadeli / opsiyonel geliştirmeler
- Çoklu kullanıcı, kimlik doğrulama ve veri izolasyonu.
- Semantic matching: embedding tabanlı benzerlik (FAISS/Milvus).
- Deployment: Docker + servis platformları, CI/CD.

## Örnek uygulanabilir görev listesi (adım adım)
1. `db.py` oluştur: SQLite bağlantısı, tabloları oluşturma fonksiyonları ve insert/list helper'lar.
2. `JobGenius.py` içine:
   - Pasted veya uploaded veriyi parse ettikten sonra `insert_job()` çağrısı yap.
   - Her requirement için `insert_requirement()` çağrısı yap.
   - HF butonuna basıldığında `insert_analysis()` kaydı oluştur.
3. Basit `Job Tracker` bölümü ekle: `st.sidebar` veya yeni `st.expander` ile kayıtlı job listesi ve detay görünümü.
4. Test: örnek CSV ile tam akışı doğrula (kaydetme, görüntüleme, HF testi).

## Önerilen DB şeması (SQLite)

SQL örnekleri:

CREATE TABLE jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT,
  row_index INTEGER,
  raw_requirements TEXT,
  created_at TEXT,
  status TEXT
);

CREATE TABLE requirements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER,
  requirement_text TEXT,
  normalized_text TEXT,
  FOREIGN KEY(job_id) REFERENCES jobs(id)
);

CREATE TABLE analyses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER,
  model TEXT,
  prompt TEXT,
  result_text TEXT,
  created_at TEXT,
  FOREIGN KEY(job_id) REFERENCES jobs(id)
);

## Güvenlik ve maliyet uyarıları
- `.env` içindeki HF token’ı asla herkese açık repoya koymayın.
- HF inference ücretlendirilebilir; toplu otomatik çağrılardan kaçının veya kullanım sınırı koyun.
- Kişisel veri saklıyorsanız ileride şifreleme veya erişim kontrolü düşünün.

## Deploy notları
- Geliştirme için `python -m streamlit run JobGenius.py` kullanın.
- Production için Dockerize edip Streamlit Cloud, Render, Azure vb. üzerinde çalıştırabilirsiniz.

## Sonraki adım önerisi
- Ben `db.py` ve `JobGenius.py` içine temel persist akışını ekleyebilirim (SQLite). Onay verirsen:`
  - `db.py` oluştururum (connection + create_tables + helper fonksiyonlar).
  - `JobGenius.py`'ye paste/upload sonrası kaydetme ve Job Tracker UI eklerim.

---

Bu dokümanı proje referansı olarak kullanabiliriz; istersen kısa bir görev listesi halinde GitHub Issues/ToDos da oluşturabilirim.
