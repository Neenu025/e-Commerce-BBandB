from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages


#Generate PDF report
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4
from .models import *
from SHOPPER.models import *
from APP1.models import Product
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


# def report_generator(request, orders):
#     buf = io.BytesIO()
#     c = canvas.Canvas(buf, pagesize=A4, bottomup=0)
#     c.setAuthor("BBandB")
#     c.setTitle("Sales report")

#     textob = c.beginText()
#     textob.setTextOrigin(inch, inch)
#     textob.setFont("Helvetica", 14)

#     max_orders_per_page = 4
#     max_lines_per_page = 36
#     order_count = 0
#     line_count = 0
#     lines = []

#     order_count = orders.count()
#     page_count = (order_count + max_orders_per_page - 1) // max_orders_per_page

#     for page in range(page_count):
#         lines.clear()

#         start_index = page * max_orders_per_page
#         end_index = start_index + max_orders_per_page
#         page_orders = orders[start_index:end_index]

#         for order in page_orders:
#             lines.append("===========================Start===========================")
#             lines.append("Order ID:"      + str(order.id))
#             lines.append("Quantity:"      + str(order.quantity))
#             lines.append("Amount:"        + str(order.amount))
#             lines.append("Address:"       + str(order.address.address1))
#             lines.append("Payment:"       + str(order.payment_type))
#             lines.append("Date:"          + str(order.date))
#             lines.append("Order Status:"  + str(order.status))
           

#         for line in lines:
#             line_count += 1
#             textob.textLine(line)
#             if line_count % max_lines_per_page == 0:
#                 c.drawText(textob)
#                 c.showPage()
#                 textob = c.beginText()
#                 textob.setTextOrigin(inch, inch)
#                 textob.setFont("Helvetica", 14)
#     c.save()
#     buf.seek(0)
#     return FileResponse(buf, as_attachment=True, filename='orders report.pdf')

def report_generator(request, orders):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    story = []

    data = [["Order ID", "Total Quantity", "Product IDs", "Product Names", "Amount"]]

    for order in orders:
        # Retrieve order items associated with the current order
        order_items = OrderItem.objects.filter(order=order)
        total_quantity = sum(item.quantity for item in order_items)

        if order_items.exists():
            product_ids = ", ".join([str(item.product.id) for item in order_items])
            product_names = ", ".join([str(item.product.product_name) for item in order_items])
        else:
            product_ids = "N/A"
            product_names = "N/A"

        data.append([order.id, total_quantity, product_ids, product_names, order.amount])

    # Create a table with the data
    table = Table(data, colWidths=[1 * inch, 1.5 * inch, 2 * inch, 3 * inch, 1 * inch])

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(table_style)

    # Add the table to the story and build the document
    story.append(table)
    doc.build(story)

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='orders_report.pdf')

def report_pdf_order(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse('Invalid date format.')
        orders = Order.objects.filter(date__range=[from_date, to_date]).order_by('-id')
        return report_generator(request, orders)
    
    
import json