from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.db import models
from django.template.loader import render_to_string
from django.core.paginator import Paginator

from .models import Postagem, Comunidade, Comentario, Mensagem, Relacionamento, Perfil
from .forms import PostagemForm, ComentarioForm # Adicione PerfilForm se necessário

# Create your views here.

# --- Views para Autenticação ---

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Cria automaticamente um perfil para o novo usuário
            Perfil.objects.create(usuario=user)
            # Opcional: Loga o usuário automaticamente após o registro
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

def login_view(request): # Nome alterado para evitar conflito com login do django.contrib.auth
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                # Redireciona para a página de origem ou para a home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home') # Ou para a página inicial pública

# --- Views para Timeline ---

def home(request):
    if request.user.is_authenticated:
        # Timeline: Postagens de amigos e comunidades que o usuário faz parte
        amigos_ids = Relacionamento.objects.filter(usuario_de=request.user, tipo='amigo').values_list('usuario_para_id', flat=True)
        comunidades_ids = request.user.comunidades_membro.values_list('id', flat=True)

        # Filtra postagens de amigos OU postagens em comunidades que o usuário faz parte
        timeline_posts = Postagem.objects.filter(
            models.Q(autor__in=amigos_ids) |
            models.Q(comunidade__in=comunidades_ids)
        ).order_by('-data_postagem')

        # Paginação (opcional para MVP, mas útil)
        paginator = Paginator(timeline_posts, 10)  # 10 postagens por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        form = PostagemForm()
        comentarios_form = ComentarioForm()

        context = {
            'page_obj': page_obj, # Usar page_obj no template em vez de timeline_posts
            'form': form,
            'comentarios_form': comentarios_form,
        }
        return render(request, 'core/timeline.html', context)
    else:
        # Página inicial para usuários não logados
        return render(request, 'core/index.html')

@login_required
def criar_postagem(request):
    if request.method == 'POST':
        form = PostagemForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            messages.success(request, 'Postagem criada com sucesso!')
            return redirect('home')
    return redirect('home')

@login_required
def apagar_postagem(request, postagem_id):
    """Somente o autor pode apagar sua própria postagem."""
    postagem = get_object_or_404(Postagem, id=postagem_id)

    if postagem.autor != request.user:
        messages.error(request, "Você não tem permissão para apagar esta postagem.")
        return redirect('home') # Ou para a página de origem, se possível

    if request.method == 'POST':
        postagem.delete()
        messages.success(request, "Postagem apagada com sucesso.")
        return redirect('home') # Ou para o perfil do autor

    # Se for GET, pode mostrar uma confirmação ou redirecionar
    messages.error(request, "Método inválido para apagar postagem.")
    return redirect('home')

@login_required
def curtir_descurtir_postagem(request, postagem_id):
    postagem = get_object_or_404(Postagem, id=postagem_id)
    user = request.user
    # Impedir que o autor curta sua própria postagem (se for regra de negócio)
    # if postagem.autor == user:
    #     messages.warning(request, "Você não pode curtir sua própria postagem.")
    #     return redirect('home') # Ou retornar JsonResponse com erro

    if user in postagem.curtidas.all():
        postagem.curtidas.remove(user)
        curtido = False
    else:
        postagem.curtidas.add(user)
        curtido = True
    # Retorna JSON com o novo número de curtidas e estado
    return JsonResponse({'curtidas_count': postagem.curtidas.count(), 'curtido': curtido})

@login_required
def adicionar_comentario(request, postagem_id):
    postagem = get_object_or_404(Postagem, id=postagem_id)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.autor = request.user
            comentario.postagem = postagem
            comentario.save()
            # Após salvar, renderiza o partial com os comentários atualizados
            comentarios_html = render_to_string('core/partials/comentarios.html', {'postagem': postagem}, request=request)
            return HttpResponse(comentarios_html)
    # Se não for POST ou o formulário for inválido, retorna um erro ou redireciona
    return redirect('home')

@login_required
def apagar_comentario(request, comentario_id):
    """Somente o autor pode apagar seu próprio comentário."""
    comentario = get_object_or_404(Comentario, id=comentario_id)

    if comentario.autor != request.user:
        messages.error(request, "Você não tem permissão para apagar este comentário.")
        return redirect('home') # Ou para a postagem original

    if request.method == 'POST':
        comentario.delete()
        messages.success(request, "Comentário apagado com sucesso.")
        return redirect('home') # Ou para a postagem original

    messages.error(request, "Método inválido para apagar comentário.")
    return redirect('home')

def atualizar_comentarios(request, postagem_id):
    """
    View para retornar o HTML atualizado dos comentários de uma postagem via AJAX.
    Usa um partial template para renderizar os comentários.
    """
    postagem = get_object_or_404(Postagem, id=postagem_id)
    # Renderiza o partial template 'partials/comentarios.html' com o contexto da postagem
    comentarios_html = render_to_string('core/partials/comentarios.html', {'postagem': postagem}, request=request)
    # Retorna o HTML renderizado como resposta HTTP
    return HttpResponse(comentarios_html)

# --- Views para Perfil ---

@login_required
def perfil_view(request, username=None):
    # Se username não for fornecido, mostra o perfil do usuário logado
    if username:
        profile_user = get_object_or_404(Perfil.usuario, username=username).perfil
        is_own_profile = profile_user.usuario == request.user
    else:
        profile_user = request.user.perfil
        is_own_profile = True

    # Obter postagens do usuário do perfil
    user_posts = Postagem.objects.filter(autor=profile_user.usuario).order_by('-data_postagem')

    # Obter informações sobre relacionamentos
    amigos_count = Relacionamento.objects.filter(usuario_de=profile_user.usuario, tipo='amigo').count() + \
                   Relacionamento.objects.filter(usuario_para=profile_user.usuario, tipo='amigo').count()
    seguidores_count = Relacionamento.objects.filter(usuario_para=profile_user.usuario, tipo='seguidor').count()
    seguindo_count = Relacionamento.objects.filter(usuario_de=profile_user.usuario, tipo='seguidor').count()

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'user_posts': user_posts,
        'amigos_count': amigos_count,
        'seguidores_count': seguidores_count,
        'seguindo_count': seguindo_count,
    }
    return render(request, 'core/perfil.html', context)

@login_required
def editar_perfil_view(request):
    """Somente o proprietário do perfil pode editá-lo."""
    # Obtem o perfil do usuário logado, não de outro usuário
    perfil = get_object_or_404(Perfil, usuario=request.user)

    if request.method == 'POST':
        # Supondo que você tenha um PerfilForm (crie-o em forms.py se desejar campos específicos)
        # form = PerfilForm(request.POST, request.FILES, instance=perfil)
        # Por enquanto, vamos atualizar manualmente os campos comuns
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        perfil.biografia = request.POST.get('biografia', '')
        if 'foto_perfil' in request.FILES:
            perfil.foto_perfil = request.FILES['foto_perfil']
        request.user.save()
        perfil.save()
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('perfil', username=request.user.username) # Redireciona para o próprio perfil

    context = {
        'perfil': perfil,
    }
    return render(request, 'core/editar_perfil.html', context)

# --- Views para Comunidades ---

@login_required
def comunidades_lista_view(request):
    comunidades = Comunidade.objects.all().order_by('nome')
    context = {
        'comunidades': comunidades,
    }
    return render(request, 'core/comunidade_list.html', context)

@login_required
def comunidade_detalhe_view(request, comunidade_id):
    comunidade = get_object_or_404(Comunidade, id=comunidade_id)
    # Verifica se o usuário é membro (necessário se comunidades forem privadas)
    # if request.user not in comunidade.membros.all():
    #     messages.error(request, f"Você não é membro da comunidade '{comunidade.nome}' e não pode visualizar seu conteúdo.")
    #     return redirect('comunidades_lista') # Ou para a home

    # Filtra postagens pertencentes a esta comunidade
    posts = Postagem.objects.filter(comunidade=comunidade).order_by('-data_postagem')
    # Verifica se o usuário logado é membro
    is_member = request.user in comunidade.membros.all()
    # Verifica se o usuário logado é administrador
    is_admin = request.user in comunidade.administradores.all()

    context = {
        'comunidade': comunidade,
        'posts': posts,
        'is_member': is_member,
        'is_admin': is_admin,
    }
    return render(request, 'core/comunidade_detail.html', context)

@login_required
def juntar_comunidade_view(request, comunidade_id):
    comunidade = get_object_or_404(Comunidade, id=comunidade_id)
    if request.user not in comunidade.membros.all():
        comunidade.membros.add(request.user)
        messages.success(request, f'Você agora faz parte da comunidade "{comunidade.nome}".')
    else:
        messages.info(request, f'Você já é membro da comunidade "{comunidade.nome}".')
    return redirect('comunidade_detalhe', comunidade_id=comunidade.id)

@login_required
def sair_comunidade_view(request, comunidade_id):
    comunidade = get_object_or_404(Comunidade, id=comunidade_id)
    if request.user in comunidade.membros.all():
        # Impedir que administradores saiam se forem os únicos
        if request.user in comunidade.administradores.all() and comunidade.administradores.count() <= 1:
             messages.error(request, 'Você não pode sair desta comunidade pois é o único administrador.')
             return redirect('comunidade_detalhe', comunidade_id=comunidade.id)

        comunidade.membros.remove(request.user)
        # Remover também das administrações, se for o caso
        if request.user in comunidade.administradores.all():
            comunidade.administradores.remove(request.user)
        messages.success(request, f'Você saiu da comunidade "{comunidade.nome}".')
    else:
        messages.error(request, f'Você não é membro da comunidade "{comunidade.nome}".')
    return redirect('comunidades_lista')

@login_required
def criar_comunidade_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        if nome: # Validação mínima
            comunidade = Comunidade.objects.create(nome=nome, descricao=descricao)
            comunidade.membros.add(request.user) # O criador automaticamente entra
            comunidade.administradores.add(request.user) # O criador automaticamente vira admin
            messages.success(request, f'Comunidade "{comunidade.nome}" criada com sucesso.')
            return redirect('comunidade_detalhe', comunidade_id=comunidade.id)
        else:
            messages.error(request, 'Nome da comunidade é obrigatório.')

    return render(request, 'core/criar_comunidade.html')

@login_required
def comunidade_editar_view(request, comunidade_id):
    """Somente administradores podem editar uma comunidade."""
    comunidade = get_object_or_404(Comunidade, id=comunidade_id)

    if request.user not in comunidade.administradores.all():
        messages.error(request, "Você não tem permissão para editar esta comunidade.")
        return redirect('comunidade_detalhe', comunidade_id=comunidade.id)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        if nome:
            comunidade.nome = nome
            comunidade.descricao = descricao
            if 'foto_capa' in request.FILES:
                comunidade.foto_capa = request.FILES['foto_capa']
            comunidade.save()
            messages.success(request, 'Comunidade atualizada com sucesso.')
            return redirect('comunidade_detalhe', comunidade_id=comunidade.id)
        else:
            messages.error(request, 'Nome da comunidade é obrigatório.')

    context = {
        'comunidade': comunidade,
    }
    return render(request, 'core/comunidade_editar.html', context) # Template a ser criado


# --- Views para Mensagens ---

@login_required
def mensagens_lista_view(request):
    # Obter IDs dos usuários com quem o usuário logado trocou mensagens
    conversas_ids = Mensagem.objects.filter(
        models.Q(remetente=request.user) | models.Q(destinatario=request.user)
    ).values_list('remetente', 'destinatario')

    conversas_set = set()
    for ids in conversas_ids:
        conversas_set.add(ids[0]) # Adiciona remetente
        conversas_set.add(ids[1]) # Adiciona destinatario
    conversas_set.discard(request.user.id) # Remove o próprio ID

    conversas_usuarios = User.objects.filter(id__in=conversas_set)

    context = {
        'conversas_usuarios': conversas_usuarios,
    }
    return render(request, 'core/mensagens.html', context)

@login_required
def mensagens_conversa_view(request, destinatario_id):
    destinatario = get_object_or_404(Perfil.usuario, id=destinatario_id).perfil.usuario # Garante que é um User
    # Impedir conversa consigo mesmo
    if destinatario == request.user:
        messages.error(request, "Você não pode enviar mensagem para si mesmo.")
        return redirect('mensagens_lista')

    # Obter mensagens entre o usuário logado e o destinatário
    mensagens = Mensagem.objects.filter(
        (models.Q(remetente=request.user) & models.Q(destinatario=destinatario)) |
        (models.Q(remetente=destinatario) & models.Q(destinatario=request.user))
    ).order_by('data_envio')

    # Marcar mensagens recebidas como lidas
    Mensagem.objects.filter(destinatario=request.user, remetente=destinatario, lida=False).update(lida=True)

    context = {
        'destinatario': destinatario,
        'mensagens': mensagens,
    }
    return render(request, 'core/conversa.html', context)

@login_required
def enviar_mensagem_view(request, destinatario_id):
    destinatario = get_object_or_404(Perfil.usuario, id=destinatario_id).perfil.usuario # Garante que é um User
    # Impedir enviar mensagem para si mesmo
    if destinatario == request.user:
        messages.error(request, "Você não pode enviar mensagem para si mesmo.")
        return redirect('mensagens_lista')

    if request.method == 'POST':
        texto = request.POST.get('texto')
        if texto.strip(): # Validação mínima
            Mensagem.objects.create(remetente=request.user, destinatario=destinatario, texto=texto)
            messages.success(request, 'Mensagem enviada.')
        else:
            messages.error(request, 'Texto da mensagem não pode estar vazio.')
    # Redireciona de volta para a conversa
    return redirect('mensagens_conversa', destinatario_id=destinatario.id)

# --- Views para Relacionamentos ---

@login_required
def relacionamento_enviar_solicitacao_view(request, usuario_para_id):
    usuario_para = get_object_or_404(Perfil.usuario, id=usuario_para_id).perfil.usuario # Garante que é um User
    # Impedir solicitação para si mesmo
    if usuario_para == request.user:
        messages.error(request, 'Você não pode enviar uma solicitação para si mesmo.')
        return redirect('perfil', username=usuario_para.username)

    # Verifica se já existe alguma relação (ativa ou pendente)
    rel_existente = Relacionamento.objects.filter(
        models.Q(usuario_de=request.user, usuario_para=usuario_para) |
        models.Q(usuario_de=usuario_para, usuario_para=request.user)
    ).exists()

    if not rel_existente:
        # Envia uma solicitação de amizade
        Relacionamento.objects.create(
            usuario_de=request.user,
            usuario_para=usuario_para,
            tipo='solicitacao_amizade' # <-- Tipo correto
        )
        messages.success(request, f'Solicitação de amizade enviada para {usuario_para.username}.')
    else:
        messages.info(request, f'Já existe uma relação com {usuario_para.username}.')
    # Onde redirecionar? Talvez para o perfil do outro usuário?
    return redirect('perfil', username=usuario_para.username)

@login_required
def relacionamento_aceitar_recusar_view(request, relacionamento_id, acao):
    relacionamento = get_object_or_404(Relacionamento, id=relacionamento_id)
    # Só o destinatário da solicitação pode aceitar/recusar
    if relacionamento.usuario_para == request.user and relacionamento.tipo == 'solicitacao_amizade':
        if acao == 'aceitar':
            # Cria o relacionamento bilateral de amizade
            Relacionamento.objects.get_or_create(usuario_de=relacionamento.usuario_para, usuario_para=relacionamento.usuario_de, tipo='amigo')
            Relacionamento.objects.get_or_create(usuario_de=relacionamento.usuario_de, usuario_para=relacionamento.usuario_para, tipo='amigo')
            # Apaga a solicitação pendente
            relacionamento.delete()
            messages.success(request, f'Solicitação de amizade de {relacionamento.usuario_de.username} aceita.')
        elif acao == 'recusar':
            relacionamento.delete() # Apaga a solicitação pendente
            messages.info(request, f'Solicitação de amizade de {relacionamento.usuario_de.username} recusada.')
        else:
            messages.error(request, 'Ação inválida.')
    else:
         messages.error(request, 'Você não tem permissão para aceitar/recusar esta solicitação ou ela não é uma solicitação de amizade pendente.')
    # Onde redirecionar? Para a página de notificações?
    return redirect('notificacoes') # <-- Redireciona para a nova view de notificações

@login_required
def relacionamento_cancelar_view(request, usuario_para_id):
    usuario_para = get_object_or_404(Perfil.usuario, id=usuario_para_id).perfil.usuario # Garante que é um User
    # Impedir cancelar relação consigo mesmo
    if usuario_para == request.user:
        messages.error(request, "Você não pode cancelar uma relação com si mesmo.")
        return redirect('perfil', username=usuario_para.username)

    # Tenta deletar qualquer tipo de relacionamento existente
    Relacionamento.objects.filter(usuario_de=request.user, usuario_para=usuario_para).delete()
    Relacionamento.objects.filter(usuario_de=usuario_para, usuario_para=request.user).delete() # Remove relação reversa se for amigo
    messages.success(request, f'Relacionamento com {usuario_para.username} cancelado/removido.')
    # Onde redirecionar? Talvez para o perfil do outro usuário ou para a home?
    return redirect('perfil', username=usuario_para.username) # Ou redirect('home')


# --- Views para Explorar ---

@login_required
def explorar_view(request):
    # Exemplo: Postagens públicas (não associadas a comunidades privadas - vamos considerar todas como públicas por enquanto)
    postagens_publicas = Postagem.objects.filter(comunidade__isnull=True).order_by('-data_postagem')[:20] # Ultimas 20 postagens públicas
    # Exemplo: Comunidades populares
    comunidades_populares = Comunidade.objects.annotate(membros_count=models.Count('membros')).order_by('-membros_count')[:5]
    # Exemplo: Usuários com mais postagens
    usuarios_ativos = User.objects.annotate(postagens_count=models.Count('postagens')).order_by('-postagens_count')[:5]

    context = {
        'postagens_publicas': postagens_publicas,
        'comunidades_populares': comunidades_populares,
        'usuarios_ativos': usuarios_ativos,
    }
    return render(request, 'core/explorar.html', context)

# --- Views para Notificações ---

@login_required
def notificacoes_view(request):
    # Filtra os relacionamentos onde o usuário logado é o 'usuario_para' e o tipo é 'solicitacao_amizade'
    solicitacoes_pendentes = Relacionamento.objects.filter(
        usuario_para=request.user,
        tipo='solicitacao_amizade'
    ).select_related('usuario_de') # select_related otimiza a query para obter o nome do usuário que solicitou

    # Exemplo: você pode querer adicionar outras notificações aqui no futuro
    # Por enquanto, só as solicitações de amizade

    context = {
        'solicitacoes_pendentes': solicitacoes_pendentes,
    }
    return render(request, 'core/notificacoes.html', context)
