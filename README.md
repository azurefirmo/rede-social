# Rede Social

Uma rede social desenvolvida com Django e Bootstrap como parte do desenvolvimento de um MVP (Produto Mínimo Viável).

## Funcionalidades

*   **Timeline:** Visualize postagens de amigos e comunidades.
*   **Comunidades:** Crie, junte-se e interaja em comunidades.
*   **Mensagens:** Envie mensagens individuais.
*   **Postagens:** Compartilhe textos, fotos, vídeos e URLs.
*   **Interações:** Curta e comente postagens.
*   **Relacionamentos:** Siga outros usuários e envie solicitações de amizade.
*   **Explorar:** Descubra novas postagens, usuários e comunidades.
*   **Perfil de Usuário:** Visualize e edite seu perfil.
*   **Notificações:** Veja solicitações de amizade pendentes.
*   **Responsividade:** Design adaptável para dispositivos móveis e web.

## Tecnologias Utilizadas

*   **Backend:** [Python](https://www.python.org/) 3.x, [Django](https://www.djangoproject.com/)
*   **Frontend:** [HTML5](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5), [CSS3](https://developer.mozilla.org/en-US/docs/Web/CSS), [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript), [Bootstrap](https://getbootstrap.com/)
*   **Banco de Dados:** SQLite (padrão para desenvolvimento Django)
*   **Servidor Web (Desenvolvimento):** Django Development Server (`runserver`)

## Como Executar Localmente

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/azurefirmo/rede-social.git
    cd rede-social
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    # No Linux/macOS
    python -m venv venv
    source venv/bin/activate

    # No Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Caso o arquivo `requirements.txt` ainda não exista, gere-o com `pip freeze > requirements.txt` após instalar o Django)*

4.  **Navegue até o diretório do projeto Django (onde está o `manage.py`):**
    ```bash
    cd rede-social
    ```

5.  **Execute as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

6.  **Crie um superusuário (opcional, mas útil para o admin):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

8.  **Abra seu navegador e acesse:** `http://127.0.0.1:8000/`

## Estrutura do Projeto

```bash
rede-social/
│
├── redesocial/ # Diretório do projeto Django
│ ├── init.py
│ ├── settings.py # Configurações do projeto
│ ├── urls.py # URLs principais do projeto
│ ├── wsgi.py # Configuração para servidores WSGI
│ └── asgi.py # Configuração para servidores ASGI (se aplicável)
├── core/ # App principal da rede social
│ ├── init.py
│ ├── admin.py # Configurações do painel administrativo
│ ├── apps.py # Configurações do app
│ ├── migrations/ # Migrações do banco de dados
│ │ └── ...
│ ├── models.py # Definição dos modelos de dados
│ ├── templates/ # Templates HTML
│ │ └── core/
│ │ ├── _base.html
│ │ ├── timeline.html
│ │ ├── index.html
│ │ ├── perfil.html
│ │ ├── ...
│ │ └── registration/
│ │ ├── login.html
│ │ └── registro.html
│ ├── views.py # Definição das views (lógica de negócio)
│ └── urls.py # URLs do app core
├── static/ # Arquivos estáticos (CSS, JS, imagens)
├── media/ # Arquivos de mídia (uploads de usuários)
├── manage.py # Script de utilidades do Django
└── requirements.txt # Dependências do projeto
```

## Status do Projeto

Este projeto está em fase de **MVP (Produto Mínimo Viável)**. A funcionalidade principal está implementada, mas ainda está em desenvolvimento e sujeita a alterações.

## Contribuição

Contribuições são bem-vindas! Por favor, abra uma *issue* para discutir possíveis melhorias ou envie um *pull request* com suas sugestões.
