# GESTIOFI - Sistema de Gestión de Ventas

Sistema integral de gestión de ventas desarrollado con Django, diseñado para pequeñas y medianas empresas que necesitan llevar un control detallado de sus productos, ventas y reportes financieros.

## 📋 Características Principales

- **Gestión de Productos**: Crear, actualizar y eliminar productos con control de stock automático
- **Registro de Ventas**: Sistema completo de ventas con soporte para múltiples productos por transacción
- **Generación de Tickets PDF**: Tickets de compra profesionales con información detallada
- **Sistema de Descuentos**: Aplicación de descuentos porcentuales por venta
- **Reportes y Estadísticas**:
  - Cierre diario de caja con reporte PDF
  - Estadísticas de ventas mensuales
  - Productos más vendidos
  - Análisis de ventas promedio
- **Autenticación Multi-empresa**: Sistema de usuarios basado en empresas
- **Control de Inventario**: Actualización automática de stock al realizar ventas

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.2.5
- **Base de Datos**: SQLite (desarrollo) / MySQL (producción)
- **Generación de PDFs**: ReportLab 4.4.3
- **Manejo de Imágenes**: Pillow 11.3.0
- **Variables de Entorno**: python-dotenv 1.1.1
- **API REST**: Django REST Framework 3.16.1

## 📦 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- MySQL (opcional, para producción)

## 🚀 Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/FacundoLescano/GESTIOFI.git
cd GESTIOFI
```

2. **Crear un entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno** (opcional para MySQL)

Crear un archivo `.env` en la raíz del proyecto:
```env
NAME=nombre_base_datos
USER=usuario_mysql
PASSWORD=contraseña_mysql
HOST=localhost
PORT=3306
```

5. **Realizar migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Ejecutar el servidor**
```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/`

## 📁 Estructura del Proyecto

```
GESTIOFI/
│
├── authe/                      # App de autenticación
│   ├── models.py              # Modelos Company y Branch
│   ├── views.py               # Vistas de login y registro
│   ├── forms.py               # Formularios de autenticación
│   └── templates/             # Templates de autenticación
│
├── web/                       # App principal de ventas
│   ├── models.py              # Modelos Product, Sale, SaleProduct
│   ├── views.py               # Vistas de gestión de ventas
│   ├── urls.py                # URLs de la aplicación
│   └── templates/             # Templates de la aplicación
│
├── sales_software/            # Configuración del proyecto
│   ├── settings.py            # Configuración de Django
│   ├── urls.py                # URLs principales
│   └── wsgi.py                # Configuración WSGI
│
├── requirements.txt           # Dependencias del proyecto
├── manage.py                  # Script de gestión de Django
└── README.md                  # Este archivo
```

## 💻 Uso

### Panel de Administración
Accede al panel de administración en `http://127.0.0.1:8000/admin/` con las credenciales del superusuario.

### Funcionalidades Principales

#### Gestión de Productos
- **Crear Producto**: `/create_product/`
- **Actualizar Producto**: `/update_products/<id>/`
- **Eliminar Producto**: `/delete_product/<id>/`
- **Listar Productos**: `/home/`

#### Gestión de Ventas
- **Crear Venta**: `/create_sale/`
  - Seleccionar múltiples productos
  - Aplicar descuentos porcentuales
  - Validación automática de stock
- **Eliminar Venta**: `/delete_sale/<id>/`
- **Generar Ticket PDF**: `/generate_report/`

#### Reportes
- **Cierre Diario**: `/total_sales_day/` - Ver ventas del día actual
- **Reporte Diario PDF**: `/generate_daily_report/` - Generar PDF de cierre diario
- **Estadísticas**: `/estadistics/` - Visualizar gráficos y análisis de ventas

#### Cuenta
- **Mi Cuenta**: `/my_account/` - Ver información de la empresa

## 🔐 Seguridad

- Sistema de autenticación de Django con modelo personalizado
- Protección CSRF en todos los formularios
- Validación de permisos por usuario (LoginRequiredMixin)
- Validación de datos en formularios

## 📊 Modelos de Datos

### Company (authe/models.py)
- username: Nombre de la empresa
- email: Correo electrónico
- password: Contraseña encriptada
- cuit: Identificación fiscal
- city: Ciudad
- state: Estado activo/inactivo

### Product (web/models.py)
- name: Nombre del producto
- category: Categoría
- description: Descripción
- price: Precio unitario
- stock: Cantidad disponible
- empresa: Relación con Company

### Sale (web/models.py)
- name: Cliente
- date: Fecha y hora de la venta
- total: Monto total
- porcentage_discount: Descuento aplicado (%)
- enterprise: Relación con Company

### SaleProduct (web/models.py)
- sale: Relación con Sale
- product: Relación con Product
- quantity: Cantidad vendida

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo licencia libre para uso educativo y comercial.

## 👥 Autor

**Facundo Lescano**
- GitHub: [@FacundoLescano](https://github.com/FacundoLescano)

## 📧 Contacto

Si tienes alguna pregunta o sugerencia, no dudes en abrir un issue en el repositorio.

## 🔄 Próximas Mejoras

- [ ] Implementar sistema de roles y permisos
- [ ] Agregar dashboard con gráficos interactivos
- [ ] Implementar sistema de notificaciones
- [ ] Agregar exportación de reportes a Excel
- [ ] Implementar sistema de alertas de stock bajo
- [ ] Agregar soporte para múltiples sucursales
- [ ] Implementar API REST completa
- [ ] Agregar sistema de respaldo automático

---

⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub!
