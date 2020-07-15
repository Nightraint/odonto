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
    codigo = models.IntegerField(blank=True,null=True)
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

    def model_name(self):
        return "Obra social"
    
    def model_name_lower(self):
        return "obra social"

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
    
    def model_name(self):
        return "Norma de trabajo"
    
    def model_name_lower(self):
        return "norma de trabajo"

class Odontologo(models.Model):
    nombre_apellido = models.CharField("Nombre y apellido",max_length=100)
    domicilio = models.CharField(max_length=100,blank=True,null=True)
    telefono = models.CharField(max_length=100,blank=True,null=True)
    dni = models.CharField(max_length=100,blank=True,null=True)
    matricula = models.CharField(max_length=100,blank=True,null=True)
    obras_sociales = models.ManyToManyField('Obra_Social',blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
    	return self.nombre_apellido

    def model_name(self):
        return "Odontólogo"
    
    def model_name_lower(self):
        return "odontólogo"

class Paciente(models.Model):
    nombre_apellido = models.CharField("Nombre y apellido",max_length=100)
    odontologos = models.ManyToManyField(Odontologo,blank=True)
    domicilio = models.CharField(max_length=100,blank=True, null=True)
    whatsapp = models.CharField(max_length=20,blank=True, null=True, help_text='Con código de area sin el cero. Ejemplo: 3492591438')
    dni = models.CharField(max_length=100,blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    def __str__(self):
    	return self.nombre_apellido

    class Meta:
        ordering = ('nombre_apellido',)

    def model_name(self):
        return "Paciente"
    
    def model_name_lower(self):
        return "paciente"

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
    d11 = models.CharField(max_length=10,null=True,blank=True)
    top11 = models.CharField(max_length=10,null=True,blank=True)
    bot11 = models.CharField(max_length=10,null=True,blank=True)
    left11 = models.CharField(max_length=10,null=True,blank=True)
    right11 = models.CharField(max_length=10,null=True,blank=True)
    d12 = models.CharField(max_length=10,null=True,blank=True)
    top12 = models.CharField(max_length=10,null=True,blank=True)
    bot12 = models.CharField(max_length=10,null=True,blank=True)
    left12 = models.CharField(max_length=10,null=True,blank=True)
    right12 = models.CharField(max_length=10,null=True,blank=True)
    d13 = models.CharField(max_length=10,null=True,blank=True)
    top13 = models.CharField(max_length=10,null=True,blank=True)
    bot13 = models.CharField(max_length=10,null=True,blank=True)
    left13 = models.CharField(max_length=10,null=True,blank=True)
    right13 = models.CharField(max_length=10,null=True,blank=True)
    d14 = models.CharField(max_length=10,null=True,blank=True)
    top14 = models.CharField(max_length=10,null=True,blank=True)
    bot14 = models.CharField(max_length=10,null=True,blank=True)
    left14 = models.CharField(max_length=10,null=True,blank=True)
    right14 = models.CharField(max_length=10,null=True,blank=True)
    d15 = models.CharField(max_length=10,null=True,blank=True)
    top15 = models.CharField(max_length=10,null=True,blank=True)
    bot15 = models.CharField(max_length=10,null=True,blank=True)
    left15 = models.CharField(max_length=10,null=True,blank=True)
    right15 = models.CharField(max_length=10,null=True,blank=True)
    d16 = models.CharField(max_length=10,null=True,blank=True)
    top16 = models.CharField(max_length=10,null=True,blank=True)
    bot16 = models.CharField(max_length=10,null=True,blank=True)
    left16 = models.CharField(max_length=10,null=True,blank=True)
    right16 = models.CharField(max_length=10,null=True,blank=True)
    d17 = models.CharField(max_length=10,null=True,blank=True)
    top17 = models.CharField(max_length=10,null=True,blank=True)
    bot17 = models.CharField(max_length=10,null=True,blank=True)
    left17 = models.CharField(max_length=10,null=True,blank=True)
    right17 = models.CharField(max_length=10,null=True,blank=True)
    d18 = models.CharField(max_length=10,null=True,blank=True)
    top18 = models.CharField(max_length=10,null=True,blank=True)
    bot18 = models.CharField(max_length=10,null=True,blank=True)
    left18 = models.CharField(max_length=10,null=True,blank=True)
    right18 = models.CharField(max_length=10,null=True,blank=True)
    d21 = models.CharField(max_length=10,null=True,blank=True)
    top21 = models.CharField(max_length=10,null=True,blank=True)
    bot21 = models.CharField(max_length=10,null=True,blank=True)
    left21 = models.CharField(max_length=10,null=True,blank=True)
    right21 = models.CharField(max_length=10,null=True,blank=True)
    d22 = models.CharField(max_length=10,null=True,blank=True)
    top22 = models.CharField(max_length=10,null=True,blank=True)
    bot22 = models.CharField(max_length=10,null=True,blank=True)
    left22 = models.CharField(max_length=10,null=True,blank=True)
    right22 = models.CharField(max_length=10,null=True,blank=True)
    d23 = models.CharField(max_length=10,null=True,blank=True)
    top23 = models.CharField(max_length=10,null=True,blank=True)
    bot23 = models.CharField(max_length=10,null=True,blank=True)
    left23 = models.CharField(max_length=10,null=True,blank=True)
    right23 = models.CharField(max_length=10,null=True,blank=True)
    d24 = models.CharField(max_length=10,null=True,blank=True)
    top24 = models.CharField(max_length=10,null=True,blank=True)
    bot24 = models.CharField(max_length=10,null=True,blank=True)
    left24 = models.CharField(max_length=10,null=True,blank=True)
    right24 = models.CharField(max_length=10,null=True,blank=True)
    d25 = models.CharField(max_length=10,null=True,blank=True)
    top25 = models.CharField(max_length=10,null=True,blank=True)
    bot25 = models.CharField(max_length=10,null=True,blank=True)
    left25 = models.CharField(max_length=10,null=True,blank=True)
    right25 = models.CharField(max_length=10,null=True,blank=True)
    d26 = models.CharField(max_length=10,null=True,blank=True)
    top26 = models.CharField(max_length=10,null=True,blank=True)
    bot26 = models.CharField(max_length=10,null=True,blank=True)
    left26 = models.CharField(max_length=10,null=True,blank=True)
    right26 = models.CharField(max_length=10,null=True,blank=True)
    d27 = models.CharField(max_length=10,null=True,blank=True)
    top27 = models.CharField(max_length=10,null=True,blank=True)
    bot27 = models.CharField(max_length=10,null=True,blank=True)
    left27 = models.CharField(max_length=10,null=True,blank=True)
    right27 = models.CharField(max_length=10,null=True,blank=True)
    d28 = models.CharField(max_length=10,null=True,blank=True)
    top28 = models.CharField(max_length=10,null=True,blank=True)
    bot28 = models.CharField(max_length=10,null=True,blank=True)
    left28 = models.CharField(max_length=10,null=True,blank=True)
    right28 = models.CharField(max_length=10,null=True,blank=True)
    d31 = models.CharField(max_length=10,null=True,blank=True)
    top31 = models.CharField(max_length=10,null=True,blank=True)
    bot31 = models.CharField(max_length=10,null=True,blank=True)
    left31 = models.CharField(max_length=10,null=True,blank=True)
    right31 = models.CharField(max_length=10,null=True,blank=True)
    d32 = models.CharField(max_length=10,null=True,blank=True)
    top32 = models.CharField(max_length=10,null=True,blank=True)
    bot32 = models.CharField(max_length=10,null=True,blank=True)
    left32 = models.CharField(max_length=10,null=True,blank=True)
    right32 = models.CharField(max_length=10,null=True,blank=True)
    d33 = models.CharField(max_length=10,null=True,blank=True)
    top33 = models.CharField(max_length=10,null=True,blank=True)
    bot33 = models.CharField(max_length=10,null=True,blank=True)
    left33 = models.CharField(max_length=10,null=True,blank=True)
    right33 = models.CharField(max_length=10,null=True,blank=True)
    d34 = models.CharField(max_length=10,null=True,blank=True)
    top34 = models.CharField(max_length=10,null=True,blank=True)
    bot34 = models.CharField(max_length=10,null=True,blank=True)
    left34 = models.CharField(max_length=10,null=True,blank=True)
    right34 = models.CharField(max_length=10,null=True,blank=True)
    d35 = models.CharField(max_length=10,null=True,blank=True)
    top35 = models.CharField(max_length=10,null=True,blank=True)
    bot35 = models.CharField(max_length=10,null=True,blank=True)
    left35 = models.CharField(max_length=10,null=True,blank=True)
    right35 = models.CharField(max_length=10,null=True,blank=True)
    d36 = models.CharField(max_length=10,null=True,blank=True)
    top36 = models.CharField(max_length=10,null=True,blank=True)
    bot36 = models.CharField(max_length=10,null=True,blank=True)
    left36 = models.CharField(max_length=10,null=True,blank=True)
    right36 = models.CharField(max_length=10,null=True,blank=True)
    d37 = models.CharField(max_length=10,null=True,blank=True)
    top37 = models.CharField(max_length=10,null=True,blank=True)
    bot37 = models.CharField(max_length=10,null=True,blank=True)
    left37 = models.CharField(max_length=10,null=True,blank=True)
    right37 = models.CharField(max_length=10,null=True,blank=True)
    d38 = models.CharField(max_length=10,null=True,blank=True)
    top38 = models.CharField(max_length=10,null=True,blank=True)
    bot38 = models.CharField(max_length=10,null=True,blank=True)
    left38 = models.CharField(max_length=10,null=True,blank=True)
    right38 = models.CharField(max_length=10,null=True,blank=True)
    d41 = models.CharField(max_length=10,null=True,blank=True)
    top41 = models.CharField(max_length=10,null=True,blank=True)
    bot41 = models.CharField(max_length=10,null=True,blank=True)
    left41 = models.CharField(max_length=10,null=True,blank=True)
    right41 = models.CharField(max_length=10,null=True,blank=True)
    d42 = models.CharField(max_length=10,null=True,blank=True)
    top42 = models.CharField(max_length=10,null=True,blank=True)
    bot42 = models.CharField(max_length=10,null=True,blank=True)
    left42 = models.CharField(max_length=10,null=True,blank=True)
    right42 = models.CharField(max_length=10,null=True,blank=True)
    d43 = models.CharField(max_length=10,null=True,blank=True)
    top43 = models.CharField(max_length=10,null=True,blank=True)
    bot43 = models.CharField(max_length=10,null=True,blank=True)
    left43 = models.CharField(max_length=10,null=True,blank=True)
    right43 = models.CharField(max_length=10,null=True,blank=True)
    d44 = models.CharField(max_length=10,null=True,blank=True)
    top44 = models.CharField(max_length=10,null=True,blank=True)
    bot44 = models.CharField(max_length=10,null=True,blank=True)
    left44 = models.CharField(max_length=10,null=True,blank=True)
    right44 = models.CharField(max_length=10,null=True,blank=True)
    d45 = models.CharField(max_length=10,null=True,blank=True)
    top45 = models.CharField(max_length=10,null=True,blank=True)
    bot45 = models.CharField(max_length=10,null=True,blank=True)
    left45 = models.CharField(max_length=10,null=True,blank=True)
    right45 = models.CharField(max_length=10,null=True,blank=True)
    d46 = models.CharField(max_length=10,null=True,blank=True)
    top46 = models.CharField(max_length=10,null=True,blank=True)
    bot46 = models.CharField(max_length=10,null=True,blank=True)
    left46 = models.CharField(max_length=10,null=True,blank=True)
    right46 = models.CharField(max_length=10,null=True,blank=True)
    d47 = models.CharField(max_length=10,null=True,blank=True)
    top47 = models.CharField(max_length=10,null=True,blank=True)
    bot47 = models.CharField(max_length=10,null=True,blank=True)
    left47 = models.CharField(max_length=10,null=True,blank=True)
    right47 = models.CharField(max_length=10,null=True,blank=True)
    d48 = models.CharField(max_length=10,null=True,blank=True)
    top48 = models.CharField(max_length=10,null=True,blank=True)
    bot48 = models.CharField(max_length=10,null=True,blank=True)
    left48 = models.CharField(max_length=10,null=True,blank=True)
    right48 = models.CharField(max_length=10,null=True,blank=True)
    d51 = models.CharField(max_length=10,null=True,blank=True)
    top51 = models.CharField(max_length=10,null=True,blank=True)
    bot51 = models.CharField(max_length=10,null=True,blank=True)
    left51 = models.CharField(max_length=10,null=True,blank=True)
    right51 = models.CharField(max_length=10,null=True,blank=True)
    d52 = models.CharField(max_length=10,null=True,blank=True)
    top52 = models.CharField(max_length=10,null=True,blank=True)
    bot52 = models.CharField(max_length=10,null=True,blank=True)
    left52 = models.CharField(max_length=10,null=True,blank=True)
    right52 = models.CharField(max_length=10,null=True,blank=True)
    d53 = models.CharField(max_length=10,null=True,blank=True)
    top53 = models.CharField(max_length=10,null=True,blank=True)
    bot53 = models.CharField(max_length=10,null=True,blank=True)
    left53 = models.CharField(max_length=10,null=True,blank=True)
    right53 = models.CharField(max_length=10,null=True,blank=True)
    d54 = models.CharField(max_length=10,null=True,blank=True)
    top54 = models.CharField(max_length=10,null=True,blank=True)
    bot54 = models.CharField(max_length=10,null=True,blank=True)
    left54 = models.CharField(max_length=10,null=True,blank=True)
    right54 = models.CharField(max_length=10,null=True,blank=True)
    d55 = models.CharField(max_length=10,null=True,blank=True)
    top55 = models.CharField(max_length=10,null=True,blank=True)
    bot55 = models.CharField(max_length=10,null=True,blank=True)
    left55 = models.CharField(max_length=10,null=True,blank=True)
    right55 = models.CharField(max_length=10,null=True,blank=True)
    d61 = models.CharField(max_length=10,null=True,blank=True)
    top61 = models.CharField(max_length=10,null=True,blank=True)
    bot61 = models.CharField(max_length=10,null=True,blank=True)
    left61 = models.CharField(max_length=10,null=True,blank=True)
    right61 = models.CharField(max_length=10,null=True,blank=True)
    d62 = models.CharField(max_length=10,null=True,blank=True)
    top62 = models.CharField(max_length=10,null=True,blank=True)
    bot62 = models.CharField(max_length=10,null=True,blank=True)
    left62 = models.CharField(max_length=10,null=True,blank=True)
    right62 = models.CharField(max_length=10,null=True,blank=True)
    d63 = models.CharField(max_length=10,null=True,blank=True)
    top63 = models.CharField(max_length=10,null=True,blank=True)
    bot63 = models.CharField(max_length=10,null=True,blank=True)
    left63 = models.CharField(max_length=10,null=True,blank=True)
    right63 = models.CharField(max_length=10,null=True,blank=True)
    d64 = models.CharField(max_length=10,null=True,blank=True)
    top64 = models.CharField(max_length=10,null=True,blank=True)
    bot64 = models.CharField(max_length=10,null=True,blank=True)
    left64 = models.CharField(max_length=10,null=True,blank=True)
    right64 = models.CharField(max_length=10,null=True,blank=True)
    d65 = models.CharField(max_length=10,null=True,blank=True)
    top65 = models.CharField(max_length=10,null=True,blank=True)
    bot65 = models.CharField(max_length=10,null=True,blank=True)
    left65 = models.CharField(max_length=10,null=True,blank=True)
    right65 = models.CharField(max_length=10,null=True,blank=True)
    d71 = models.CharField(max_length=10,null=True,blank=True)
    top71 = models.CharField(max_length=10,null=True,blank=True)
    bot71 = models.CharField(max_length=10,null=True,blank=True)
    left71 = models.CharField(max_length=10,null=True,blank=True)
    right71 = models.CharField(max_length=10,null=True,blank=True)
    d72 = models.CharField(max_length=10,null=True,blank=True)
    top72 = models.CharField(max_length=10,null=True,blank=True)
    bot72 = models.CharField(max_length=10,null=True,blank=True)
    left72 = models.CharField(max_length=10,null=True,blank=True)
    right72 = models.CharField(max_length=10,null=True,blank=True)
    d73 = models.CharField(max_length=10,null=True,blank=True)
    top73 = models.CharField(max_length=10,null=True,blank=True)
    bot73 = models.CharField(max_length=10,null=True,blank=True)
    left73 = models.CharField(max_length=10,null=True,blank=True)
    right73 = models.CharField(max_length=10,null=True,blank=True)
    d74 = models.CharField(max_length=10,null=True,blank=True)
    top74 = models.CharField(max_length=10,null=True,blank=True)
    bot74 = models.CharField(max_length=10,null=True,blank=True)
    left74 = models.CharField(max_length=10,null=True,blank=True)
    right74 = models.CharField(max_length=10,null=True,blank=True)
    d75 = models.CharField(max_length=10,null=True,blank=True)
    top75 = models.CharField(max_length=10,null=True,blank=True)
    bot75 = models.CharField(max_length=10,null=True,blank=True)
    left75 = models.CharField(max_length=10,null=True,blank=True)
    right75 = models.CharField(max_length=10,null=True,blank=True)
    d81 = models.CharField(max_length=10,null=True,blank=True)
    top81 = models.CharField(max_length=10,null=True,blank=True)
    bot81 = models.CharField(max_length=10,null=True,blank=True)
    left81 = models.CharField(max_length=10,null=True,blank=True)
    right81 = models.CharField(max_length=10,null=True,blank=True)
    d82 = models.CharField(max_length=10,null=True,blank=True)
    top82 = models.CharField(max_length=10,null=True,blank=True)
    bot82 = models.CharField(max_length=10,null=True,blank=True)
    left82 = models.CharField(max_length=10,null=True,blank=True)
    right82 = models.CharField(max_length=10,null=True,blank=True)
    d83 = models.CharField(max_length=10,null=True,blank=True)
    top83 = models.CharField(max_length=10,null=True,blank=True)
    bot83 = models.CharField(max_length=10,null=True,blank=True)
    left83 = models.CharField(max_length=10,null=True,blank=True)
    right83 = models.CharField(max_length=10,null=True,blank=True)
    d84 = models.CharField(max_length=10,null=True,blank=True)
    top84 = models.CharField(max_length=10,null=True,blank=True)
    bot84 = models.CharField(max_length=10,null=True,blank=True)
    left84 = models.CharField(max_length=10,null=True,blank=True)
    right84 = models.CharField(max_length=10,null=True,blank=True)
    d85 = models.CharField(max_length=10,null=True,blank=True)
    top85 = models.CharField(max_length=10,null=True,blank=True)
    bot85 = models.CharField(max_length=10,null=True,blank=True)
    left85 = models.CharField(max_length=10,null=True,blank=True)
    right85 = models.CharField(max_length=10,null=True,blank=True)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey('Clinica',on_delete=models.PROTECT)

    def model_name(self):
        return "Ficha"
    
    def model_name_lower(self):
        return "ficha"

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

class Turno(models.Model):
    paciente = models.ForeignKey('Paciente',on_delete=models.PROTECT,blank=True,null=True)
    odontologo = models.ForeignKey('Odontologo',on_delete=models.PROTECT,blank=True,null=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    observaciones = models.TextField(max_length=1000,blank=True)
    todo_el_dia = models.BooleanField(blank=True,null=True)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    clinica = models.ForeignKey('Clinica',on_delete=models.PROTECT)
    
    def __str__(self):
    	return self.paciente.nombre_apellido

    def model_name(self):
        return "Turno"
    
    def model_name_lower(self):
        return "turno"

class Tutorial(models.Model):
    titulo = models.CharField(max_length=200,null=True,blank=True)
    descripcion = models.CharField(max_length=1000,null=True,blank=True)
    url = models.CharField(max_length=500,null=True,blank=True)
    categoria = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
    	return self.titulo

    def model_name(self):
        return "Tutorial"
    
    def model_name_lower(self):
        return "tutorial"

class Cuenta_Corriente(models.Model):
    fecha = models.DateTimeField()
    paciente = models.ForeignKey('Paciente',on_delete=models.CASCADE,blank=True,null=True)
    
    IE = [
        ('1', 'Ingreso'),
        ('2', 'Egreso'),
    ]
    ingreso_egreso = models.CharField(
        max_length=20,
        choices=IE,
        null=True,
        blank=True
    )
    concepto = models.CharField(max_length=4000, blank=True, null=True)
    importe = models.DecimalField(decimal_places=2, max_digits=12)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)    

    def model_name(self):
        return "Cuenta corriente"
    
    def model_name_lower(self):
        return "cuenta corriente"