from django.db import models
from django.utils.translation import gettext_lazy as _

class Grupo(models.Model):
    id_grupo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    c_aprendices = models.IntegerField(default=0)
    capacidad_maxima = models.IntegerField(default=15)
    id_componente = models.ForeignKey('asesorias.Componente', on_delete=models.CASCADE, related_name='grupos')
    id_asesor = models.ForeignKey('users.Asesor', on_delete=models.SET_NULL, null=True, related_name='grupos')
    estado = models.CharField(max_length=20, choices=[('activo', 'Activo'), ('inactivo', 'Inactivo'), ('completo', 'Completo')], default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'grupo'
        verbose_name = _('grupo')
        verbose_name_plural = _('grupos')

    def __str__(self):
        return f"Grupo: {self.nombre} - {self.id_componente.nombre}"


class AprendizGrupo(models.Model):
    id_aprendiz_grupo = models.AutoField(primary_key=True)
    id_aprendiz = models.ForeignKey('users.Aprendiz', on_delete=models.CASCADE, related_name='grupos')
    id_grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name='aprendices')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[('asignado', 'Asignado'), ('activo', 'Activo'), ('retirado', 'Retirado')], default='asignado')

    class Meta:
        db_table = 'aprendiz_grupo'
        verbose_name = _('aprendiz grupo')
        verbose_name_plural = _('aprendices grupos')
        unique_together = ('id_aprendiz', 'id_grupo')

    def __str__(self):
        return f"Aprendiz: {self.id_aprendiz.id_usuario.username} - Grupo: {self.id_grupo.nombre}"


class AsesorComponente(models.Model):
    id_asesor_componente = models.AutoField(primary_key=True)
    id_asesor = models.ForeignKey('users.Asesor', on_delete=models.CASCADE, related_name='componentes')
    id_componente = models.ForeignKey('asesorias.Componente', on_delete=models.CASCADE, related_name='asesores')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[('asignado', 'Asignado'), ('activo', 'Activo'), ('inactivo', 'Inactivo')], default='asignado')

    class Meta:
        db_table = 'asesor_componente'
        verbose_name = _('asesor componente')
        verbose_name_plural = _('asesores componentes')
        unique_together = ('id_asesor', 'id_componente')

    def __str__(self):
        return f"Asesor: {self.id_asesor.id_usuario.username} - Componente: {self.id_componente.nombre}"
