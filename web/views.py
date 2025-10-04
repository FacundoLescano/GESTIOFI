from .models import Sale, Product, SaleProduct
from authe.models import Company
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
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
        # Permitir seleccionar cualquier empresa disponible
        # form.fields['enterprise'].queryset = form.fields['enterprise'].queryset.filter(id=self.request.user.id)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = SaleProductFormSet(self.request.POST)
        else:
            # Crear formset vacío para que el usuario pueda agregar productos dinámicamente
            context['formset'] = SaleProductFormSet(queryset=SaleProduct.objects.none())
        
        # Agregar productos disponibles para el template
        context['products'] = Product.objects.filter(empresa=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
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
            # Asignar el total calculado
            self.object.total = total_venta
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
        # Obtener el ID de la venta desde el formulario
        sale_id = request.POST.get('sale_id')
        if not sale_id:
            # Si no se especifica una venta, usar la primera venta del usuario
            sale = Sale.objects.filter(enterprise=self.request.user).first()
        else:
            sale = Sale.objects.filter(id_venta=sale_id, enterprise=self.request.user).first()
        
        if not sale:
            return HttpResponse("Venta no encontrada", status=404)
        
        # Crear respuesta HTTP para el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_venta_{self.request.user}_{sale_id}.pdf"'
        
        # Crear el documento PDF
        doc = SimpleDocTemplate(response, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Obtener estilos
        styles = getSampleStyleSheet()
        
        # Crear estilos personalizados
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
        
        # Obtener datos de la empresa
        company = sale.enterprise
        
        # Construir el contenido del PDF
        story = []
        
        # Título del ticket
        story.append(Paragraph("TICKET DE COMPRA", title_style))
        story.append(Spacer(1, 20))
        
        # Información de la empresa
        story.append(Paragraph(f"<b>{company.username}</b>", company_style))
        story.append(Paragraph(f"Email: {company.email}", info_style))
        story.append(Spacer(1, 20))
        
        # Línea separadora
        story.append(Paragraph("_" * 50, info_style))
        story.append(Spacer(1, 20))
        
        # Información de la venta
        story.append(Paragraph(f"<b>Número de Ticket:</b> {sale.id_venta}", info_style))
        story.append(Paragraph(f"<b>Cliente:</b> {sale.name}", info_style))
        story.append(Paragraph(f"<b>Fecha:</b> {sale.date.strftime('%d/%m/%Y %H:%M')}", info_style))
        story.append(Spacer(1, 20))
        
        # Tabla de productos
        story.append(Paragraph("<b>DETALLE DE PRODUCTOS</b>", info_style))
        story.append(Spacer(1, 10))
        
        # Crear datos para la tabla
        table_data = [['Producto', 'Categoría', 'Precio Unit.', 'Cantidad', 'Subtotal']]
        
        total_venta = 0
        for sale_product in sale.saleproduct_set.all():
            product = sale_product.product
            quantity = sale_product.quantity
            
            # Verificar que el producto existe y tiene precio
            if product and product.price is not None:
                subtotal = float(product.price) * quantity
                total_venta += subtotal
                
                table_data.append([
                    product.name,
                    product.category,
                    f"${product.price}",
                    str(quantity),
                    f"${subtotal:.2f}"
                ])
        
        # Crear la tabla
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
        
        # Total
        story.append(Paragraph("_" * 50, info_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>TOTAL: ${total_venta:.2f}</b>", 
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
        
        # Construir el PDF
        doc.build(story)
        
        return response


class DeleteSaleView(DeleteView):
    model = Sale
    success_url = reverse_lazy("home")


class TotalSaleDayView(LoginRequiredMixin, TemplateView):
    template_name = "web/DiaryCount.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sales = Sale.objects.filter(enterprise=self.request.user)
        total_sales = sum(sale.total for sale in sales)
        context['total_sales'] = total_sales
        context['ventas'] = Sale.objects.filter(enterprise=self.request.user)
        return context


class EstadisticsView(LoginRequiredMixin, TemplateView):
    template_name = "web/Estadistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sales = Sale.objects.filter(enterprise=self.request.user)
        products = Product.objects.filter(empresa=self.request.user)
        
        # Datos para estadísticas generales
        total_sales = sum(sale.total for sale in sales)
        total_orders = sales.count()
        avg_order = total_sales / total_orders if total_orders > 0 else 0
        
        # Datos para gráfico de ventas por mes
        from datetime import datetime
        from collections import defaultdict
        
        sales_by_month = defaultdict(float)
        for sale in sales:
            month_key = sale.date.strftime('%Y-%m')
            sales_by_month[month_key] += float(sale.total)
        
        # Generar datos para los últimos 12 meses
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
        
        # Datos para productos más vendidos
        from collections import Counter
        
        product_sales = Counter()
        for sale in sales:
            for sale_product in sale.saleproduct_set.all():
                product_sales[sale_product.product.name] += sale_product.quantity
        
        # Top 5 productos más vendidos
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