import streamlit as st
import requests
import json

# --- OPENROUTER ANAHTARIN ---
# Kanka buradaki tırnakların içine OpenRouter'daki anahtarının TAMAMINI yapıştır
API_KEY = "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"

def model_yanit_al(prompt):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "HTTP-Referer": "http://localhost:8501", 
                "X-Title": "OmerGPT"
            },
            data=json.dumps({
                "model": "meta-llama/llama-3.1-8b-instruct:free", # En sağlam ücretsiz model
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        res = response.json()
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"🚨 Bağlantı Hatası: {str(e)}"

# Arayüz ve Sohbet kodların zaten GitHub'da olduğu gibi kalsın...