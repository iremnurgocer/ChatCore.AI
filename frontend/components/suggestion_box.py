# -*- coding: utf-8 -*-
"""
Suggestion Box Component - Next question suggestions

Shows AI-generated next question suggestions.
"""
import streamlit as st
import requests
from typing import List, Optional


def suggestion_box_component(
    backend_url: str,
    token: str,
    last_response: str
) -> Optional[str]:
    """
    Suggestion box component
    
    Returns:
        Selected suggestion text or None
    """
    if not last_response:
        return None
    
    st.markdown("**💡 Önerilen Sorular:**")
    
    try:
        # Get suggestions from backend
        response = requests.post(
            f"{backend_url}/api/v2/suggestions",
            headers={"Authorization": f"Bearer {token}"},
            json={"last_response": last_response[:500]},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get("suggestions", [])
            
            if suggestions:
                cols = st.columns(min(len(suggestions), 3))
                for idx, suggestion in enumerate(suggestions[:3]):
                    with cols[idx % 3]:
                        if st.button(suggestion, key=f"suggestion_{idx}", use_container_width=True):
                            return suggestion
            else:
                st.caption("Henüz öneri yok.")
        else:
            # Fallback suggestions
            fallback = [
                "Daha fazla detay verebilir misin?",
                "Bu konuyla ilgili başka ne öğrenebilirim?",
                "Bununla ilgili örnekler var mı?"
            ]
            cols = st.columns(3)
            for idx, suggestion in enumerate(fallback):
                with cols[idx]:
                    if st.button(suggestion, key=f"fallback_{idx}", use_container_width=True):
                        return suggestion
    
    except Exception as e:
        st.caption("Öneriler yüklenemedi.")
    
    return None



