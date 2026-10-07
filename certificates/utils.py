from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_certificate(name, email, certificate_id):
    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    # Title
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(
        width / 2,
        height - 150,
        "CERTIFICATE"
    )

    # Subtitle
    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(
        width / 2,
        height - 200,
        "OF PARTICIPATION"
    )

    # Main text
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        width / 2,
        height - 280,
        "This certificate is awarded to"
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(
        width / 2,
        height - 330,
        name
    )

    # Description
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        width / 2,
        height - 390,
        "for successfully participating in the event."
    )

    # Email
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(
        width / 2,
        height - 430,
        f"Email: {email}"
    )

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return buffer