from django.db import models
from django.contrib.auth.models import AbstractUser
import os

class Clinica(models.Model):
    nombre = models.CharField("Nombre",max_length=100)

    def __str__(self):
    	return self.nombre

class CustomUser(AbstractUser):
    clinica = models.ForeignKey(Clinica, null=True, blank=True, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
    	return self.username

class Obra_Social(models.Model):
    codigo = models.IntegerField()
    nombre = models.CharField(max_length=100) 
    usa_bonos = models.BooleanField(default=False)
    usa_coseguro = models.BooleanField(default=False)
    usa_autorizacion = models.BooleanField(default=False)
    usa_planes = models.BooleanField(default=False)   
    observaciones = models.TextField(max_length=1000,blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    class Meta:
        unique_together = (("codigo", "clinica"),)
        ordering = ('nombre',)

class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    obra_social = models.ForeignKey('Obra_Social',on_delete=models.CASCADE)
    paga_coseguro = models.BooleanField('Paga coseguro',blank=True,null=True)

    VACIO = ''
    GRAVADO = 'GR'
    NO_GRAVADO = 'NG'
    EXENTO = 'EX'
    IVA = [
        (VACIO, 'Seleccione IVA'),
        (GRAVADO, 'Gravado'),
        (NO_GRAVADO, 'No gravado'),
        (EXENTO, 'Exento')
    ]
    iva = models.CharField(
        max_length=2,
        choices=IVA,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ('nombre',)

class Norma_Trabajo(models.Model):
    obra_social = models.ForeignKey('Obra_Social',on_delete=models.CASCADE)
    codigo = models.CharField(max_length=100)
    dias = models.IntegerField(blank=True, null=True)
    meses = models.IntegerField(blank=True, null=True)
    años = models.IntegerField(blank=True, null=True)
    descripcion = models.TextField('Concepto',max_length=2000)
    coseguro = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    bonos = models.IntegerField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = (("codigo", "obra_social", "clinica"),)
        ordering = ('obra_social__nombre',)

    def __str__(self):
        return self.codigo + ' - ' + self.descripcion

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
    dni = models.CharField(max_length=100,blank=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
    	return self.nombre_apellido

    class Meta:
        ordering = ('nombre_apellido',)

class PacienteObraSocial(models.Model):
    paciente = models.ForeignKey("Paciente", on_delete = models.CASCADE)
    obra_social = models.ForeignKey('Obra_Social',on_delete=models.CASCADE)
    plan = models.ForeignKey('Plan',null=True,blank=True,on_delete=models.CASCADE)
    nro_afiliado = models.CharField('Nro. Afiliado', max_length=20)

class Telefono(models.Model):
    paciente = models.ForeignKey("Paciente", on_delete = models.CASCADE)
    descripcion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100)

    def __str__(self):
    	return self.descripcion + ': ' + self.telefono

class Email(models.Model):
    paciente = models.ForeignKey("Paciente", on_delete = models.CASCADE)
    descripcion = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)

    def __str__(self):
    	return self.descripcion + ': ' + self.email 

class Ficha(models.Model):
    fecha = models.DateTimeField()
    paciente = models.ForeignKey('Paciente',on_delete=models.PROTECT)
    odontologo = models.ForeignKey('Odontologo',on_delete=models.PROTECT)
    obra_social = models.ForeignKey('Obra_Social',null=True,blank=True,on_delete=models.PROTECT)
    plan = models.ForeignKey('Plan',null=True,blank=True,on_delete=models.PROTECT)
    nro_afiliado = models.CharField(max_length=50,null=True,blank=True)
    observaciones = models.TextField(max_length=1000,blank=True)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey('Clinica',on_delete=models.PROTECT)

class Consulta(models.Model):
    fecha = models.DateTimeField(null=True,blank=True)
    nro_diente = models.IntegerField(null=True,blank=True)
    norma_trabajo = models.ForeignKey('Norma_Trabajo',null=True,blank=True,on_delete=models.PROTECT)
    detalle = models.TextField(max_length=1000,null=True,blank=True)
    ficha = models.ForeignKey('Ficha', on_delete=models.CASCADE)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

class Imagen(models.Model):
    ruta = models.TextField()
    imagen = models.FileField(blank=True, null=True, upload_to='imagenes_fichas/')
    descripcion = models.CharField(blank=True, null=True,max_length=500)
    ficha = models.ForeignKey('Ficha', on_delete=models.CASCADE)
    creada = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.imagen.name)
    