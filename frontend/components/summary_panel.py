# -*- coding: utf-8 -*-
"""
Summary Panel Component - Display conversation summary and sources

Shows conversation summary and used documents.
"""
import streamlit as st
import requests
from typing import Optional, List, Dict


def summary_panel_component(
    backend_url: str,
    token: str,
    conversation_id: str
) -> Optional[str]:
    """
    Summary panel component
    
    Returns:
        Summary text or None
    """
    with st.expander("📋 Konuşma Özeti ve Kaynaklar", expanded=False):
        if st.button("🔄 Özeti Yenile"):
            with st.spinner("Özet oluşturuluyor..."):
                try:
                    # Get conversation summary
                    response = requests.get(
                        f"{backend_url}/api/v2/memory/summary/{conversation_id}",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        summary = data.get("summary", "")
                        
                        if summary:
                            st.markdown(f"**Özet:**\n\n{summary}")
                        else:
                            st.info("Henüz özet oluşturulmamış.")
                    else:
                        st.warning("Özet alınamadı.")
                
                except Exception as e:
                    st.error(f"Özet hatası: {str(e)}")
        
        # Show used documents from last message
        st.markdown("**Kullanılan Kaynaklar:**")
        # This would be populated from chat response
        st.caption("Kaynaklar son mesajdan alınacak")


def show_used_sources(used_documents: List[Dict]):
    """Display used documents/sources"""
    if not used_documents:
        st.info("Bu yanıt için kaynak kullanılmadı.")
        return
    
    st.markdown("**Kullanılan Kaynaklar:**")
    for idx, doc in enumerate(used_documents[:5], 1):
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{idx}. {doc.get('title', 'Belge')}**")
                if doc.get('snippet'):
                    st.caption(doc['snippet'][:150] + "...")
            with col2:
                score = doc.get('score', 0)
                st.metric("İlgililik", f"{score:.2f}")
            
            if doc.get('doc_type'):
                st.caption(f"Tip: {doc['doc_type']} | Departman: {doc.get('department', 'N/A')}")
            
            st.divider()



