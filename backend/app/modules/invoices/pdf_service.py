from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from decimal import Decimal


class InvoicePDFService:
    @staticmethod
    def generate_pdf(invoice):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        y = height - 50
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, f"INVOICE {invoice.invoice_number}")
        y -= 30
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Status: {invoice.status}")
        y -= 20
        p.drawString(50, y, f"Issue Date: {invoice.issue_date}")
        y -= 20
        p.drawString(50, y, f"Due Date: {invoice.due_date}")
        y -= 20
        p.drawString(50, y, f"Currency: {invoice.currency}")
        y -= 40
        
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "Description")
        p.drawString(250, y, "Qty")
        p.drawString(300, y, "Unit Price")
        p.drawString(380, y, "Tax")
        p.drawString(450, y, "Total")
        y -= 20
        p.line(50, y, 550, y)
        y -= 15
        
        p.setFont("Helvetica", 9)
        for line in invoice.lines:
            p.drawString(50, y, str(line.description)[:40])
            p.drawString(250, y, str(line.quantity))
            p.drawString(300, y, str(line.unit_price))
            p.drawString(380, y, str(line.tax_amount))
            p.drawString(450, y, str(line.line_total))
            y -= 15
            if y < 100:
                p.showPage()
                y = height - 50
        
        y -= 20
        p.line(50, y, 550, y)
        y -= 20
        p.drawString(400, y, f"Subtotal: {invoice.subtotal}")
        y -= 15
        p.drawString(400, y, f"Tax: {invoice.tax_amount}")
        y -= 15
        p.setFont("Helvetica-Bold", 10)
        p.drawString(400, y, f"Total: {invoice.total}")
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
