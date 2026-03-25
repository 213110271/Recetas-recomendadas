from django.contrib import admin
from .models import Producto, Contacto, Receta, RecetaGuardada

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre','categoria','precio')

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre','email','telefono','creado')
    readonly_fields = ('creado',)

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('nombre','tipo','tiempo','dificultad')
    list_filter = ('tipo','dificultad')
    search_fields = ('nombre','descripcion')

@admin.register(RecetaGuardada)
class RecetaGuardadaAdmin(admin.ModelAdmin):
    list_display = ('nombre','usuario','origen','favorita','fecha_guardada')
    list_filter = ('origen','favorita','fecha_guardada')
    search_fields = ('nombre','usuario__username')
    readonly_fields = ('fecha_guardada','actualizada')
    fieldsets = (
        ('Información de la Receta', {
            'fields': ('nombre','descripcion','tipo','tiempo','dificultad')
        }),
        ('Detalles', {
            'fields': ('usuario','origen','favorita','notas')
        }),
        ('Ingredientes', {
            'fields': ('ingredientes','pasos')
        }),
        ('Metadata', {
            'fields': ('fecha_guardada','actualizada'),
            'classes': ('collapse',)
        }),
    )
