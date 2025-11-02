from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import datetime

def create_chat_report(chat_history, output_path="chat_report.pdf"):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("ChatCore.AI Raporu", styles["Title"]))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"Tarih: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    content.append(Spacer(1, 20))

    for msg in chat_history:
        role = "Kullanıcı" if msg["role"] == "user" else "Asistan"
        content.append(Paragraph(f"<b>{role}:</b> {msg['content']}", styles["Normal"]))
        content.append(Spacer(1, 12))

    doc.build(content)
    return output_path
