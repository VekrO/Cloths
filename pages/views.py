from tkinter import N
from django.shortcuts import HttpResponse, render, redirect
from django.views import View
#Contrib
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.storage import FileSystemStorage
#local
from enderecos.models import Endereco
from lojas.models import Loja, Plano
from colecoes.models import Colecao
from pedidos.models import Item, Pedido
from roupas.models import Categoria, Roupa

from django.views.decorators.csrf import csrf_exempt
import uuid
# Create your views here.


def get_POST_form_fields(request, fields):
    dicionario = {}
    for field in fields:
        val = request.POST.get(field)
        dicionario[str(field)] = val
    return dicionario

def sair(request):
    logout(request)
    return redirect('home')

class Home(View):
    def get(self, request):
        return render(request, 'home.html')
    def post(self, request):
        pass

class Login(View):
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        d = get_POST_form_fields(request, ['email', 'senha'])
        if len(d) < 2:
            raise ValueError('Faltam valores a serem inseridos')
        user = authenticate(request, email=d['email'], password=d['senha'])
        login (request, user)
        return redirect('home')

class Cadastro(View):
    def get(self, request):
        return render(request, 'creatAcount.html')
    def post(self, request):
        d = get_POST_form_fields(request, ['nome', 'cpf', 'rg', 'telefone', 'email', 'senha', 'cep', 'estado', 'cidade', 'rua', 'bairro', 'numero'])
        if len(d) < 12:
            raise ValueError('Faltam valores a serem inseridos')
        endereco = Endereco.objects.create_endereco(d['cep'], d['estado'], d['cidade'], d['bairro'], d['rua'], d['numero'])
        endereco.save()
        db=get_user_model()
        user = db.objects.create_user(d['email'], d['senha'], d['cpf'], nome=d['nome'], telefone=d['telefone'], rg=d['rg'], endereco=endereco)
        user.save()
        return redirect('home')

class Perfil(View):
    def get(self, request):
        return render(request, 'perfil_usuario.html')
    def post(self, request):
        pass

class EditarPerfil(View):
    def get(self, request):
        return render(request, 'perfil_usuario_editar.html')
    def post(self, request):
        d = get_POST_form_fields(request, ['nome', 'telefone'])
        e = get_POST_form_fields(request, ['cep', 'estado', 'cidade', 'rua', 'bairro', 'numero'])
        if len(d) < 2:
            raise ValueError('Faltam valores a serem inseridos')
        user = get_user_model().objects.get_user(request.user.email)
        user.alter_fields(list(d.keys()),list(d.values()))
        user.set_foto_usuario('fotos_usuarios', 'foto_usuario', request)
        return redirect('perfil')

class PerfilLoja(View):
    def get(self, request):
        return render(request, 'perfil_loja.html')
    def post(self, request):
        pass

class EditarPerfilLoja(View):
    def get(self, request):
        return render(request, 'perfil_loja_editar.html')
    def post(self, request):
        d = get_POST_form_fields(request, ['nome_loja', 'telefone_loja', 'email_loja'])
        if len(d) < 3:
            raise ValueError('Falitam valores a serem inseridos')
        loja = request.user.loja
        loja.alter_fields(list(d.keys()), list(d.values()))
        loja.set_logo_loja('logos_lojas', 'logo', request)
        return redirect('perfil_loja')

class Planos(View):
    def get(self, request):
        return render(request, 'planos.html')
    def post(self, request):
        pass

class AtualizarParaContaComercial(View):
    def get(self, request, plano):
        self.plano = plano
        context = {'plano': plano}
        return render(request, 'AtualizarParaContaComercial.html', context)
    def post(self, request, plano):
        d = get_POST_form_fields(request, ['nome_loja', 'cnpj', 'numero_cartao', 'nome_cartao', 'cvv', 'data_expiracao'])
        e = get_POST_form_fields(request, ['cep', 'estado', 'cidade', 'rua', 'bairro', 'numero'])
        endereco = Endereco.objects.easy_create_endereco(list(e.keys()), list(e.values()))
        user = get_user_model().objects.get_user(request.user.email)
        loja = Loja.objects.create_loja(user, d['nome_loja'],d['cnpj'], d['numero_cartao'], d['nome_cartao'], d['cvv'], data_expiracao=d['data_expiracao'], endereco=endereco, plano=plano)
        loja.save()
        return redirect('perfil')

class MinhasColecoes(View):
    def get(self, request):
        return render(request, 'minhas_colecoes.html')
    def post(self, request):
        pass

def add_colecao(request):
    nome = request.POST.get('nome')
    Colecao.objects.create_colecao(nome, request.user.loja)
    return redirect('minhas_colecoes')

class VerColecao(View):
    def get(self, request, pk):
        context= {'pk':pk,}
        self.pk = pk
        return render(request, 'minhas_colecoes.html', context)
    def post(self, request, pk):
        d = get_POST_form_fields(request, ['nome_roupa', 'preco', 't1', 't2', 't3', 't4', 't5', 't6'])
        colecao = Colecao.objects.get(pk=pk)
        d['colecao'] = colecao
        categoria = Categoria.objects.get(nome_categoria=request.POST.get('categoria'))
        d['categoria'] = categoria
        #isso daqui é o easy create, com duas listas
        #roupa = Roupa.objects.easy_create_roupa(list(d.keys()), list(d.values())) 
        #roupa.set_foto('fotos_roupas', 'foto', request)
        #roupa.save()
        roupa = Roupa.objects.create_roupa(d['nome_roupa'],d['preco'],categoria, colecao, d['t1'],d['t2'],d['t3'],d['t4'],d['t5'],d['t6'])
        roupa.set_foto('fotos_roupas', 'foto', request)
        roupa.save()
        return redirect('colecao', pk = pk)

class TelaPesquisa(View):
    def get(self, request):
        query = request.GET.get('query')
        context = {'query':query}
        context ['resultados_roupas'] = Roupa.objects.pesquisa_roupas(query)
        context ['resultados_lojas'] = Loja.objects.pesquisa_lojas(query)
        return render(request, 'pesquisa.html', context)
    def post(self, request):
        pass

def pesquisar(self, request):
    return redirect('tela_pesquisa')

def delete(request, colecaoPk,roupaPk):
    roupa = Roupa.objects.get(pk=roupaPk)
    roupa.delete()
    return redirect('colecao', pk=colecaoPk)

class LojasCadastradas(View):
    def get(self, request):
        context = {
            'lojas': Loja.objects.all(),
        }
        #necessita Refatorar
        estados_com_loja = Endereco.objects.filter(loja__nome_loja__icontains='').values('estado').distinct()
        enderecos = Endereco.objects.filter(loja__nome_loja__icontains='').values('cidade', 'estado').distinct()
        context['estados_com_loja'] = estados_com_loja
        context['enderecos'] = enderecos
        #necessita refatorar
        return render (request, 'cidades_por_estado.html', context)
    def post(self, request):
        pass

class LojasCidade(View):
    def get(self, request, cidade):
        context = {}
        context['cidade'] = cidade
        context['lojas_cidade'] = Loja.objects.filter(endereco__cidade=cidade).order_by('nome_loja')
        return render(request, 'lojas_cidade.html', context)
    def post(self, request):
        pass

class LojaVer(View):
    def get(self, request, cidade, loja):
        context={}
        loja = Loja.objects.get(nome_loja = loja)
        context['loja'] = loja
        colecoes = Colecao.objects.filter(loja=loja)
        context['colecoes'] = colecoes
        context['roupas'] = Roupa.objects.all()
        context['cidade'] = cidade
        return render(request, 'loja_ver.html', context)
    def post(self, request):
        pass

class RoupaVer(View):
    def get(self, request, cidade, loja, roupa):

        # Caso o usuário não esteja conectado.
        context = {}
        context['loja'] = Loja.objects.get(nome_loja=loja)
        context['roupa'] = Roupa.objects.get(pk=roupa)

        if(request.user.is_authenticated):
            print('Conectado')
            context['user_id'] = request.user.pk
            return render(request, 'ropa.html', context)
        else:

            # Usuário Anônimo.
            # Gerar um ID único para o usuário não conectado!
            id_unico = uuid.uuid4()
            print(id_unico)
            context['user_id'] = id_unico
            return render(request, 'ropa.html', context)

    def post(self, request):
        pass

class EmBreve(View):
    def get(self, request):
        return render (request, 'emBreve.html')
    def post(self, request):
        pass

class MeusPacotes(View):
    def get(self, request):
        context = {}
        if request.user.is_authenticated:
            pedidos = Pedido.objects.filter(usuario_pedinte=request.user)
            context['pedidos'] = pedidos
        return render (request, 'meusPacotes.html', context)

    def post(self, request):

        # Receber e pegar parâmetros.
        id = request.POST.get('product_id')
        quantidade = request.POST.get('product_qnt')
        tamanho = request.POST.get('product_size')
        loja_id = request.POST.get('loja_id')
        user_id = request.POST.get('user_id')
        
        roupa = Roupa.objects.get(pk=id)

        item = Item.objects.create(
            user_id=user_id,
            roupa=roupa,
            tamanho=tamanho,
            quantidade=quantidade,
        )

        Pedido.objects.adicionar_item(item=item, user_id=user_id, loja_id=loja_id)

        return HttpResponse('Salve')

class MeusPedidos(View):
    def get(self, request):
        context = {}
        pedidos = Pedido.objects.filter(loja=request.user.loja).order_by('data_pedido')
        context['pedidos'] = pedidos
        return render (request, 'pedidos.html', context)
    def post(self, request):
        pass

class VerPedido(View):
    def get(self, request, pk):
        #é só para lojas
        context = {}
        pedido = Pedido.objects.get(pk=pk)
        context['pedido'] = pedido
        return render(request, 'pedido.html', context)
    def post(self, request):
        pass