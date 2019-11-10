from django.db import models
from django.contrib.auth.models import AbstractUser

class Clinica(models.Model):
    nombre = models.CharField("Nombre",max_length=100)

    def __str__(self):
    	return self.nombre

class CustomUser(AbstractUser):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
    	return self.username

class Odontologo(models.Model):
    nombre_apellido = models.CharField("Nombre y apellido",max_length=100)
    domicilio = models.CharField(max_length=100,blank=True)
    telefono = models.CharField(max_length=100,blank=True)
    dni = models.CharField(max_length=100,blank=True)
    matricula = models.CharField(max_length=100,blank=True)
    obras_sociales = models.ManyToManyField('Obra_Social',blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
    	return self.nombre_apellido

class Paciente(models.Model):
    nombre_apellido = models.CharField("Nombre y apellido",max_length=100)
    odontologos = models.ManyToManyField(Odontologo,blank=True)
    domicilio = models.CharField(max_length=100,blank=True)
    mail = models.EmailField(blank=True)
    dni = models.CharField(max_length=100,blank=True)
    obras_sociales = models.ManyToManyField('Obra_Social',blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField(blank=True, null=True)

    def __str__(self):
    	return self.nombre_apellido

    class Meta:
        ordering = ('nombre_apellido',)

class Telefono(models.Model):
    paciente = models.ForeignKey("Paciente", on_delete = models.CASCADE)
    descripcion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100)

class Obra_Social(models.Model):
    codigo = models.IntegerField()
    nombre = models.CharField(max_length=100)    
    observaciones = models.TextField(max_length=1000,blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    class Meta:
        unique_together = (("codigo", "clinica"),)
        ordering = ('nombre',)

class Norma_Trabajo(models.Model):
    codigo = models.CharField(max_length=100)
    obra_social = models.ForeignKey('Obra_Social',on_delete=models.CASCADE)
    dias = models.IntegerField()
    meses = models.IntegerField()
    años = models.IntegerField()
    descripcion = models.TextField('Concepto',max_length=2000)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("codigo", "obra_social", "clinica"),)
        ordering = ('obra_social__nombre',)

    def __str__(self):
        return self.codigo + ' - ' + self.descripcion


class Ficha(models.Model):
    fecha = models.DateTimeField()
    paciente = models.ForeignKey('Paciente',on_delete=models.PROTECT)
    odontologo = models.ForeignKey('Odontologo',on_delete=models.PROTECT)
    obra_social = models.ForeignKey('Obra_Social',null=True,blank=True,on_delete=models.PROTECT)
    norma_trabajo = models.ForeignKey('Norma_Trabajo',null=True,blank=True,on_delete=models.PROTECT)
    detalle = models.TextField(max_length=1000,blank=True)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey('Clinica',on_delete=models.PROTECT)