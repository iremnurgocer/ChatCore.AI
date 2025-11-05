# -*- coding: utf-8 -*-
"""
File Uploader Component - Drag-drop document upload

Streamlit component for uploading PDF, DOCX, XLSX files.
"""
import streamlit as st
import requests
from typing import Optional, Dict


def file_uploader_component(backend_url: str, token: str, department: Optional[str] = None) -> Optional[Dict]:
    """
    File uploader component
    
    Returns:
        Dict with upload result or None
    """
    st.subheader("📄 Belge Yükle")
    
    uploaded_file = st.file_uploader(
        "PDF, DOCX, XLSX veya TXT dosyası seçin",
        type=["pdf", "docx", "xlsx", "txt"],
        help="Maksimum dosya boyutu: 50MB"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            title = st.text_input("Belge Başlığı (opsiyonel)", value=uploaded_file.name.rsplit(".", 1)[0])
        
        with col2:
            dept = st.text_input("Departman (opsiyonel)", value=department or "")
        
        if st.button("📤 Yükle ve İndeksle", type="primary"):
            with st.spinner("Dosya yükleniyor ve işleniyor..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {}
                    if title:
                        data["title"] = title
                    if dept:
                        data["department"] = dept
                    
                    response = requests.post(
                        f"{backend_url}/api/v2/files/upload",
                        headers={"Authorization": f"Bearer {token}"},
                        files=files,
                        data=data,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Dosya başarıyla yüklendi! ({result.get('chunks_indexed', 0)} parça indekslendi)")
                        return result
                    else:
                        error_msg = response.json().get("detail", "Yükleme hatası")
                        st.error(f"❌ Hata: {error_msg}")
                        return None
                
                except Exception as e:
                    st.error(f"❌ Yükleme hatası: {str(e)}")
                    return None
    
    return None



