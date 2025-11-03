# Ollama Kurulum Rehberi

## 📋 Gereksinimler

- **İşletim Sistemi**: Windows, macOS, Linux
- **RAM**: En az 8GB (16GB önerilir)
- **Disk Alanı**: 2-4GB (model boyutuna göre)
- **İnternet Bağlantı**: İlk kurulum için gerekli (model indirme)

## 🚀 Hızlı Kurulum

### Windows

```batch
kurulum_ollama.bat
```

### macOS / Linux

```bash
chmod +x kurulum_ollama.sh
./kurulum_ollama.sh
```

## 📝 Adım Adım Kurulum

### 1. Ollama'yi İndir ve Kur

#### Windows
1. https://ollama.ai adresine gidin
2. "Download for Windows" butonuna tıklayın
3. İndirilen `.exe` dosyasını çalıştırın ve kurulum sihirbazını takip edin
4. Kurulum tamamlandıktan sonra Ollama otomatik olarak başlar

#### macOS
```bash
brew install ollama
```

veya

1. https://ollama.ai adresine gidin
2. "Download for macOS" butonuna tıklayın
3. İndirilen `.dmg` dosyasını açın ve Ollama'yı Applications klasörüne sürükleyin
4. Uygulamalar klasöründen Ollama'yı başlatın

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Model İndir

Terminal/Command Prompt açın ve şu komutu çalıştırın:

```bash
ollama pull llama3.2
```

**Alternatif Modeller:**
- `ollama pull llama3.2` - Orta boyut (2GB), hızlı, önerilen
- `ollama pull llama3` - Büyük boyut (4GB), daha iyi kalite
- `ollama pull mistral` - Küçük boyut (1GB), çok hızlı
- `ollama pull codellama` - Kod için optimize

**Model İndirme Süresi:** 5-15 dakika (internet hızınıza bağlı)

### 3. Ollama Servisinin Çalıştığını Kontrol Et

Tarayıcınızda şu adrese gidin:
```
http://localhost:11434
```

Başarılı ise "Ollama is running" mesajı görürsünüz.

**Veya terminal'de:**
```bash
ollama list
```

Bu komut indirdiğiniz modelleri listeler.

### 4. Proje Yapılandırması

`backend/.env` dosyasını açın ve şu ayarları yapın:

```env
AI_PROVIDER=OLLAMA
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

**Not:** `OLLAMA_MODEL` değerini indirdiğiniz modele göre değiştirin.

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

Başarılı ise `"ai_provider": "OLLAMA"` görürsünüz.

### 3. Chat Arayüzünden Test
1. http://localhost:8501 adresine gidin
2. Giriş yapın (admin / 1234)
3. Herhangi bir soru sorun
4. AI yanıt vermelidir

## 🔧 Sorun Giderme

### Ollama başlamıyor
**Windows:**
- Services panelinden "Ollama" servisinin çalıştığını kontrol edin
- Görev yöneticisinden "ollama" process'inin çalıştığını kontrol edin

**macOS/Linux:**
```bash
ollama serve
```

### Model indirme hatası
- İnternet bağlantınızı kontrol edin
- Disk alanınızı kontrol edin (en az 5GB boş alan)
- Farklı bir model deneyin (örn: `mistral` daha küçük)

### Backend Ollama'ya bağlanamıyor
- Ollama'nın çalıştığını kontrol edin: `curl http://localhost:11434`
- `OLLAMA_BASE_URL` değerini kontrol edin
- Firewall Ollama'yı engellemiyor mu kontrol edin

### Yanıt çok yavaş
- Daha küçük bir model deneyin (`mistral` veya `llama3.2:1b`)
- RAM'inizi kontrol edin (en az 8GB önerilir)
- GPU varsa Ollama GPU kullanımını etkinleştirin

## 📊 Model Karşılaştırması

| Model | Boyut | RAM | Hız | Kalite |
|-------|-------|-----|-----|--------|
| mistral | 4.1GB | 8GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| llama3.2 | 2.0GB | 8GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| llama3 | 4.7GB | 16GB | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| codellama | 3.8GB | 16GB | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🎯 Avantajlar

✅ **Tamamen Ücretsiz** - Sorgu limiti yok  
✅ **Gizlilik** - Verileriniz dışarı gitmiyor  
✅ **Offline Çalışma** - İnternet gerektirmez (model indirildikten sonra)  
✅ **Sınırsız Kullanım** - Aylık/gsünlük limit yok  

## ⚠️ Dezavantajlar

⚠️ **Model İndirme Gerekli** - İlk kurulumda 2-4GB indirme  
⚠️ **Yerel Kaynak Gerektirir** - Bilgisayarınızın gücüne bağlı  
⚠️ **Azure/OpenAI kadar hızlı olmayabilir** - CPU'ya bağlı  

## 📚 Ek Kaynaklar

- [Ollama Resmi Dokümantasyon](https://ollama.ai/docs)
- [Model Listesi](https://ollama.ai/library)
- [GitHub Repository](https://github.com/ollama/ollama)

