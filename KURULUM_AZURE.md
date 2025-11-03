# Azure OpenAI Kurulum Rehberi

## 📋 Gereksinimler

- **Azure Hesabı**: Ücretsiz deneme hesabı yeterli
- **Azure OpenAI Kaynağı**: Azure Portal'da oluşturulmalı
- **İnternet Bağlantı**: Sürekli gerekli (bulut servisi)
- **API Key**: Azure Portal'dan alınmalı

## 🚀 Hızlı Kurulum

### Windows

```batch
kurulum_azure.bat
```

### macOS / Linux

```bash
chmod +x kurulum_azure.sh
./kurulum_azure.sh
```

## 📝 Adım Adım Kurulum

### 1. Azure Hesabı Oluştur

1. https://azure.microsoft.com/free/ adresine gidin
2. "Start free" butonuna tıklayın
3. Microsoft hesabınızla giriş yapın
4. Telefon numaranızı doğrulayın
5. Kredi kartı bilgilerinizi girin (ücretsiz deneme için, ücretlendirilmez)

### 2. Azure OpenAI Kaynağı Oluştur

#### Adım 1: Azure Portal'a Giriş
1. https://portal.azure.com adresine gidin
2. Azure hesabınızla giriş yapın

#### Adım 2: OpenAI Kaynağı Oluştur
1. Sol üstten "Create a resource" (Kaynak oluştur) butonuna tıklayın
2. Arama kutusuna "Azure OpenAI" yazın
3. "Azure OpenAI" seçeneğini seçin
4. "Create" butonuna tıklayın

#### Adım 3: Kaynak Ayarları
**Temel Bilgiler:**
- **Subscription (Abonelik)**: Ücretsiz deneme hesabınızı seçin
- **Resource Group (Kaynak Grubu)**: Yeni oluşturun veya mevcut birini seçin
- **Region (Bölge)**: Size en yakın bölgeyi seçin (örn: West Europe)
- **Name (İsim)**: Benzersiz bir isim verin (örn: chatcore-openai)

**Fiyatlandırma:**
- **Pricing tier**: "S0" (Standart) seçin

5. "Review + create" (İncele ve oluştur) butonuna tıklayın
6. "Create" butonuna tıklayın
7. Kaynak oluşturulması 2-5 dakika sürebilir

### 3. API Key ve Endpoint Alma

#### Adım 1: Kaynak Sayfasına Git
1. Azure Portal'da "All resources" (Tüm kaynaklar) seçeneğine tıklayın
2. Oluşturduğunuz Azure OpenAI kaynağını bulun ve tıklayın

#### Adım 2: API Key'i Kopyala
1. Sol menüden "Keys and Endpoint" (Anahtarlar ve Uç Nokta) seçeneğine tıklayın
2. **KEY 1** veya **KEY 2** altındaki değeri kopyalayın
3. **ENDPOINT** değerini de kopyalayın

**⚠️ ÖNEMLİ:** API Key'i güvenli bir yere kaydedin. Daha sonra göremeyeceksiniz!

### 4. Model Deployment Oluştur

#### Adım 1: Model Yönetimi
1. Azure OpenAI kaynağınızın sayfasında
2. Sol menüden "Model deployments" (Model dağıtımları) seçeneğine tıklayın
3. "Create" (+ Create) butonuna tıklayın

#### Adım 2: Deployment Ayarları
- **Deployment name (Dağıtım adı)**: `gpt-4o-mini` (veya istediğiniz isim)
- **Model (Model)**: `gpt-4o-mini` seçin
  - Alternatifler: `gpt-35-turbo`, `gpt-4`, `gpt-4-turbo`
- **Version (Sürüm)**: En son sürümü seçin
- **Capacity (Kapasite)**: Başlangıç için 30K TPM yeterli

4. "Create" butonuna tıklayın
5. Deployment oluşturulması 1-3 dakika sürebilir

**⚠️ NOT:** Deployment ismini not edin, `.env` dosyasında kullanacaksınız!

### 5. Proje Yapılandırması

`backend/.env` dosyasını açın ve şu ayarları yapın:

```env
AI_PROVIDER=AZURE
AZURE_OPENAI_API_KEY=your-azure-openai-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

**Örnek:**
```env
AI_PROVIDER=AZURE
AZURE_OPENAI_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
AZURE_OPENAI_ENDPOINT=https://chatcore-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

**⚠️ ÖNEMLİ:**
- `AZURE_OPENAI_ENDPOINT` değerinin sonunda `/` olmamalı (script bunu ekler)
- Deployment adı büyük-küçük harf duyarlıdır

### 6. Endpoint Formatını Kontrol Et

Endpoint şu formatta olmalı:
```
https://YOUR-RESOURCE-NAME.openai.azure.com
```

Eğer farklı bir format görüyorsanız, doğru endpoint'i kullanın.

## ✅ Kurulumu Test Et

### 1. Backend'i Başlat
```batch
# Windows
baslat.bat

# macOS/Linux
./baslat.sh
```

### 2. Test Komutu
Terminal'de:
```bash
curl http://localhost:8000/api/status
```

Başarılı ise `"ai_provider": "AZURE"` görürsünüz.

### 3. Chat Arayüzünden Test
1. http://localhost:8501 adresine gidin
2. Giriş yapın (admin / 1234)
3. Herhangi bir soru sorun
4. AI yanıt vermelidir

## 🔧 Sorun Giderme

### "Invalid API Key" Hatası
- API Key'i doğru kopyaladığınızdan emin olun
- Başında/sonunda boşluk olmamalı
- KEY 1 çalışmazsa KEY 2'yi deneyin

### "Deployment not found" Hatası
- Deployment adının doğru olduğundan emin olun
- Büyük-küçük harf duyarlıdır
- Azure Portal'dan deployment'ın aktif olduğunu kontrol edin

### "Endpoint not found" Hatası
- Endpoint URL'sinin doğru olduğundan emin olun
- Sonunda `/` olmamalı
- Format: `https://YOUR-RESOURCE-NAME.openai.azure.com`

### "Quota exceeded" Hatası
- Azure ücretsiz deneme limitini aştınız
- Ücretli plana geçmeniz gerekebilir
- Kullanımınızı Azure Portal'dan kontrol edin

### Yavaş Yanıt
- Bölge seçiminizi kontrol edin (size yakın bölge seçin)
- Model seçiminizi kontrol edin (`gpt-4o-mini` genelde hızlıdır)
- Azure kaynağınızın durumunu kontrol edin

## 💰 Fiyatlandırma

Azure OpenAI ücretlendirmesi kullanıma göre yapılır:

### Standart Modeller (yaklaşık)
- **gpt-4o-mini**: $0.15 / 1M input tokens, $0.60 / 1M output tokens
- **gpt-35-turbo**: $0.50 / 1M input tokens, $1.50 / 1M output tokens
- **gpt-4**: $30 / 1M input tokens, $60 / 1M output tokens

**💡 İpucu:** Başlangıç için `gpt-4o-mini` hem hızlı hem de ekonomiktir.

### Ücretsiz Deneme
- Azure hesabı açtığınızda **$200 kredi** verilir
- Bu kredi 30 gün geçerlidir
- Normal kullanım için yeterlidir

## 🎯 Avantajlar

✅ **Kurumsal Kalite** - Enterprise özellikler  
✅ **Yüksek Güvenlik** - Azure güvenlik standartları  
✅ **Ölçeklenebilir** - Yüksek trafik için uygun  
✅ **Azure Entegrasyonu** - Diğer Azure servisleriyle entegre  

## ⚠️ Dezavantajlar

⚠️ **Ücretli** - Kullanım başına ücret  
⚠️ **Azure Hesabı Gerekli** - Kurulum biraz karmaşık  
⚠️ **İnternet Gerekli** - Offline çalışmaz  

## 📚 Ek Kaynaklar

- [Azure OpenAI Dokümantasyon](https://learn.microsoft.com/azure/ai-services/openai/)
- [Fiyatlandırma](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/)
- [Azure Portal](https://portal.azure.com)

