from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    biografia = models.TextField(max_length=500, blank=True)
    foto_perfil = models.ImageField(upload_to='perfis/', blank=True, null=True)
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class Comunidade(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    membros = models.ManyToManyField(User, related_name='comunidades_membro')
    administradores = models.ManyToManyField(User, related_name='comunidades_admin')
    foto_capa = models.ImageField(upload_to='comunidades/', blank=True, null=True)
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nome

class Postagem(models.Model):
    TIPO_CHOICES = [
        ('texto', 'Texto'),
        ('foto', 'Foto'),
        ('video', 'Vídeo'),
        ('url', 'URL'),
    ]

    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postagens')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='texto')
    conteudo_texto = models.TextField(blank=True) # Para postagens de texto
    conteudo_midia = models.FileField(upload_to='postagens/', blank=True, null=True) # Foto ou Vídeo
    url = models.URLField(blank=True, null=True) # Para postagens de URL
    comunidade = models.ForeignKey(Comunidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='postagens') # Opcional
    data_postagem = models.DateTimeField(default=timezone.now)
    curtidas = models.ManyToManyField(User, related_name='postagens_curtidas', blank=True)
    comentarios_ativos = models.BooleanField(default=True)

    class Meta:
        ordering = ['-data_postagem']

    def __str__(self):
        return f"Postagem de {self.autor.username} em {self.data_postagem.strftime('%d/%m/%Y %H:%M')}"

class Comentario(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    postagem = models.ForeignKey(Postagem, on_delete=models.CASCADE, related_name='comentarios')
    texto = models.TextField()
    data_comentario = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['data_comentario']

    def __str__(self):
        return f'Comentário de {self.autor.username} em {self.postagem.id}'

class Mensagem(models.Model):
    remetente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens_recebidas')
    texto = models.TextField()
    data_envio = models.DateTimeField(default=timezone.now)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ['data_envio']

    def __str__(self):
        return f'Mensagem de {self.remetente.username} para {self.destinatario.username}'

class Relacionamento(models.Model):
    DE_TIPO_CHOICES = [
        ('amigo', 'Amigo'), # Amizade ativa (bilateral implícita ou unilateral)
        ('seguidor', 'Seguidor'), # Seguir unilateral
        ('solicitacao_amizade', 'Solicitação de Amizade'), # Nova opção
    ]
    usuario_de = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relacionamentos_de')
    usuario_para = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relacionamentos_para')
    tipo = models.CharField(max_length=20, choices=DE_TIPO_CHOICES) # Aumentei o max_length para acomodar o novo tipo
    data_inicio = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('usuario_de', 'usuario_para')

    def __str__(self):
        return f"{self.usuario_de.username} é {self.tipo} de {self.usuario_para.username}"