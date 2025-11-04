# -*- coding: utf-8 -*-
"""
Rapor Servis Modülü

Bu modül chat geçmişi için PDF rapor oluşturma özelliği sunar.
Kullanıcıların sohbet geçmişlerini PDF formatında indirebilmesini sağlar.

Ne İşe Yarar:
- Chat geçmişini PDF formatına çevirme
- Rapor oluşturma ve formatlama
- PDF indirme özelliği

Kullanım:
- generate_report() - PDF rapor oluştur
- export_conversation() - Conversation'ı PDF'e çevir
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import datetime
from typing import List, Dict, Any

def create_chat_report(chat_history: List[Dict[str, str]], output_path: str = "chat_report.pdf") -> str:
    """
    Chat geçmişinden PDF rapor oluşturur
    
    Args:
        chat_history: 'role' ve 'content' anahtarlarına sahip mesaj dictionary'lerinin listesi
        output_path: PDF'in kaydedileceği yol
        
    Returns:
        Oluşturulan PDF dosyasının yolu
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Chat Raporu", styles["Title"]))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"Tarih: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    content.append(Spacer(1, 20))

    for msg in chat_history:
        role = "Kullanıcı" if msg.get("role") == "user" else "Asistan"
        content_text = msg.get("content", "")
        content.append(Paragraph(f"<b>{role}:</b> {content_text}", styles["Normal"]))
        content.append(Spacer(1, 12))

    doc.build(content)
    return output_path
