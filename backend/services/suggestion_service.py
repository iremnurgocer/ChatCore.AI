# -*- coding: utf-8 -*-
"""
Module: Suggestion Service
Description: Generates contextual next-question suggestions based on AI responses.
"""
from typing import List, Optional
from services.ai_service import AIService
from core.logger import APILogger, ErrorCategory


class SuggestionService:
    """Service for generating next-question suggestions"""
    
    async def generate_suggestions(
        self,
        last_response: str,
        conversation_context: Optional[List] = None,
        count: int = 3
    ) -> List[str]:
        """
        Generate next-question suggestions based on last AI response
        
        Args:
            last_response: Latest AI response text
            conversation_context: Optional conversation history
            count: Number of suggestions to generate
        
        Returns:
            List of suggested questions
        """
        if not last_response or len(last_response.strip()) < 20:
            return self._default_suggestions()
        
        try:
            # Create prompt for suggestion generation
            prompt = f"""Aşağıdaki yanıta dayalı olarak kullanıcının sorabileceği {count} adet ilgili ve yararlı soru öner.

Yanıt:
{last_response[:500]}

Sadece soruları liste halinde ver, başka açıklama yapma. Her soru tek satırda olsun."""
            
            async with AIService() as ai:
                suggestions_text, _ = await ai.generate(
                    prompt=prompt,
                    conversation_history=None,
                    context=None
                )
            
            # Parse suggestions from response
            suggestions = self._parse_suggestions(suggestions_text, count)
            
            # Fallback to default if parsing failed
            if not suggestions or len(suggestions) < count:
                suggestions.extend(self._default_suggestions()[:count - len(suggestions)])
            
            return suggestions[:count]
        
        except Exception as e:
            APILogger.log_error(
                "/suggestions/generate",
                e,
                None,
                ErrorCategory.AI_ERROR
            )
            return self._default_suggestions()[:count]
    
    def _parse_suggestions(self, text: str, count: int) -> List[str]:
        """Parse suggestions from AI response"""
        suggestions = []
        
        # Split by newlines and clean
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            
            # Remove numbering (1., 2., - , etc.)
            line = line.lstrip("0123456789.-) ")
            
            # Check if it looks like a question
            if line and ("?" in line or line.endswith("mi") or line.endswith("mı")):
                suggestions.append(line)
            
            if len(suggestions) >= count:
                break
        
        return suggestions
    
    def _default_suggestions(self) -> List[str]:
        """Default fallback suggestions"""
        return [
            "Daha fazla detay verebilir misin?",
            "Bu konuyla ilgili başka ne öğrenebilirim?",
            "Bununla ilgili örnekler var mı?"
        ]


# Global instance
suggestion_service = SuggestionService()

