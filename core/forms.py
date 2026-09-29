from django import forms
from .models import Postagem, Comentario

class PostagemForm(forms.ModelForm):
    class Meta:
        model = Postagem
        fields = ['tipo', 'conteudo_texto', 'conteudo_midia', 'url']
        widgets = {
            'conteudo_texto': forms.Textarea(attrs={'rows': 3, 'placeholder': 'O que você está pensando?'}),
            'conteudo_midia': forms.FileInput(attrs={'accept': 'image/*,video/*'}),
            'url': forms.URLInput(attrs={'placeholder': 'Cole o link aqui...'}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Adicione um comentário...', 'style': 'resize:none;'}),
        }