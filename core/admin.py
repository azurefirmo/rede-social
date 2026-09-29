from django.contrib import admin
from .models import Perfil, Comunidade, Postagem, Comentario, Mensagem, Relacionamento

# Register your models here.

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'data_criacao')

@admin.register(Comunidade)
class ComunidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_criacao')
    filter_horizontal = ('membros', 'administradores')

@admin.register(Postagem)
class PostagemAdmin(admin.ModelAdmin):
    list_display = ('autor', 'tipo', 'data_postagem', 'comunidade')
    list_filter = ('tipo', 'data_postagem', 'comunidade')
    raw_id_fields = ('autor', 'curtidas')

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'postagem', 'data_comentario')
    list_filter = ('data_comentario',)
    raw_id_fields = ('autor', 'postagem')

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ('remetente', 'destinatario', 'data_envio')
    list_filter = ('data_envio',)
    raw_id_fields = ('remetente', 'destinatario')

@admin.register(Relacionamento)
class RelacionamentoAdmin(admin.ModelAdmin):
    list_display = ('usuario_de', 'usuario_para', 'tipo')
    list_filter = ('tipo',)
    raw_id_fields = ('usuario_de', 'usuario_para')
