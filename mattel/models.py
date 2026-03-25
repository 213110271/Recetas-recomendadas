from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    CATEGORIAS = [
        ('vegetales', 'Vegetales'),
        ('frutas', 'Frutas'),
        ('carnes', 'Carnes'),
        ('legumbres', 'Legumbres'),
        ('cereales', 'Cereales'),
        ('condimentos', 'Condimentos'),
        ('especias', 'Especias'),
    ]

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre


class Contacto(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    mensaje = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.email}"


class Receta(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()

    # 🔥 NUEVOS CAMPOS PROFESIONALES 🔥
    tiempo = models.CharField(max_length=50, default="30 minutos")  
    dificultad = models.CharField(
        max_length=20,
        choices=[
            ("Fácil", "Fácil"),
            ("Media", "Media"),
            ("Difícil", "Difícil"),
        ],
        default="Fácil"
    )
    pasos = models.TextField(
        help_text="Escribe cada paso en una nueva línea.",
        default="1. Preparar ingredientes\n2. Mezclar\n3. Cocinar"
    )

    ingredientes = models.ManyToManyField(Producto, related_name='recetas')
    imagen = models.ImageField(upload_to='recetas/', blank=True, null=True)

    # 🔥 NUEVO CAMPO PARA CLASIFICAR RECETAS 🔥
    tipo = models.CharField(
        max_length=50,
        choices=[
            ("ensalada", "Ensalada"),
            ("guisado", "Guisado"),
            ("sopa", "Sopa"),
            ("postre", "Postre"),
            ("bebida", "Bebida"),
            ("sandwich", "Sandwich"),
            ("pasta", "Pasta"),
            ("carne", "Carne"),
            ("mariscos", "Mariscos"),
            ("vegana", "Vegana"),
            ("pizza", "Pizza"),
            ("tacos", "Tacos"),
            ("wrap", "Wrap"),
            ("arroz", "Arroz"),
            ("cereal", "Cereal"),
            ("pan", "Pan"),
            ("dulce", "Dulce"),
            ("salado", "Salado"),
            ("light", "Light"),
            ("rápida", "Rápida"),
        ],
        default="ensalada"
    )

    def pasos_lista(self):
        return self.pasos.split("\n")

    def __str__(self):
        return self.nombre


class RecetaGuardada(models.Model):
    """
    Modelo para guardar recetas generadas por IA o modo offline
    en el perfil de cada usuario.
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recetas_guardadas')
    
    # Datos de la receta
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    pasos = models.TextField()
    tiempo = models.CharField(max_length=50, default="30 minutos")
    dificultad = models.CharField(max_length=20, default="Fácil")
    tipo = models.CharField(max_length=50, default="ensalada")
    
    # Ingredientes como JSON string
    ingredientes = models.TextField(help_text="JSON con ingredientes utilizados")
    
    # Metadata
    origen = models.CharField(
        max_length=10,
        choices=[
            ('ia', 'IA (Gemini)'),
            ('offline', 'Generada Offline'),
            ('bd', 'De Base de Datos'),
        ],
        default='offline'
    )
    fecha_guardada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    
    # Opcionales
    notas = models.TextField(blank=True, help_text="Notas personales sobre la receta")
    favorita = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_guardada']
        verbose_name_plural = "Recetas Guardadas"
    
    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"


class LoginAudit(models.Model):
    """🔐 Registro de auditoría de intentos de login"""
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField(default=False)
    reason = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Auditoría de Login"
        verbose_name_plural = "Auditorías de Login"
    
    def __str__(self):
        status = "✅ SUCCESS" if self.success else "❌ FAILED"
        return f"{status} - {self.username} - {self.ip_address} - {self.timestamp}"