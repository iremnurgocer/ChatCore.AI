# -*- coding: utf-8 -*-
"""
Persona Selector Component - Select AI persona

Allows users to select persona (Finance, IT, HR, Legal).
"""
import streamlit as st
import requests
from typing import Optional, Dict


def persona_selector_component(
    backend_url: str,
    token: str,
    current_persona: str = "default"
) -> Optional[str]:
    """
    Persona selector component
    
    Returns:
        Selected persona name or None
    """
    st.sidebar.markdown("### 🤖 AI Personası")
    
    try:
        # Get available personas
        response = requests.get(
            f"{backend_url}/api/v2/user/preferences/personas",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            personas = data.get("personas", {})
        else:
            personas = {
                "default": "Varsayılan",
                "finance": "Finans",
                "it": "IT",
                "hr": "İnsan Kaynakları",
                "legal": "Hukuk"
            }
    except:
        personas = {
            "default": "Varsayılan",
            "finance": "Finans",
            "it": "IT",
            "hr": "İnsan Kaynakları",
            "legal": "Hukuk"
        }
    
    selected = st.sidebar.selectbox(
        "Persona Seçin",
        options=list(personas.keys()),
        format_func=lambda x: personas.get(x, x),
        index=list(personas.keys()).index(current_persona) if current_persona in personas else 0
    )
    
    if selected != current_persona:
        # Update preference
        try:
            response = requests.put(
                f"{backend_url}/api/v2/user/preferences",
                headers={"Authorization": f"Bearer {token}"},
                json={"persona": selected},
                timeout=5
            )
            
            if response.status_code == 200:
                st.sidebar.success(f"✅ Persona güncellendi: {personas.get(selected, selected)}")
                return selected
        except:
            st.sidebar.error("Persona güncellenemedi.")
    
    return None



