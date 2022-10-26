from ast import If
import re
from unicodedata import name
from django import template
from pedidos.models import Pedido
from users.models import User
from colecoes.models import Colecao
from lojas.models import Loja
from roupas.models import Roupa
from django.contrib.auth.models import Group
from django.utils.html import escape, mark_safe

register = template.Library()

@register.inclusion_tag('logBox.html')
def login_box(request):
    if request.user.is_authenticated:
        logged = True
        if request.user.groups.filter(name = 'usuario_normal').exists() and not request.user.groups.filter(name = 'usuario_dono_loja').exists():
            if not request.user.foto_usuario:
                perfil = request.user.nome[0]
            elif request.user.foto_usuario:
                perfil = request.user.foto_usuario.url
                perfil = f"<div class='userFT'><img src='{escape(perfil)}'></div>"
        elif request.user.groups.filter(name = 'usuario_dono_loja').exists():
            if request.user.loja.logo_loja:
                perfil = request.user.loja.logo_loja.url
                perfil = f"<div class='userFT'><img src='{escape(perfil)}'></div>"
            else:
                if request.user.foto_usuario:
                    perfil = request.user.foto_usuario.url
                    perfil = f"<div class='userFT'><img src='{escape(perfil)}'></div>"
                else:
                    perfil = request.user.loja.nome_loja[0]
                
    else:
        perfil = 'None'
        logged = False
    return {
        'perfil': mark_safe(perfil),
        'logged': logged,
    }

@register.inclusion_tag('menu_user.html')
def menu_user(request):
    if request.user.is_authenticated:
        logged = True
        loja = False
        if request.user.groups.filter(name='usuario_dono_loja').exists():
            loja = True
        else:
            loja = False
    else:
        logged = False
        loja = False
    return {
        'logged':logged,
        'loja' : loja,
    }

@register.inclusion_tag('btn_atualizar.html')
def btn_atualizar(request):
    if request.user.is_authenticated:
        logged = True
        loja = False
        if request.user.groups.filter(name='usuario_dono_loja').exists():
            loja = True
        else:
            loja = False
    else:
        logged = False
        loja = False
    return {
        'logged':logged,
        'loja' : loja,
    }

@register.inclusion_tag('colecoes_lista.html')
def colecoes_lista(request):
    colecoes = Colecao.objects.filter(loja = request.user.loja)
    return {
        'colecoes':colecoes,
    }

@register.inclusion_tag('card_colecoes.html')
def card_colecoes(request, pk):
    colecao = Colecao.objects.get(pk=pk)
    roupas = Roupa.objects.filter(colecao = colecao)

    return {
        'roupas':roupas,
        'colecao':colecao,
    }

@register.inclusion_tag('barra_pesquisa.html')
def barra_pesquisa(request):
    return {
        'request': request,
    }

@register.inclusion_tag('header.html')
def header(request):
    return {
        'request': request,
    }

@register.inclusion_tag('footer.html')
def footer():
    return {
        
    }

@register.inclusion_tag('gerenciador.html')
def gerenciador():
    
    return {

    }

@register.inclusion_tag('card_pacote.html')
def card_pacote(request):
    context = {}
    if request.user.is_authenticated:
        user = User.objects.get(email=request.user.email)
        pedidos = Pedido.objects.filter(usuario_pedinte=user)
        context['pedidos'] = pedidos
    return context