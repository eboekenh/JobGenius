# JobGenius

Basit bir Streamlit uygulaması: yüklediğiniz iş ilanı / başvuru CSV/TSV dosyalarındaki "Requirements" sütununu ayrıştırır ve gereksinimleri okunabilir maddelere böler. İsteğe bağlı olarak yapıştırılan metni de işler ve Hugging Face inference API ile kariyer-koç tarzı öneriler alabilirsiniz.

## Dosyalar
- `JobGenius.py` - Ana Streamlit uygulaması.

## Gereksinimler
- Python 3.8+
- Paketler: `streamlit`, `pandas`, `python-dotenv`, `requests`

## Kurulum
Windows PowerShell için örnek adımlar:

1. Proje dizinine gidin:

   cd 'C:\Users\birli\Documents\GitHub\JobGenius'

2. (Opsiyonel) sanal ortam oluşturup aktifleştirin:

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

3. Paketleri kurun:

   pip install --upgrade pip
   pip install streamlit pandas python-dotenv requests

4. (Hugging Face kullanacaksanız) `.env` dosyası oluşturun ve içine:

   HUGGINGFACE_API_TOKEN=your_token_here

   Not: Token oluşturmak için https://huggingface.co/settings/tokens adresini kullanın.

## Çalıştırma

Streamlit uygulamasını başlatın:

python -m streamlit run JobGenius.py

veya

streamlit run JobGenius.py

Tarayıcı otomatik açılmazsa terminalde çıkan URL'yi kopyalayın (genellikle http://localhost:8501).

## Kullanım
- "Choose a file" ile CSV/TSV dosyası yükleyin. Uygulama otomatik olarak dosyayı ayrıştırmaya çalışır.
- İsterseniz CSV içeriğini veya sadece "Requirements" sütununu sağ üstteki kutuya yapıştırıp "Process pasted text" butonuna basın.
- Eğer "Requirements" sütunu bulunursa uygulama maddeleri çıkarır ve kopyalayabileceğiniz bir metin alanı sunar.
- "Ask HF (career coach)" butonuna basarsanız Hugging Face API çağrısı yapılır (HUGGINGFACE_API_TOKEN gereklidir).

## Hata ayıklama / Sık sorunlar
- Yapıştırılan metin için çıktı yoksa:
  - Metindeki sütun adlarını kontrol edin; `Requirements` sütunu mevcut mu?
  - Uygulama içinde DEBUG alanında tespit edilen delimiter ve dosya örneği gösterilir; ona bakın.
- Hugging Face çağrısı çalışmıyorsa:
  - `.env` içindeki `HUGGINGFACE_API_TOKEN` doğru mu kontrol edin.
  - Ağ veya API limitleri nedeniyle hata alabilirsiniz; hata mesajı uygulamada gösterilir.

## Güvenlik ve maliyet
- Hugging Face inference API ücretlendirilebilir. Token'ınızı güvenli tutun ve herkese açık repoya koymayın.

## Katkıda bulunma
İyileştirme önerileri, hata düzeltmeleri veya yeni özellikler için PR açabilirsiniz.

## Lisans
Bu proje MIT lisansı altında yayımlanmıştır. (İstiyorsanız lisans dosyası ekleyin.)
