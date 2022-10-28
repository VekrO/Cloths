from email.policy import default
from multiprocessing.sharedctypes import Value
from sre_constants import GROUPREF_UNI_IGNORE
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
import re
from django.core.files.storage import FileSystemStorage
import os


#LOCAL
from enderecos.models import Endereco

# Create your models here.
class CustomUserManager(BaseUserManager):

    def get_user(self, email):
        if not email:
            raise ValueError('Insira um email')
        user = self.get(email=email)
        return user
    def valida_cpf(self, cpf):
        formato_cpf = re.compile('^\d{3}.\d{3}.\d{3}-\d{2}$')
        is_valido = formato_cpf.match(str(cpf))
        return bool(is_valido)
    def valida_telefone(self, telefone):
        formato_telefone = re.compile('^(\d{2})\d{5}-\d{4}')
        is_valido = formato_telefone.match(str(telefone))
        return bool(is_valido)
    def get_grupo(self, grupo):
        grupo = Group.objects.get(name=grupo)
        return grupo
    def rm_grupo(self, nomeGrupo):
        if not nomeGrupo:
            raise ValueError ('Para remover o usuário de um grupo, é necessário inserir seu nome')
        grupo = self.get_grupo(nomeGrupo)
        self.groups.remove(grupo)
        self.save()
    def set_grupo(self, nomeGrupo):
        if not nomeGrupo:
            raise ValueError('Para associar o usuário a um grupo, é necessário que o mesmo exista')
        grupo = self.get_grupo(nomeGrupo)
        if grupo == None:
            raise ValueError('Esse grupo não existe')
        self.groups.add(grupo)
        self.save()
    def create_gen_user(self, email, password, **other):
        if not email:
            raise ValueError('Todo usuário necessita de um email')
        
        if not password:
            raise ValueError('Todo usuário deve possuir uma senha')
        email = self.normalize_email(email)
        user = self.model(email=email, **other)
        user.set_password(password)
        user.save(using=self._db)
        user.set_grupo('usuario_normal')
        user.save(using=self._db)
        return user

    def create_user(self, email, password, cpf, **other):
        other.setdefault('is_superuser', False)
        other.setdefault('is_staff', False)
        other.setdefault('is_active', True)

        if other.get('is_superuser') is not False:
            raise ValueError('Todo user normal deve ter is_superuser=False')
        if other.get('is_staff') is not False:
            raise ValueError('Todo user normal deve ter is_staff=False')
        if other.get('is_active') is not True:
            raise ValueError('Todo usuário recém-criado deve ter is_active=True')
        if not cpf:
            raise ValueError('Todo usuário deve possuir um CPF')

        if self.valida_cpf(cpf) is not True:
            raise ValueError('Todo CPF deve ser da forma xxx.xxx.xxx-xx')

        return self.create_gen_user(email, password, cpf=cpf, **other)

    def create_superuser(self, email, password, **other):
        other.setdefault('is_superuser', True)
        other.setdefault('is_staff', True)
        other.setdefault('is_active', True)

        if other.get('is_superuser') is not True:
            raise ValueError('Todo superuser deve ter is_superuser=True')
        if other.get('is_staff') is not True:
            raise ValueError('Todo superuser deve ter is_staff=True')
        if other.get('is_active') is not True:
            raise ValueError('Todo usuário recém-criado deve ter is_active=True')

        return self.create_gen_user(email, password, **other)


class User(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=255)
    cpf = models.CharField(max_length=15)
    rg = models.CharField(max_length=15, null=True, blank=True)

    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, related_name='user', null=True)
    foto_usuario = models.ImageField(null=True, blank=True, upload_to='fotos_usuarios/', default=None)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'


    def set_foto_usuario(self, caminho, uploadImage, request):
        if request.FILES:
            fs = FileSystemStorage(location='media/'+caminho+'/', base_url='/'+caminho+'/')
            upload = request.FILES[uploadImage]
            upload_name = upload.name
            upload_name = upload_name.replace(" ", "")
            upload_name = upload_name.replace("ç","c")
            filename = fs.save(upload.name.replace(" ",""), upload)
            url = fs.url(filename)
            if url:
                if self.foto_usuario:
                    currentDirectory=os.getcwd()
                    fs.delete(currentDirectory+self.foto_usuario.url)
                setattr(self, 'foto_usuario', url)
                self.save()

    def rm_grupo(self, nomeGrupo):
        if not nomeGrupo:
            raise ValueError ('Para remover o usuário de um grupo, é necessário inserir seu nome')
        grupo = self.get_grupo(nomeGrupo)
        self.groups.remove(grupo)
        self.save()
    def set_grupo(self, nomeGrupo):
        if not nomeGrupo:
            raise ValueError('Para associar o usuário a um grupo, é necessário que o mesmo exista')
        grupo = self.get_grupo(nomeGrupo)
        if grupo == None:
            raise ValueError('Esse grupo não existe')
        self.groups.add(grupo)
        self.save()
    def valida_telefone(self, telefone):
        formato_telefone = re.compile('^(\d{2})\d{5}-\d{4}')
        is_valido = formato_telefone.match(str(telefone))
        return bool(is_valido)

    def set_nome(self, nome):
        self.nome = nome
        self.save()
    def set_telefone(self, telefone):
        if not self.valida_telefone(telefone):
            raise ValueError('Todo telefone deve ser da forma (xx)xxxxx-xxxx')
        self.telefone = telefone
        self.save()
    def get_grupo(self, grupo):
        grupo = Group.objects.get(name=grupo)
        return grupo
    def alter_fields(self, fields, values):
        if len(fields) != len(values):
            raise ValueError('As listas de campos e valores devem ter tamanhos iguais')
        for field, value in zip(fields, values):
            if value and not value.isspace():
                setattr(self, field, value)
            self.save()

    def __str__(self):
        return self.email
    

