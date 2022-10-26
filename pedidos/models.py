from ast import USub
from django.db import models
from django.utils import timezone
#LOCAL
from users.models import User
from lojas.models import Loja
from roupas.models import Roupa

# Create your models here.
class Item(models.Model):
    user_id = models.CharField(max_length=255)
    roupa = models.ForeignKey(Roupa, on_delete=models.CASCADE, related_name='item')
    tamanho = models.CharField(max_length=2)
    quantidade = models.PositiveBigIntegerField(default=0)
    
    def __str__(self):
        return self.roupa.nome_roupa+'/'+self.roupa.colecao.nome+'/'+self.roupa.colecao.loja.nome_loja+'/'+str(self.quantidade)

class PedidoManager(models.Manager):
    
    def create_pedido(self, user_id, loja_id):
        pedido = self.model(
                usuario_pedinte = user_id,
                loja = Loja.objects.get(pk=loja_id),
                status='NF'
            )
        pedido.save()
        return pedido

    def adicionar_item(self, item, user_id, loja_id):

        if self.filter(usuario_pedinte=user_id, loja=Loja.objects.get(pk=loja_id)).exists():
            pedido = self.get(usuario_pedinte=user_id, loja=Loja.objects.get(pk=loja_id))
            pedido.add_item(item)
        elif not self.filter(usuario_pedinte=user_id, loja=Loja.objects.get(pk=loja_id)).exists():
            pedido = self.create_pedido(user_id, loja_id)
            pedido.add_item(item)

            

class AbstractPedidoManager(models.Model):
    objects = PedidoManager()
    class Meta:
        abstract = True

class Pedido(AbstractPedidoManager):
    status_choices = [
        ('NF', 'Pedido não realizado!'),
        ('FE', 'Pedido encaminhado!'),
        ('EV', 'Pedido enviado!'),
        ('ET', 'Entregue!'),
        ('DV', 'Pedido devolvido!'),
    ]

    usuario_pedinte = models.CharField(max_length=255)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='pedido')
    itens = models.ManyToManyField(Item)

    data_pedido = models.DateField(default=timezone.now)
    data_entrega = models.DateField(null=True, blank=True)
    data_devolução = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=status_choices)

    def __str__(self):
        return self.usuario_pedinte+"/"+self.loja.nome_loja
    def add_item(self, item):
        if not item:
            raise ValueError('Não tem item, você precisa de um!')
            
        self.itens.add(item)
        self.save()
    
    def delete_item(self, item):
        
        if not item:
            raise ValueError('Não tem item, você precisa de um!')
        self.itens.remove(item)
        self.save()


class PedidoConcluido(Pedido):
    itens_comprados = models.ManyToManyField(Roupa)
    preco_final = models.FloatField()
    data_conclusão = models.DateField(default=timezone.now)
