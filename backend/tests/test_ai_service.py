# -*- coding: utf-8 -*-
"""
AI Service modülü için testler
"""
import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from ai_service import ask_ai, get_vector_store

def test_get_vector_store():
    """Vector store oluşturma testi"""
    vector_store, embeddings = get_vector_store()
    # Vector store oluşturulabilmeli (veri dosyaları varsa)
    # None olabilir ama exception fırlatmamalı
    assert vector_store is None or hasattr(vector_store, 'similarity_search')

def test_ask_ai_empty_prompt():
    """Boş prompt testi"""
    response = ask_ai("", [])
    assert "Lütfen bir soru" in response or len(response) > 0

def test_ask_ai_with_prompt():
    """Geçerli prompt testi"""
    response = ask_ai("Test sorusu", [], use_cache=False, user_id="test")
    assert response is not None
    assert len(response) > 0

