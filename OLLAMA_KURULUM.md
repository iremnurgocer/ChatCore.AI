# Ollama Kurulum Rehberi - ÜCRETSİZ Yerel AI

Ollama tamamen ücretsizdir ve bilgisayarınızda yerel olarak çalışır. İnternet bağlantısı olmadan da kullanabilirsiniz!

## 🚀 Hızlı Kurulum (Windows)

1. **Ollama'yı İndirin:**
   - https://ollama.ai adresine gidin
   - "Download for Windows" butonuna tıklayın
   - İndirilen `.exe` dosyasını çalıştırıp kurun

2. **Model İndirin:**
   Kurulumdan sonra PowerShell veya CMD'de şu komutu çalıştırın:
   ```
   ollama pull llama3.2
   ```
   Veya daha küçük ve hızlı bir model:
   ```
   ollama pull llama3.2:1b
   ```

3. **Ollama'yı Başlatın:**
   Ollama genelde otomatik başlar, ama kontrol etmek için:
   ```
   ollama serve
   ```

4. **ChatCore.AI'yi Ollama'ya Ayarlayın:**
   - `backend\.env` dosyasını açın
   - `AI_PROVIDER=OLLAMA` olarak değiştirin
   - (Ollama varsayılan olarak `http://localhost:11434` adresinde çalışır)

5. **Backend'i Yeniden Başlatın:**
   - Backend penceresini kapatın
   - `baslat.bat` dosyasını çalıştırın

## ✅ Test

Tarayıcıda bir soru sorun, artık Ollama kullanıyor olmalı!

## 📝 Önerilen Modeller

- **llama3.2:1b** - En hızlı, küçük model (~1GB)
- **llama3.2** - Dengeli, orta boy (~2GB)
- **llama3.1:8b** - Daha güçlü ama daha yavaş (~4.7GB)
- **mistral** - İyi performans (~4GB)
- **phi3** - Küçük ama etkili (~2.3GB)

## 💡 Avantajlar

- ✅ Tamamen ücretsiz
- ✅ İnternet bağlantısı gerektirmez (model indirildikten sonra)
- ✅ Verileriniz hiçbir yere gönderilmez (gizlilik)
- ✅ Sorgu limiti yok
- ✅ API key gerektirmez

## ⚠️ Dezavantajlar

- İlk model indirme biraz uzun sürebilir
- Bilgisayarınızın RAM'ine bağlı olarak yavaş olabilir
- Büyük modeller için disk alanı gerektirir

