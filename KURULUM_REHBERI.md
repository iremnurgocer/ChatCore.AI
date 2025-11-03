# ChatCore.AI - Kurulum Rehberi

## 🎯 Hızlı Başlangıç

### 1. Genel Kurulum
Önce projeyi kurun:
```batch
# Windows
kurulum.bat

# macOS/Linux
chmod +x kurulum.sh
./kurulum.sh
```

### 2. AI Sağlayıcı Seçin

Hangi AI servisini kullanmak istiyorsunuz?

| Servis | Fiyat | Kurulum | Kalite | Hız | Önerilen |
|--------|-------|---------|--------|-----|----------|
| **Gemini** | Ücretsiz | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Başlangıç için |
| **Ollama** | Ücretsiz | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Yerel kullanım |
| **OpenAI** | Ücretli | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ En iyi kalite |
| **Azure** | Ücretli | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Kurumsal |

## 📚 Detaylı Kurulum Rehberleri

### 🟢 Ücretsiz Seçenekler

#### Google Gemini (Önerilen - Ücretsiz)
- ✅ Azure/OpenAI benzeri bulut servisi
- ✅ Sadece API key gerekli
- ✅ Günlük sorgu limiti var ama yeterli
- ✅ Kurulum gerektirmez

**Kurulum:**
```batch
# Windows
kurulum.bat  # Gemini varsayılan olarak gelir

# macOS/Linux
./kurulum.sh
```

**Detaylı Rehber:** `KURULUM_GEMINI.md` (henüz oluşturulmadı)

#### Ollama (Yerel - Ücretsiz)
- ✅ Tamamen ücretsiz, sınırsız
- ✅ Verileriniz dışarı gitmiyor
- ⚠️ Model indirme gerekir (2-4GB)
- ⚠️ Yerel kaynak gerektirir

**Kurulum:**
```batch
# Windows
kurulum_ollama.bat

# macOS/Linux
chmod +x kurulum_ollama.sh
./kurulum_ollama.sh
```

**Detaylı Rehber:** [KURULUM_OLLAMA.md](KURULUM_OLLAMA.md)

### 🔵 Ücretli Seçenekler

#### OpenAI
- ✅ En iyi AI kalitesi
- ✅ Çok hızlı
- ✅ Kolay kurulum
- ⚠️ Kullanım başına ücret

**Kurulum:**
```batch
# Windows
kurulum_openai.bat

# macOS/Linux
chmod +x kurulum_openai.sh
./kurulum_openai.sh
```

**Detaylı Rehber:** [KURULUM_OPENAI.md](KURULUM_OPENAI.md)

#### Azure OpenAI
- ✅ Kurumsal kalite
- ✅ Yüksek güvenlik
- ✅ Azure entegrasyonu
- ⚠️ Kullanım başına ücret
- ⚠️ Azure hesabı gerekli

**Kurulum:**
```batch
# Windows
kurulum_azure.bat

# macOS/Linux
chmod +x kurulum_azure.sh
./kurulum_azure.sh
```

**Detaylı Rehber:** [KURULUM_AZURE.md](KURULUM_AZURE.md)

## 🚀 Servisleri Başlatma

Hangi platform kullanıyorsanız kullanın, servisleri başlatmak için:

```batch
# Windows
baslat.bat

# macOS/Linux
chmod +x baslat.sh
./baslat.sh
```

## 🔄 AI Sağlayıcı Değiştirme

AI sağlayıcınızı değiştirmek için:

1. İlgili kurulum scriptini çalıştırın:
   - `kurulum_ollama.bat` / `kurulum_ollama.sh`
   - `kurulum_openai.bat` / `kurulum_openai.sh`
   - `kurulum_azure.bat` / `kurulum_azure.sh`

2. Backend'i yeniden başlatın:
   ```batch
   baslat.bat  # veya ./baslat.sh
   ```

## ❓ Hangi Servisi Seçmeliyim?

### Benim için en uygun servis nedir?

**Ücretsiz başlamak istiyorum:**
→ **Gemini** veya **Ollama**
- Gemini: Azure benzeri, sadece API key
- Ollama: Tamamen yerel, model indirme gerekir

**En iyi kalite istiyorum:**
→ **OpenAI**
- En gelişmiş modeller
- Hızlı yanıt
- Kolay kurulum

**Kurumsal kullanım:**
→ **Azure OpenAI**
- Enterprise özellikler
- Azure entegrasyonu
- Yüksek güvenlik

**Gizlilik önemli:**
→ **Ollama**
- Veriler dışarı gitmiyor
- Offline çalışabilir
- Tamamen yerel

## 🔧 Sorun Giderme

### Hangi servisi kullanıyorum?
`backend/.env` dosyasını açın ve `AI_PROVIDER` değerine bakın:
```env
AI_PROVIDER=GEMINI  # veya OLLAMA, OPENAI, AZURE
```

### Servis çalışmıyor
1. `backend/.env` dosyasını kontrol edin
2. API key'lerin doğru olduğundan emin olun
3. Backend loglarını kontrol edin
4. İlgili servisin kurulum rehberine bakın

### Servis değiştirmek istiyorum
1. Yeni servis için kurulum scriptini çalıştırın
2. Backend'i yeniden başlatın
3. Test edin

## 📖 Ek Dokümantasyon

- [Ollama Kurulum](KURULUM_OLLAMA.md)
- [OpenAI Kurulum](KURULUM_OPENAI.md)
- [Azure OpenAI Kurulum](KURULUM_AZURE.md)

## 💡 İpuçları

1. **Başlangıç için Gemini önerilir** - Ücretsiz ve kolay
2. **Yerel kullanım için Ollama** - Gizlilik ve sınırsız
3. **Üretim için OpenAI/Azure** - En iyi kalite ve hız

## 🆘 Yardım

Sorun yaşıyorsanız:
1. İlgili servisin kurulum rehberini okuyun
2. `backend/.env` dosyasını kontrol edin
3. Backend loglarını inceleyin
4. GitHub Issues'da sorun bildirin

---

**Son Güncelleme:** 2024

