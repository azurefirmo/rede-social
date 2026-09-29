from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('entrar/', views.login_view, name='login'), # Usando o nome corrigido
    path('sair/', views.logout_view, name='logout'), # Usando o nome corrigido
    path('postar/', views.criar_postagem, name='criar_postagem'),
    path('curtir/<int:postagem_id>/', views.curtir_descurtir_postagem, name='curtir_postagem'),
    path('comentar/<int:postagem_id>/', views.adicionar_comentario, name='adicionar_comentario'),
    path('atualizar-comentarios/<int:postagem_id>/', views.atualizar_comentarios, name='atualizar_comentarios'),

    # URLs para Perfil
    path('perfil/<str:username>/', views.perfil_view, name='perfil'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),

    # URLs para Comunidades
    path('comunidades/', views.comunidades_lista_view, name='comunidades_lista'),
    path('comunidade/<int:comunidade_id>/', views.comunidade_detalhe_view, name='comunidade_detalhe'),
    path('comunidade/<int:comunidade_id>/juntar/', views.juntar_comunidade_view, name='juntar_comunidade'),
    path('comunidade/<int:comunidade_id>/sair/', views.sair_comunidade_view, name='sair_comunidade'),
    path('comunidade/criar/', views.criar_comunidade_view, name='criar_comunidade'),

    # URLs para Mensagens
    path('mensagens/', views.mensagens_lista_view, name='mensagens_lista'),
    path('mensagens/para/<int:destinatario_id>/', views.mensagens_conversa_view, name='mensagens_conversa'),
    path('mensagens/enviar/para/<int:destinatario_id>/', views.enviar_mensagem_view, name='enviar_mensagem'),

    # URLs para Relacionamentos
    path('relacionamento/<int:usuario_para_id>/solicitar/', views.relacionamento_enviar_solicitacao_view, name='relacionamento_enviar_solicitacao'),
    path('relacionamento/<int:relacionamento_id>/<str:acao>/', views.relacionamento_aceitar_recusar_view, name='relacionamento_aceitar_recusar'),
    path('relacionamento/<int:usuario_para_id>/cancelar/', views.relacionamento_cancelar_view, name='relacionamento_cancelar'),

    # URL para Notificações
    path('notificacoes/', views.notificacoes_view, name='notificacoes'),

    # URLs para Explorar
    path('explorar/', views.explorar_view, name='explorar'),

    # Adicione mais URLs para outras funcionalidades (perfil, comunidade, mensagem, etc.)
]
