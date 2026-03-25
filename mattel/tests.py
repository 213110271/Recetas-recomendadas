from django.test import TestCase, Client
from django.urls import reverse
from .models import Producto, Receta

class MattelViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear productos de prueba
        self.producto1 = Producto.objects.create(
            nombre="Tomate",
            precio=10.00,
            categoria="vegetales",
            descripcion="Tomate fresco"
        )
        self.producto2 = Producto.objects.create(
            nombre="Lechuga",
            precio=15.00,
            categoria="vegetales",
            descripcion="Lechuga fresca"
        )
        
        # Crear receta de prueba
        self.receta = Receta.objects.create(
            nombre="Ensalada Mixta",
            descripcion="Una ensalada saludable",
            tiempo="10 minutos",
            dificultad="Fácil",
            pasos="1. Lavar\n2. Cortar\n3. Servir",
            tipo="ensalada"
        )
        self.receta.ingredientes.add(self.producto1, self.producto2)

    def test_inicio_view(self):
        """Prueba que la página de inicio carga correctamente"""
        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mattel/inicio.html')

    def test_productos_view(self):
        """Prueba que la página de productos carga correctamente"""
        response = self.client.get(reverse('productos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mattel/productos.html')
        # La vista productos muestra categorías, no productos individuales
        self.assertContains(response, "Vegetales")

    def test_catalogo_categoria_view(self):
        """Prueba el filtrado por categoría"""
        response = self.client.get(reverse('catalogo_categoria', args=['vegetales']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tomate")

    def test_seleccionar_ingredientes(self):
        """Prueba la selección de ingredientes"""
        # Primero seleccionamos un ingrediente (simulando POST)
        # Enviamos HTTP_REFERER para evitar error en redirección
        response = self.client.post(
            reverse('seleccionar_ingredientes'), 
            {'ingredientes': ['Tomate']},
            HTTP_REFERER=reverse('productos')
        )
        # Debería redirigir
        self.assertEqual(response.status_code, 302)
        
        # Verificar que está en la sesión
        session = self.client.session
        self.assertIn('ingredientes_seleccionados', session)
        self.assertIn('Tomate', session['ingredientes_seleccionados'])

    def test_ver_recetas_con_ingredientes(self):
        """Prueba la vista de recetas recomendadas con ingredientes en sesión"""
        # Configurar sesión manualmente
        session = self.client.session
        session['ingredientes_seleccionados'] = ['Tomate', 'Lechuga']
        session.save()
        
        response = self.client.get(reverse('recetas_con_ingredientes'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la receta está en el contexto (aunque el template no la muestre)
        self.assertIn(self.receta, response.context['sugeridas'])
        
        # Verificar que se muestran las recetas generadas
        self.assertContains(response, "Preparación profesional basada en")

    def test_receta_completa_view(self):
        """Prueba la vista de detalle de receta"""
        response = self.client.get(reverse('receta_completa', args=[self.receta.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ensalada Mixta")
        # La vista genera pasos dinámicos ignorando el campo pasos del modelo
        self.assertContains(response, "Lava y prepara")

    def test_contacto_view(self):
        """Prueba la página de contacto"""
        response = self.client.get(reverse('contacto'))
        self.assertEqual(response.status_code, 200)
