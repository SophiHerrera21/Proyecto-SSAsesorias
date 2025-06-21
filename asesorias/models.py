from django.db import models
from django.utils.translation import gettext_lazy as _

class Componente(models.Model):
    id_componente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=45, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'componente'
        verbose_name = _('componente')
        verbose_name_plural = _('componentes')

    def __str__(self):
        return self.nombre


class Asesoria(models.Model):
    id_asesoria = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=45, null=True, blank=True)
    fecha = models.DateField()
    hora = models.TimeField()
    id_grupo = models.ForeignKey('grupos.Grupo', on_delete=models.CASCADE, related_name='asesorias')
    id_componente = models.ForeignKey(Componente, on_delete=models.CASCADE, related_name='asesorias')
    link_reunion = models.CharField(max_length=255, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[('programada', 'Programada'), ('en_curso', 'En Curso'), ('finalizada', 'Finalizada'), ('cancelada', 'Cancelada')], default='programada')
    observaciones = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'asesoria'
        verbose_name = _('asesoria')
        verbose_name_plural = _('asesorias')

    def __str__(self):
        return f"Asesoría: {self.descripcion} - {self.fecha} {self.hora}"
