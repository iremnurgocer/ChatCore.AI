# -*- coding: utf-8 -*-
"""
Module: AI Service
Description: Async multi-provider AI integration service using httpx.AsyncClient.
"""
import json
import time
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import httpx

from core.config import get_settings
from core.logger import APILogger, ErrorCategory
from services.cache_service import get_cache_service

settings = get_settings()
cache_service = get_cache_service()

# System Prompt Template
SYSTEM_PROMPT_TEMPLATE = """You are a professional digital assistant for {company_name}.

Your role:
- Provide accurate and helpful responses based on the company's internal information
- Answer in a clear, professional manner
- Only use information provided in the context
- Do not make assumptions about information not available
- Answer questions about employees, projects, and departments

If a user's question is not related to {company_name}'s internal information, politely explain that you can only assist with company-related matters."""

SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.format(company_name=settings.COMPANY_NAME)


class AIService:
    """Async AI service with multi-provider support"""
    
    def __init__(self):
        self.http_client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.http_client = httpx.AsyncClient(timeout=60.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_client:
            await self.http_client.aclose()
    
    async def generate(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict]] = None,
        context: Optional[str] = None,
        provider: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """
        Generate AI response with context
        
        Returns:
            (response_text, metadata) where metadata includes:
            - provider_used
            - token_count (if available)
            - latency_ms
        """
        provider = provider or settings.AI_PROVIDER
        start_time = time.time()
        
        # Check cache
        context_hash = ""
        if conversation_history:
            last_messages = conversation_history[-2:] if len(conversation_history) >= 2 else conversation_history
            context_str = "|".join([m.get('content', '')[:50] for m in last_messages if isinstance(m, dict)])
            import hashlib
            context_hash = hashlib.md5(context_str.encode()).hexdigest()
        
        cached_response = await cache_service.get_ai_response(
            prompt, provider, user_id or "", context_hash
        )
        if cached_response:
            return cached_response, {"provider_used": provider, "cached": True}
        
        # Generate response based on provider
        try:
            if provider == "GEMINI":
                response, metadata = await self._generate_gemini(prompt, conversation_history, context)
            elif provider == "OPENAI":
                response, metadata = await self._generate_openai(prompt, conversation_history, context)
            elif provider == "AZURE":
                response, metadata = await self._generate_azure(prompt, conversation_history, context)
            elif provider == "OLLAMA":
                response, metadata = await self._generate_ollama(prompt, conversation_history, context)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            latency_ms = (time.time() - start_time) * 1000
            metadata["latency_ms"] = round(latency_ms, 2)
            metadata["provider_used"] = provider
            
            # Cache response
            await cache_service.set_ai_response(
                prompt, provider, response, user_id or "", context_hash
            )
            
            return response, metadata
        
        except Exception as e:
            APILogger.log_error(
                "/api/chat",
                e,
                user_id,
                ErrorCategory.AI_ERROR
            )
            raise
    
    async def _generate_gemini(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict]] = None,
        context: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """Generate response using Gemini API"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        
        if not self.http_client:
            self.http_client = httpx.AsyncClient(timeout=60.0)
        
        # Build prompt with context
        system_msg = SYSTEM_PROMPT
        if context:
            system_msg = f"{SYSTEM_PROMPT}\n\nŞirket Bilgileri:\n{context}"
        
        # Build contents array
        contents = []
        
        # Add conversation history
        if conversation_history:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            for m in recent_history:
                if isinstance(m, dict):
                    role = m.get('role', 'user')
                    content = m.get('content', '')
                    # Gemini uses 'model' instead of 'assistant'
                    gemini_role = 'model' if role == 'assistant' else 'user'
                    contents.append({
                        "role": gemini_role,
                        "parts": [{"text": content}]
                    })
        
        # Add current prompt with system message
        user_text = f"{system_msg}\n\nSoru: {prompt}"
        contents.append({
            "role": "user",
            "parts": [{"text": user_text}]
        })
        
        # Try models in order
        models_to_try = [
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-pro"
        ]
        
        for model_name in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
                
                response = await self.http_client.post(url, json={"contents": contents})
                
                if response.status_code == 200:
                    data = response.json()
                    if "candidates" in data and len(data["candidates"]) > 0:
                        candidate = data["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            text = candidate["content"]["parts"][0].get("text", "").strip()
                            if text:
                                return text, {"model": model_name}
                
                if response.status_code == 401:
                    raise ValueError("Invalid Gemini API key")
                if response.status_code == 429:
                    raise ValueError("Gemini API rate limit exceeded")
            
            except httpx.HTTPError:
                continue
        
        raise ValueError("All Gemini models failed")
    
    async def _generate_openai(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict]] = None,
        context: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """Generate response using OpenAI API"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        
        if not self.http_client:
            self.http_client = httpx.AsyncClient(timeout=60.0)
        
        # Build messages
        messages = []
        
        system_msg = SYSTEM_PROMPT
        if context:
            system_msg = f"{SYSTEM_PROMPT}\n\nŞirket Bilgileri:\n{context}"
        
        messages.append({"role": "system", "content": system_msg})
        
        if conversation_history:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            valid_history = [
                m for m in recent_history
                if isinstance(m, dict) and "role" in m and "content" in m
            ]
            messages.extend(valid_history)
        
        messages.append({"role": "user", "content": prompt})
        
        # Call OpenAI API
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        response = await self.http_client.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise ValueError(f"OpenAI API error: {response.status_code}")
        
        data = response.json()
        if "choices" not in data or len(data["choices"]) == 0:
            raise ValueError("OpenAI returned no choices")
        
        text = data["choices"][0]["message"]["content"].strip()
        token_count = data.get("usage", {}).get("total_tokens")
        
        return text, {"model": "gpt-3.5-turbo", "token_count": token_count}
    
    async def _generate_azure(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict]] = None,
        context: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """Generate response using Azure OpenAI"""
        if not settings.AZURE_OPENAI_API_KEY or not settings.AZURE_OPENAI_ENDPOINT:
            raise ValueError("Azure OpenAI credentials not configured")
        
        if not self.http_client:
            self.http_client = httpx.AsyncClient(timeout=60.0)
        
        # Build messages (same as OpenAI)
        messages = []
        
        system_msg = SYSTEM_PROMPT
        if context:
            system_msg = f"{SYSTEM_PROMPT}\n\nŞirket Bilgileri:\n{context}"
        
        messages.append({"role": "system", "content": system_msg})
        
        if conversation_history:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            valid_history = [
                m for m in recent_history
                if isinstance(m, dict) and "role" in m and "content" in m
            ]
            messages.extend(valid_history)
        
        messages.append({"role": "user", "content": prompt})
        
        # Call Azure OpenAI API
        url = f"{settings.AZURE_OPENAI_ENDPOINT}/openai/deployments/{settings.AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=2024-02-15-preview"
        headers = {
            "api-key": settings.AZURE_OPENAI_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 600
        }
        
        response = await self.http_client.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise ValueError(f"Azure OpenAI API error: {response.status_code}")
        
        data = response.json()
        if "choices" not in data or len(data["choices"]) == 0:
            raise ValueError("Azure OpenAI returned no choices")
        
        text = data["choices"][0]["message"]["content"].strip()
        token_count = data.get("usage", {}).get("total_tokens")
        
        return text, {"model": settings.AZURE_OPENAI_DEPLOYMENT, "token_count": token_count}
    
    async def _generate_ollama(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict]] = None,
        context: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """Generate response using Ollama"""
        if not self.http_client:
            self.http_client = httpx.AsyncClient(timeout=120.0)
        
        # Build full prompt
        system_msg = SYSTEM_PROMPT
        if context:
            system_msg = f"{SYSTEM_PROMPT}\n\nŞirket Bilgileri:\n{context}"
        
        full_prompt = f"{system_msg}\n\nSoru: {prompt}"
        
        if conversation_history:
            recent_history = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
            history_text = "\n".join([
                f"{m.get('role', 'user')}: {m.get('content', '')}"
                for m in recent_history
                if isinstance(m, dict)
            ])
            if history_text:
                full_prompt = f"{full_prompt}\n\nÖnceki Konuşma:\n{history_text}"
        
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        }
        
        response = await self.http_client.post(url, json=payload)
        
        if response.status_code != 200:
            raise ValueError(f"Ollama API error: {response.status_code}")
        
        data = response.json()
        text = data.get("response", "").strip()
        
        if not text:
            raise ValueError("Ollama returned empty response")
        
        return text, {"model": settings.OLLAMA_MODEL}


# Global instance (use async context manager in routes)
ai_service = AIService()

