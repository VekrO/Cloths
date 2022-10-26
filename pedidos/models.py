from ast import USub
from django.db import models
from django.utils import timezone
#LOCAL
from users.models import User
from lojas.models import Loja
from roupas.models import Roupa

# Create your models here.
class StatusPedido(models.Model):
    nome_status = models.CharField(max_length=255)

    def __str__(self):
        return self.nome_status

class Item(models.Model):
    roupa = models.ForeignKey(Roupa, on_delete=models.CASCADE, related_name='item') 
    tamanho = models.CharField(max_length=2, null=True)
    quantidade = models.PositiveBigIntegerField(default=0)
    
    def __str__(self):
        return self.roupa.nome_roupa+'/'+self.roupa.colecao.nome+'/'+self.roupa.colecao.loja.nome_loja+'/'+str(self.quantidade)

class PedidoManager(models.Manager):
    pass

class AbstractPedidoManager(models.Model):
    objects = PedidoManager()
    class Meta:
        abstract = True


class Pedido(AbstractPedidoManager):
    usuario_pedinte = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedido')
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='pedido')
    itens = models.ManyToManyField(Item)

    data_pedido = models.DateField(default=timezone.now)
    data_entrega = models.DateField(null=True, blank=True)
    data_devolução = models.DateField(null=True, blank=True)

    status = models.ForeignKey(StatusPedido, on_delete=models.PROTECT, related_name='pedido')

    def __str__(self):
        return self.usuario_pedinte.email + '/' + self.loja.nome_loja

class PedidoConcluido(Pedido):
    itens_comprados = models.ManyToManyField(Roupa)
    preco_final = models.FloatField()
    data_conclusão = models.DateField(default=timezone.now)

