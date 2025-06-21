from django.db import models
from django.utils.translation import gettext_lazy as _

class Prueba(models.Model):
    id_prueba = models.AutoField(primary_key=True)
    tema = models.CharField(max_length=45)
    fecha = models.DateField()
    hora = models.TimeField()
    id_asesoria = models.ForeignKey('asesorias.Asesoria', on_delete=models.CASCADE, related_name='pruebas')
    id_grupo = models.ForeignKey('grupos.Grupo', on_delete=models.CASCADE, related_name='pruebas')
    descripcion = models.TextField(null=True, blank=True)
    archivo_adjunto = models.FileField(upload_to='pruebas/', null=True, blank=True)
    fecha_limite = models.DateField()
    estado = models.CharField(max_length=20, choices=[('creada', 'Creada'), ('publicada', 'Publicada'), ('vencida', 'Vencida'), ('calificada', 'Calificada')], default='creada')
    instrucciones = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'prueba'
        verbose_name = _('prueba')
        verbose_name_plural = _('pruebas')

    def __str__(self):
        return f"Prueba: {self.tema} - {self.fecha}"


class EntregaPrueba(models.Model):
    id_entrega = models.AutoField(primary_key=True)
    id_prueba = models.ForeignKey(Prueba, on_delete=models.CASCADE, related_name='entregas')
    id_aprendiz = models.ForeignKey('users.Aprendiz', on_delete=models.CASCADE, related_name='entregas')
    archivo_entrega = models.FileField(upload_to='entregas/', null=True, blank=True)
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    comentarios = models.TextField(null=True, blank=True)
    calificacion = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[('entregada', 'Entregada'), ('revisada', 'Revisada'), ('calificada', 'Calificada'), ('tardía', 'Tardía')], default='entregada')

    class Meta:
        db_table = 'entrega_prueba'
        verbose_name = _('entrega prueba')
        verbose_name_plural = _('entregas pruebas')
        unique_together = ('id_prueba', 'id_aprendiz')

    def __str__(self):
        return f"Entrega: {self.id_aprendiz.id_usuario.username} - Prueba: {self.id_prueba.tema}"
