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
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
    	return self.nombre_apellido

class Paciente(models.Model):
    nombre_apellido = models.CharField("Nombre y apellido",max_length=100)
    odontologos = models.ManyToManyField(Odontologo,blank=True)
    domicilio = models.CharField(max_length=100,blank=True)
    telefono = models.CharField(max_length=100,blank=True)
    dni = models.CharField(max_length=100,blank=True)
    obras_sociales = models.ManyToManyField('Obra_Social',blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
    	return self.nombre_apellido

    class Meta:
        ordering = ('nombre_apellido',)

class Obra_Social(models.Model):
    codigo = models.IntegerField(unique=True,error_messages={'unique':"Ya existe una obra social con el codigo ingresado."})
    nombre = models.CharField(max_length=100)    
    observaciones = models.TextField(max_length=1000,blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ('nombre',)

class Norma_Trabajo(models.Model):
    codigo = models.CharField(max_length=100)
    obra_social = models.ForeignKey('Obra_Social',on_delete=models.CASCADE)
    vencimiento = models.DateField('Vencimiento')
    descripcion = models.TextField('Concepto',max_length=2000)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
        return self.codigo


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