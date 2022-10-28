from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
import os

#local
from colecoes.models import Colecao
# Create your models here.

class Tamanho(models.Model):
    nome_tipo = models.CharField(max_length=255)

    def __str__(self):
        return self.nome_tipo

class Categoria(models.Model):
    nome_categoria = models.CharField(max_length=255)
    tipo_tamanho = models.ForeignKey(Tamanho, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.nome_categoria


class RoupaManager(models.Manager):
    def pesquisa_roupas(self, query):
        if query:
            resultado = self.model.objects.filter(nome_roupa__icontains=query).order_by('nome_roupa')
        else:
            resultado = self.model.objects.all().order_by('nome_roupa')
        return resultado
    def easy_create_roupa(self, fields, values):
        if len(fields) != len(values):
            raise ValueError('Ambas as listas devem ter o mesmo tamanho')
        roupa = self.model()
        roupa.save()
        for field, value in zip(fields, values):
            print(field, value)
            if value and not value.isspace():
                setattr(roupa, field, value)
            elif value == None:
                setattr(roupa, field, 0)
        roupa.save()
        return roupa
    def create_roupa(self, nome_roupa, preco, categoria, colecao, t1,t2,t3,t4,t5,t6):
        if not nome_roupa:
            raise ValueError('Toda roupa precisa de um nome')
        if not preco:
            raise ValueError('Toda roupa precisa de um preço')
        if not categoria:
            raise ValueError('Toda roupa precisa de uma categoria')
        if not colecao:
            raise ValueError('Toda roupa deve pertencer a uma coleção')
        if not t1 and not t2 and not t3 and not t4 and not t5 and not t6:
            raise ValueError ('Toda roupa precisa de seus tamanhos especificados')
        l = [t1, t2, t3, t4, t5 , t6]
        for i in range (len(l)):
            if l[i] == None:
                l[i] = 0
        roupa = self.model(nome_roupa=nome_roupa, preco=preco, categoria=categoria, colecao=colecao, t1=l[0],t2=l[1],t3=l[2],t4=l[3],t5=l[4],t6=l[5])
        roupa.save()
        return roupa


class AbstractRoupaManager(models.Model):
    objects = RoupaManager()
    class Meta:
        abstract = True

class Roupa(AbstractRoupaManager):
    colecao = models.ForeignKey(Colecao, on_delete=models.CASCADE, null=True, related_name='roupa')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, null=True, related_name='roupa')
    
    nome_roupa = models.CharField(max_length=255)
    preco = models.FloatField()

    data_adicao = models.DateField(default=timezone.now)

    foto = models.ImageField(upload_to='fotos_roupas/', null=True)

    t1 = models.PositiveIntegerField(default=0)
    t2 = models.PositiveIntegerField(default=0)
    t3 = models.PositiveIntegerField(default=0)
    t4 = models.PositiveIntegerField(default=0)
    t5 = models.PositiveIntegerField(default=0)
    t6 = models.PositiveIntegerField(default=0)

    def set_foto(self, caminho, uploadImage, request):
        if request.FILES:
            fs = FileSystemStorage(location='media/'+caminho+'/', base_url='/'+caminho+'/')
            upload = request.FILES[uploadImage]
            upload_name = upload.name
            upload_name = upload_name.replace(" ", "")
            upload_name = upload_name.replace("ç","c")
            filename = fs.save(upload.name.replace(" ",""), upload)
            url = fs.url(filename)
            if url:
                if self.foto:
                    currentDirectory=os.getcwd()
                    fs.delete(currentDirectory+self.foto.url)
                setattr(self, 'foto', url)
                self.save()

    def __str__(self):
        return self.nome_roupa+'/'+self.colecao.nome+'/'+self.colecao.loja.nome_loja

