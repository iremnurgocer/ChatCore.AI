# -*- coding: utf-8 -*-
"""
Module: Summary Service
Description: LLM-based summarization for conversations and documents.
"""
from typing import Optional, List, Dict
from services.ai_service import AIService

from core.config import get_settings
from core.logger import APILogger, ErrorCategory

settings = get_settings()


class SummaryService:
    """Service for generating summaries using LLM"""
    
    async def summarize_conversation(
        self,
        messages: List[Dict],
        max_length: int = 200
    ) -> str:
        """
        Summarize a conversation
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_length: Maximum summary length in words
        
        Returns:
            Summary text
        """
        if not messages:
            return "No conversation to summarize."
        
        # Extract conversation text
        conversation_text = "\n".join([
            f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}"
            for msg in messages
            if isinstance(msg, dict) and msg.get('content')
        ])
        
        # Create summarization prompt
        prompt = f"""Aşağıdaki konuşmayı özetle. Özet {max_length} kelimeden uzun olmamalı ve ana konuları kapsamalı.

Konuşma:
{conversation_text}

Özet:"""
        
        try:
            async with AIService() as ai:
                summary, _ = await ai.generate(
                    prompt=prompt,
                    conversation_history=None,
                    context=None
                )
            
            return summary.strip()
        
        except Exception as e:
            APILogger.log_error(
                "/summary/conversation",
                e,
                None,
                ErrorCategory.AI_ERROR
            )
            # Fallback: simple summary
            return self._simple_summary(messages, max_length)
    
    async def summarize_document(
        self,
        text: str,
        max_length: int = 150
    ) -> str:
        """
        Summarize a document
        
        Args:
            text: Document text
            max_length: Maximum summary length in words
        
        Returns:
            Summary text
        """
        if not text or len(text.strip()) < 50:
            return "Document too short to summarize."
        
        # Truncate if too long (to avoid token limits)
        if len(text) > 5000:
            text = text[:5000] + "..."
        
        prompt = f"""Aşağıdaki belgeyi özetle. Özet {max_length} kelimeden uzun olmamalı ve ana noktaları kapsamalı.

Belge:
{text}

Özet:"""
        
        try:
            async with AIService() as ai:
                summary, _ = await ai.generate(
                    prompt=prompt,
                    conversation_history=None,
                    context=None
                )
            
            return summary.strip()
        
        except Exception as e:
            APILogger.log_error(
                "/summary/document",
                e,
                None,
                ErrorCategory.AI_ERROR
            )
            # Fallback: simple summary
            return self._simple_summary([{"content": text}], max_length)
    
    def _simple_summary(
        self,
        messages: List[Dict],
        max_length: int
    ) -> str:
        """Fallback simple summary (first N words)"""
        text_parts = [
            msg.get('content', '')
            for msg in messages
            if isinstance(msg, dict) and msg.get('content')
        ]
        full_text = " ".join(text_parts)
        words = full_text.split()[:max_length]
        return " ".join(words) + ("..." if len(full_text.split()) > max_length else "")


# Global instance
summary_service = SummaryService()

