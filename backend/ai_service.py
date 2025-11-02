import os
import json
import requests
from dotenv import load_dotenv

# LangChain importları
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from transformers import pipeline

# Ortam değişkenlerini yükle
load_dotenv()

# ====================================
# Ortam değişkenleri
# ====================================
AI_PROVIDER = os.getenv("AI_PROVIDER", "LOCAL").upper()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Azure OpenAI
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# Hugging Face
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "distilgpt2")

print(f"🚀 Aktif AI sağlayıcısı: {AI_PROVIDER}")


# ====================================
# Ana Fonksiyon
# ====================================
def ask_ai(prompt: str) -> str:
    """
    Kullanıcıdan gelen prompt'a göre uygun AI sağlayıcısından yanıt döndürür.
    """

    if not prompt or not prompt.strip():
        return "⚠️ Lütfen bir soru veya metin girin."

    try:
        if AI_PROVIDER == "OPENAI":
            if not OPENAI_API_KEY:
                return "⚠️ OpenAI API anahtarı bulunamadı."
            return ask_openai_langchain(prompt)

        elif AI_PROVIDER == "AZURE":
            if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
                return "⚠️ Azure API bilgileri eksik."
            return ask_azure(prompt)

        elif AI_PROVIDER == "HUGGINGFACE":
            if not HUGGINGFACE_API_KEY:
                return "⚠️ Hugging Face API anahtarı eksik."
            return ask_huggingface(prompt)

        elif AI_PROVIDER == "LOCAL":
            return ask_local(prompt)

        else:
            return f"⚠️ Tanınmayan AI_PROVIDER değeri: {AI_PROVIDER}"

    except Exception as e:
        print(f"💥 AI servis hatası: {e}")
        return f"❌ Hata: {e}"


# ====================================
# OpenAI + LangChain (RAG destekli)
# ====================================
def ask_openai_langchain(prompt: str) -> str:
    """
    OpenAI GPT ile JSON veri tabanını kullanarak akıllı yanıt döndürür.
    (employees.json, departments.json, projects.json)
    """
    try:
        # Embedding modeli
        embeddings = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # JSON verileri oku
        docs = []
        for file in ["data/employees.json", "data/departments.json", "data/projects.json"]:
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    docs.append(json.dumps(data, ensure_ascii=False))

        # FAISS vektör veri tabanı oluştur
        db = FAISS.from_texts(docs, embeddings)

        # LLM (OpenAI) modelini hazırla
        llm = OpenAI(temperature=0.3, openai_api_key=OPENAI_API_KEY)

        # LangChain QA pipeline
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=db.as_retriever(search_kwargs={"k": 3}),
            chain_type="stuff"
        )

        print(f"🧠 LangChain araması: {prompt}")
        answer = qa.run(prompt)
        return answer.strip()

    except Exception as e:
        print(f"LangChain/OpenAI hata: {e}")
        return "❌ OpenAI yanıt oluşturulamadı."


# ====================================
# Azure OpenAI (gpt-4o-mini veya eşdeğeri)
# ====================================
def ask_azure(prompt: str) -> str:
    import openai

    try:
        openai.api_type = "azure"
        openai.api_key = AZURE_OPENAI_API_KEY
        openai.api_base = AZURE_OPENAI_ENDPOINT
        openai.api_version = "2024-02-15-preview"

        response = openai.ChatCompletion.create(
            engine="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.5,
        )

        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"Azure OpenAI hata: {e}")
        return "❌ Azure yanıtı alınamadı."


# ====================================
# Hugging Face API (ücretsiz)
# ====================================
def ask_huggingface(prompt: str) -> str:
    try:
        url = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {"inputs": prompt}

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            return f"Hugging Face API hatası: {response.status_code} - {response.text}"

        data = response.json()
        if isinstance(data, list):
            return data[0].get("generated_text", "").strip()
        elif isinstance(data, dict):
            return data.get("generated_text", "").strip()
        else:
            return str(data)

    except Exception as e:
        print(f"HuggingFace hata: {e}")
        return "❌ Hugging Face modeliyle yanıt alınamadı."


# ====================================
# Yerel model (internet yoksa)
# ====================================
def ask_local(prompt: str) -> str:
    """
    İnternet bağlantısı veya API anahtarı olmadan HuggingFace transformer ile çalışır.
    """
    try:
        generator = pipeline("text-generation", model="dbmdz/bert-base-turkish-cased")
        output = generator(prompt, max_length=100, num_return_sequences=1)
        text = output[0]["generated_text"]
        return text.strip()
    except Exception as e:
        print(f"Lokal model hatası: {e}")
        return "❌ Yerel model çalıştırılırken hata oluştu."
