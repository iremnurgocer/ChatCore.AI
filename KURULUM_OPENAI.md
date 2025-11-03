# OpenAI Kurulum Rehberi

## 📋 Gereksinimler

- **OpenAI Hesabı**: Ücretsiz hesap oluşturulabilir
- **API Key**: OpenAI Platform'dan alınmalı
- **İnternet Bağlantı**: Sürekli gerekli (bulut servisi)
- **Kredi Kartı**: API kullanımı için gerekli (ücretsiz kredi mevcut)

## 🚀 Hızlı Kurulum

### Windows

```batch
kurulum_openai.bat
```

### macOS / Linux

```bash
chmod +x kurulum_openai.sh
./kurulum_openai.sh
```

## 📝 Adım Adım Kurulum

### 1. OpenAI Hesabı Oluştur

1. https://platform.openai.com/signup adresine gidin
2. Email adresiniz, şifreniz ve telefon numaranızı girin
3. Email doğrulaması yapın
4. Telefon numarasını doğrulayın

### 2. Ücretsiz Kredi Ekle (Opsiyonel)

1. https://platform.openai.com/account/billing adresine gidin
2. "Add payment method" (Ödeme yöntemi ekle) butonuna tıklayın
3. Kredi kartı bilgilerinizi girin
4. **İyi haber:** OpenAI size **$5 ücretsiz kredi** verir!

**⚠️ NOT:** Ücretsiz kredi bitene kadar ücretlendirilmezsiniz. Kredi bittiğinde otomatik ücretlendirme yapılır, bu yüzden limit koymanızı öneririz.

### 3. API Key Oluştur

#### Adım 1: API Keys Sayfasına Git
1. https://platform.openai.com/api-keys adresine gidin
2. "Create new secret key" (Yeni gizli anahtar oluştur) butonuna tıklayın

#### Adım 2: Key Adı Ver
1. Key için bir isim verin (örn: "ChatCore-AI")
2. "Create secret key" butonuna tıklayın

#### Adım 3: Key'i Kopyala
1. Açılan pencerede API key görünür
2. **HEMEN KOPYALAYIN!** Bu key'i bir daha göremeyeceksiniz
3. Güvenli bir yere kaydedin

**⚠️ ÖNEMLİ:** API Key'inizi kimseyle paylaşmayın! Key çalınırsa:
- Key'i hemen silin
- Yeni bir key oluşturun
- Eski key'i kullanan uygulamaları güncelleyin

### 4. Kullanım Limiti Ayarla (Önerilen)

1. https://platform.openai.com/account/limits adresine gidin
2. "Hard limit" (Sert limit) seçeneğini etkinleştirin
3. Aylık limit belirleyin (örn: $10)

Bu sayede beklenmedik ücretlerden korunursunuz.

### 5. Proje Yapılandırması

`backend/.env` dosyasını açın ve şu ayarları yapın:

```env
AI_PROVIDER=OPENAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Örnek:**
```env
AI_PROVIDER=OPENAI
OPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

**⚠️ ÖNEMLİ:**
- API Key'in başında `sk-` veya `sk-proj-` olmalı
- Key'de boşluk olmamalı
- Tırnak işareti kullanmayın

### 6. Model Seçimi

OpenAI birçok model sunar. `.env` dosyasına ekleyebilirsiniz (opsiyonel):

```env
OPENAI_MODEL=gpt-4o-mini
```

**Popüler Modeller:**
- `gpt-4o-mini` - Hızlı, ekonomik, önerilen ✅
- `gpt-4o` - En iyi kalite, orta hız
- `gpt-4-turbo` - Yüksek kalite, hızlı
- `gpt-3.5-turbo` - Ekonomik, hızlı

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

Başarılı ise `"ai_provider": "OPENAI"` görürsünüz.

### 3. Chat Arayüzünden Test
1. http://localhost:8501 adresine gidin
2. Giriş yapın (admin / 1234)
3. Herhangi bir soru sorun
4. AI yanıt vermelidir

### 4. Kullanımı Kontrol Et
1. https://platform.openai.com/usage adresine gidin
2. API kullanımınızı görüntüleyin
3. Kalan kredinizi kontrol edin

## 🔧 Sorun Giderme

### "Invalid API Key" Hatası
- API Key'i doğru kopyaladığınızdan emin olun
- Başında/sonunda boşluk olmamalı
- Key'in aktif olduğunu kontrol edin: https://platform.openai.com/api-keys

### "Insufficient quota" Hatası
- Krediniz bitmiş olabilir
- https://platform.openai.com/account/billing adresinden kontrol edin
- Yeni ödeme yöntemi ekleyin veya limit artırın

### "Rate limit exceeded" Hatası
- Çok fazla istek gönderiyorsunuz
- Biraz bekleyip tekrar deneyin
- Daha yavaş bir model kullanın (`gpt-3.5-turbo`)

### "Model not found" Hatası
- Model adını kontrol edin
- Kullandığınız model aktif mi kontrol edin
- Farklı bir model deneyin

### Yavaş Yanıt
- Model seçiminizi kontrol edin
- Daha hızlı bir model deneyin (`gpt-4o-mini` veya `gpt-3.5-turbo`)
- İnternet bağlantınızı kontrol edin

## 💰 Fiyatlandırma

OpenAI kullanım başına ücretlendirir:

### Güncel Fiyatlar (yaklaşık)
- **gpt-4o-mini**: $0.15 / 1M input tokens, $0.60 / 1M output tokens
- **gpt-4o**: $2.50 / 1M input tokens, $10 / 1M output tokens
- **gpt-4-turbo**: $10 / 1M input tokens, $30 / 1M output tokens
- **gpt-3.5-turbo**: $0.50 / 1M input tokens, $1.50 / 1M output tokens

**💡 İpucu:** Başlangıç için `gpt-4o-mini` hem hızlı hem de en ekonomiktir.

### Ücretsiz Deneme
- Hesap açtığınızda **$5 ücretsiz kredi** verilir
- Normal kullanım için yeterlidir
- Kredi bittiğinde otomatik ücretlendirme yapılır

### Maliyet Tahmini
- 1000 mesaj (ortalama): ~$0.10 - $0.50 (modele göre)
- Aylık hafif kullanım: ~$5 - $20
- Aylık yoğun kullanım: ~$50 - $200

## 🎯 Avantajlar

✅ **En İyi Kalite** - En gelişmiş AI modelleri  
✅ **Hızlı** - Düşük gecikme süresi  
✅ **Kolay Kurulum** - Sadece API key yeterli  
✅ **Güvenilir** - Yüksek uptime  

## ⚠️ Dezavantajlar

⚠️ **Ücretli** - Kullanım başına ücret  
⚠️ **İnternet Gerekli** - Offline çalışmaz  
⚠️ **Rate Limits** - Aşırı kullanımda limit  

## 📚 Ek Kaynaklar

- [OpenAI Platform Dokümantasyon](https://platform.openai.com/docs)
- [API Keys Yönetimi](https://platform.openai.com/api-keys)
- [Fiyatlandırma](https://openai.com/pricing)
- [Kullanım İstatistikleri](https://platform.openai.com/usage)

