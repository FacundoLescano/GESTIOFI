from .models import Sale, Product, SaleProduct
from authe.models import Company
from django.views.generic import ListView, CreateView, TemplateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from authe.form import SaleForm, ProductForm
from django.urls import reverse_lazy
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import HttpResponse
from datetime import datetime
from authe.form import SaleProductFormSet

class PageWelcome(TemplateView):
    template_name = "web/PageWelcome.html"
    

class getproductsView(LoginRequiredMixin, TemplateView):
    template_name = "web/getProducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Products'] = Product.objects.filter(empresa=self.request.user)
        context["Sales"] = Sale.objects.filter(enterprise=self.request.user)
        return context
    
    
class CreateSaleView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "web/CreateSaleView2.html"
    success_url = reverse_lazy("home")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['enterprise'].queryset = form.fields['enterprise'].queryset.filter(id=self.request.user.id)
        #form.fields[''].queryset = form.fields['enterprise'].queryset.filter(id=self.request.user.id)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = SaleProductFormSet(self.request.POST)
        else:
            context['formset'] = SaleProductFormSet(queryset=SaleProduct.objects.none())

        #user_products = Product.objects.filter(empresa=self.request.user)

        #for form in context['formset']:
        #    form.fields['product'].queryset = user_products

        context['products'] = Product.objects.filter(empresa=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        porcentage_discount = form.cleaned_data.get('porcentage_discount')
        if formset.is_valid():
            has_products = False
            for sale_product in formset:
                if sale_product.cleaned_data:
                    product = sale_product.cleaned_data.get('product')
                    quantity = sale_product.cleaned_data.get('quantity')
                    if product is not None and quantity is not None and quantity > 0:
                        has_products = True
                        break
            if not has_products:
                form.add_error(None, "Debe seleccionar al menos un producto para la venta.")
                return self.form_invalid(form)
            self.object = form.save(commit=False)
            total_venta = 0
            for sale_product in formset:
                if sale_product.cleaned_data:
                    product = sale_product.cleaned_data.get('product')
                    quantity = sale_product.cleaned_data.get('quantity')
                    if product is not None and quantity is not None and quantity > 0:
                        # Validar stock disponible
                        if product.stock < quantity:
                            form.add_error(None, f"No hay suficiente stock para {product.name}. Stock disponible: {product.stock}, solicitado: {quantity}")
                            return self.form_invalid(form)
                        subtotal = float(product.price) * int(quantity)
                        total_venta += subtotal
                        product.stock -= quantity
                        product.save()
            self.object.total = total_venta - (total_venta * porcentage_discount / 100)
            self.object.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class CreateProductView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "web/CreateProductView.html"
    success_url = reverse_lazy("home")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['empresa'].queryset = form.fields['empresa'].queryset.filter(id=self.request.user.id)
        return form


class DeleteProductView(DeleteView):
    model = Product
    success_url = reverse_lazy("home")


class MyaccountView(LoginRequiredMixin, TemplateView):
    template_name = "web/Myaccount.html"
    context_object_name = "user"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Company.objects.filter(id=self.request.user.id)
        return context


class GeneratePDFView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        sale_id = request.POST.get('sale_id')
        if not sale_id:
            sale = Sale.objects.filter(enterprise=self.request.user).first()
        else:
            sale = Sale.objects.filter(id_venta=sale_id, enterprise=self.request.user).first()
        
        if not sale:
            return HttpResponse("Venta no encontrada", status=404)
        
        # Crear respuesta HTTP para el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_venta_{self.request.user}_{sale_id}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        company_style = ParagraphStyle(
            'CompanyStyle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            alignment=TA_LEFT,
            textColor=colors.black
        )

        company = sale.enterprise

        story = []

        story.append(Paragraph("TICKET DE COMPRA", title_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph(f"<b>{company.username}</b>", company_style))
        story.append(Paragraph(f"Email: {company.email}", info_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("_" * 50, info_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph(f"<b>Número de Ticket:</b> {sale.id_venta}", info_style))
        story.append(Paragraph(f"<b>Cliente:</b> {sale.name}", info_style))
        story.append(Paragraph(f"<b>Fecha:</b> {sale.date.strftime('%d/%m/%Y %H:%M')}", info_style))
        story.append(Paragraph(f"<b>Descuento:</b> {sale.porcentage_discount}%", info_style))
        story.append(Paragraph(f"TICKET NO VALIDO COMO FACTURA.", info_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("<b>DETALLE DE PRODUCTOS</b>", info_style))
        story.append(Spacer(1, 10))

        table_data = [['Producto', 'Categoría', 'Precio Unit.', 'Cant.', 'Subtotal']]

        total_sin_descuento = 0
        for sale_product in sale.saleproduct_set.all():
            product = sale_product.product
            quantity = sale_product.quantity

            if product and product.price is not None:
                subtotal = float(product.price) * quantity
                total_sin_descuento += subtotal

                table_data.append([
                    product.name,
                    product.category,
                    f"${product.price}",
                    str(quantity),
                    f"${subtotal:.2f}"
                ])

        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1*inch, 0.8*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))

        # Cálculos del total
        monto_descuento = total_sin_descuento * sale.porcentage_discount / 100
        total_final = total_sin_descuento - monto_descuento

        # Total
        story.append(Paragraph("_" * 50, info_style))
        story.append(Spacer(1, 10))

        # Mostrar subtotal
        story.append(Paragraph(f"<b>Subtotal:</b> ${total_sin_descuento:.2f}",
                              ParagraphStyle('SubtotalStyle', parent=info_style,
                                            fontSize=12, alignment=TA_RIGHT)))

        # Mostrar descuento si existe
        if sale.porcentage_discount > 0:
            story.append(Paragraph(f"<b>Descuento ({sale.porcentage_discount}%):</b> -${monto_descuento:.2f}",
                                  ParagraphStyle('DiscountStyle', parent=info_style,
                                                fontSize=12, alignment=TA_RIGHT,
                                                textColor=colors.red)))

        story.append(Spacer(1, 5))
        story.append(Paragraph("_" * 50, info_style))
        story.append(Spacer(1, 5))

        # Total final
        story.append(Paragraph(f"<b>TOTAL: ${total_final:.2f}</b>",
                              ParagraphStyle('TotalStyle', parent=info_style,
                                            fontSize=14, alignment=TA_RIGHT)))
        story.append(Spacer(1, 30))
        
        # Pie del ticket
        story.append(Paragraph("_" * 50, info_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("¡Gracias por su compra!", 
                              ParagraphStyle('ThanksStyle', parent=info_style, 
                                            alignment=TA_CENTER, fontSize=12)))
        story.append(Paragraph(f"Ticket generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                              ParagraphStyle('DateStyle', parent=info_style, 
                                            alignment=TA_CENTER, fontSize=10)))

        doc.build(story)
        
        return response


class DeleteSaleView(DeleteView):
    model = Sale
    success_url = reverse_lazy("home")


class TotalSaleDayView(LoginRequiredMixin, TemplateView):
    template_name = "web/DiaryCount.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import date
        today = date.today()

        sales = Sale.objects.filter(enterprise=self.request.user, date__date=today)
        total_sales = sum(sale.total for sale in sales)

        context['total_sales'] = total_sales
        context['ventas'] = sales
        context['today'] = today
        return context


class EstadisticsView(LoginRequiredMixin, TemplateView):
    template_name = "web/Estadistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sales = Sale.objects.filter(enterprise=self.request.user)
        products = Product.objects.filter(empresa=self.request.user)

        total_sales = sum(sale.total for sale in sales)
        total_orders = sales.count()
        avg_order = total_sales / total_orders if total_orders > 0 else 0

        from datetime import datetime
        from collections import defaultdict
        
        sales_by_month = defaultdict(float)
        for sale in sales:
            month_key = sale.date.strftime('%Y-%m')
            sales_by_month[month_key] += float(sale.total)

        import calendar
        from datetime import date, timedelta
        
        months_data = []
        sales_data = []
        
        for i in range(11, -1, -1):
            target_date = date.today() - timedelta(days=30*i)
            month_key = target_date.strftime('%Y-%m')
            month_name = calendar.month_name[target_date.month]
            months_data.append(month_name)
            sales_data.append(float(sales_by_month.get(month_key, 0)))

        from collections import Counter
        
        product_sales = Counter()
        for sale in sales:
            for sale_product in sale.saleproduct_set.all():
                product_sales[sale_product.product.name] += sale_product.quantity

        top_products = product_sales.most_common(5)
        product_names = [item[0] for item in top_products]
        product_quantities = [item[1] for item in top_products]
        
        context.update({
            'sales': sales,
            'products': products,
            'total_sales': total_sales,
            'total_orders': total_orders,
            'avg_order': avg_order,
            'months_data': months_data,
            'sales_data': sales_data,
            'product_names': product_names,
            'product_quantities': product_quantities,
        })
        return context

class GenerateDailyReportView(LoginRequiredMixin, TemplateView):
    """Vista para generar el PDF del cierre diario de ventas"""

    def post(self, request, *args, **kwargs):
        from datetime import date

        today = date.today()

        today_sales = Sale.objects.filter(enterprise=self.request.user, date__date=today)

        total_day = sum(sale.total for sale in today_sales)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cierre_diario_{today.strftime("%d_%m_%Y")}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#667eea'),
            fontName='Helvetica-Bold'
        )

        company_style = ParagraphStyle(
            'CompanyStyle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        )

        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            alignment=TA_LEFT,
            textColor=colors.black
        )

        total_style = ParagraphStyle(
            'TotalStyle',
            parent=styles['Heading1'],
            fontSize=36,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#28a745'),
            fontName='Helvetica-Bold'
        )

        company = self.request.user

        story = []

        story.append(Paragraph("CIERRE DEL DÍA", title_style))
        story.append(Spacer(1, 20))

        story.append(Paragraph(f"<b>{company.username}</b>", company_style))
        story.append(Paragraph(f"Email: {company.email}", info_style))
        story.append(Spacer(1, 20))

        story.append(Paragraph("=" * 80, info_style))
        story.append(Spacer(1, 20))

        story.append(Paragraph(f"<b>Fecha:</b> {today.strftime('%d/%m/%Y')}",
                              ParagraphStyle('DateStyle', parent=info_style, fontSize=14)))
        story.append(Paragraph(f"<b>Número de ventas:</b> {today_sales.count()}",
                              ParagraphStyle('CountStyle', parent=info_style, fontSize=14)))
        story.append(Spacer(1, 30))

        story.append(Paragraph("TOTAL DEL DÍA",
                              ParagraphStyle('TotalLabel', parent=info_style,
                                           fontSize=16, alignment=TA_CENTER,
                                           textColor=colors.HexColor('#667eea'))))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"${total_day:.2f}", total_style))
        story.append(Spacer(1, 30))

        if today_sales.exists():
            story.append(Paragraph("=" * 80, info_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph("<b>DETALLE DE VENTAS DEL DÍA</b>",
                                  ParagraphStyle('DetailTitle', parent=info_style,
                                               fontSize=14, alignment=TA_CENTER)))
            story.append(Spacer(1, 15))

            table_data = [['ID', 'Cliente', 'Hora', 'Total']]

            for sale in today_sales:
                table_data.append([
                    str(sale.id_venta),
                    sale.name,
                    sale.date.strftime('%H:%M'),
                    f"${sale.total:.2f}"
                ])

            table = Table(table_data, colWidths=[1*inch, 3*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))

            story.append(table)
            story.append(Spacer(1, 30))
        else:
            story.append(Paragraph("=" * 80, info_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph("No hay ventas registradas para el día de hoy",
                                  ParagraphStyle('NoSales', parent=info_style,
                                               fontSize=14, alignment=TA_CENTER,
                                               textColor=colors.HexColor('#6c757d'))))
            story.append(Spacer(1, 30))

        story.append(Paragraph("=" * 80, info_style))
        story.append(Spacer(1, 20))

        story.append(Paragraph(f"Reporte generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                              ParagraphStyle('FooterStyle', parent=info_style,
                                           alignment=TA_CENTER, fontSize=10,
                                           textColor=colors.HexColor('#6c757d'))))
        story.append(Spacer(1, 10))
        story.append(Paragraph("GESTIOFI - Sistema de Gestión de Ventas",
                              ParagraphStyle('CompanyFooter', parent=info_style,
                                           alignment=TA_CENTER, fontSize=10,
                                           textColor=colors.HexColor('#6c757d'))))

        doc.build(story)

        return response


class Update_products(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['price', 'stock']
    template_name = 'web/UpdateProducts.html'
    success_url = reverse_lazy("home")