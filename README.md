# LigaHub

Sistema web para gerenciamento de campeonatos de futebol desenvolvido como Trabalho Final da disciplina de Programação de Sistemas Web II (PSW II), no Instituto Federal Baiano — Campus Guanambi.

O LigaHub foi desenvolvido com Django e utiliza o formato de campeonato por pontos corridos. O sistema permite gerenciar campeonatos, times, pessoas, estádios, partidas, inscrições e elencos, além de calcular automaticamente a classificação a partir dos resultados registrados.

## Autores

- João
- Sergio

## Tecnologias utilizadas

- Python
- Django
- SQLite
- Bootstrap
- HTML
- CSS
- Pillow

## Funcionalidades

- Criação de conta de usuário
- Login e logout
- Controle de acesso com `django.contrib.auth`
- Proteção de rotas com `login_required`
- Controle de permissões com `permission_required`
- Cadastro, listagem, detalhamento, edição e exclusão de campeonatos
- Cadastro, listagem, detalhamento, edição e exclusão de times
- Cadastro, listagem, detalhamento, edição e exclusão de pessoas
- Cadastro, listagem, detalhamento, edição e exclusão de estádios
- Cadastro, listagem, detalhamento, edição e exclusão de partidas
- Inscrição de times em campeonatos
- Gerenciamento de jogadores no elenco dos times
- Upload de escudos dos times
- Registro de resultados das partidas
- Classificação calculada automaticamente
- Mensagens de feedback ao usuário
- Interface responsiva com Bootstrap
- Navegação entre registros relacionados

## Regras da competição

O LigaHub trabalha com campeonatos no formato de pontos corridos.

Pontuação:

- Vitória: 3 pontos
- Empate: 1 ponto
- Derrota: 0 pontos

Critérios de desempate:

1. Pontos
2. Vitórias
3. Saldo de gols
4. Gols marcados

A classificação não é armazenada em um model próprio. Ela é calculada dinamicamente a partir das partidas que possuem placar registrado.

## CRUDs principais

Os cinco CRUDs completos do sistema são:

1. Campeonato
2. Time
3. Pessoa
4. Estádio
5. Partida

Cada um desses módulos possui operações de criação, leitura/listagem, visualização detalhada, edição e exclusão.

Os módulos de Inscrição e Elenco são utilizados como módulos auxiliares do sistema.

## Arquitetura

Todas as views da aplicação foram implementadas utilizando Function-Based Views (FBVs).

O projeto não utiliza Class-Based Views (CBVs).

## Estrutura principal do projeto

```text
ligahub/
├── campeonatos/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── ligahub/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── media/
├── manage.py
├── requirements.txt
├── diagrama_classes_ligahub.png
└── README.md
```

## Diagrama de Classes

O diagrama de classes utilizado na modelagem do sistema deve ser mantido no repositório com o nome:

```text
diagrama_classes_ligahub.png
```

> Se o arquivo do diagrama já estiver no repositório com outro nome, ele pode ser mantido, mas o nome acima facilita a identificação durante a avaliação.

## Pré-requisitos

Antes de executar o projeto, tenha instalado:

- Python 3.12 ou superior
- pip
- Git

## Como clonar o projeto

Clone o repositório:

```bash
git clone https://github.com/joaogabriel143/Trabalho-Final---PSW-II
```

Entre na pasta do projeto:

```bash
cd ligahub
```

> Substitua `https://github.com/joaogabriel143/Trabalho-Final---PSW-II` pelo endereço real do repositório do LigaHub no GitHub.

## Como criar e ativar o ambiente virtual

Crie o ambiente virtual:

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

## Como instalar as dependências

Com o ambiente virtual ativado, execute:

```bash
python -m pip install -r requirements.txt
```

## Como preparar o banco de dados

Execute as migrations:

```bash
python manage.py migrate
```

## Como criar o superusuário

Para acessar o Django Admin, crie um superusuário:

```bash
python manage.py createsuperuser
```

Informe o nome de usuário, e-mail (quando solicitado) e senha.

## Como executar o servidor

Execute:

```bash
python manage.py runserver
```

Depois acesse:

```text
http://127.0.0.1:8000/
```

O painel administrativo do Django fica disponível em:

```text
http://127.0.0.1:8000/admin/
```

## Autenticação e permissões

A página inicial do LigaHub é pública.

As áreas internas de gerenciamento exigem autenticação.

Os usuários criados pela página de cadastro do LigaHub recebem as permissões do aplicativo `campeonatos`, permitindo utilizar as funcionalidades administrativas disponibilizadas pela interface.

As ações de criação, edição e exclusão são protegidas por decorators de permissão.

## Pessoas, técnicos e jogadores

O model `Pessoa` é utilizado para representar pessoas relacionadas ao domínio do sistema, como técnicos e jogadores.

Esses registros herdam do `User` do Django, mas não são criados para realizar login no sistema. O username é gerado internamente e, quando aplicável, a senha é marcada como inutilizável.

## Times e escudos

Os times podem possuir uma imagem de escudo.

O projeto utiliza o Pillow para permitir o uso de `ImageField`.

Os arquivos enviados são armazenados na pasta de mídia configurada pelo Django.

## Classificação

A classificação é atualizada automaticamente com base nas partidas realizadas.

São exibidas informações como:

- Jogos
- Vitórias
- Empates
- Derrotas
- Gols pró
- Gols contra
- Saldo de gols
- Pontos

Isso evita duplicação de dados e mantém a classificação coerente com os resultados cadastrados.

## Banco de dados

O projeto utiliza SQLite no ambiente de desenvolvimento.

As tabelas são criadas por meio das migrations do Django.

## Verificação do projeto

Antes de iniciar o servidor, também é possível verificar a configuração do projeto com:

```bash
python manage.py check
```

O resultado esperado é semelhante a:

```text
System check identified no issues (0 silenced).
```

## Observação sobre o GitHub

O projeto foi desenvolvido em dupla em um único repositório, utilizando commits, branches, Pull Requests e revisões para registrar a participação dos integrantes.

## Disciplina

Programação de Sistemas Web II — PSW II  
Instituto Federal Baiano — Campus Guanambi
