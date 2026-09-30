from django.urls import path

from . import views


app_name = "campeonatos"


urlpatterns = [

    # AUTENTICAÇÃO

    path(
        "login/",
        views.entrar,
        name="login",
    ),

    path(
        "criar-conta/",
        views.criar_conta,
        name="criar_conta",
    ),

    path(
        "logout/",
        views.sair,
        name="logout",
    ),


    # INÍCIO

    path(
        "",
        views.inicio,
        name="inicio",
    ),


    # CAMPEONATOS

    path(
        "campeonatos/",
        views.campeonato_listar,
        name="campeonato_listar",
    ),

    path(
        "campeonatos/novo/",
        views.campeonato_criar,
        name="campeonato_criar",
    ),

    path(
        "campeonatos/<int:pk>/",
        views.campeonato_detalhar,
        name="campeonato_detalhar",
    ),

    path(
        "campeonatos/<int:pk>/editar/",
        views.campeonato_editar,
        name="campeonato_editar",
    ),

    path(
        "campeonatos/<int:pk>/excluir/",
        views.campeonato_excluir,
        name="campeonato_excluir",
    ),


    # PESSOAS

    path(
        "pessoas/",
        views.pessoa_listar,
        name="pessoa_listar",
    ),

    path(
        "pessoas/nova/",
        views.pessoa_criar,
        name="pessoa_criar",
    ),

    path(
        "pessoas/<int:pk>/",
        views.pessoa_detalhar,
        name="pessoa_detalhar",
    ),

    path(
        "pessoas/<int:pk>/editar/",
        views.pessoa_editar,
        name="pessoa_editar",
    ),

    path(
        "pessoas/<int:pk>/excluir/",
        views.pessoa_excluir,
        name="pessoa_excluir",
    ),


    # ESTÁDIOS

    path(
        "estadios/",
        views.estadio_listar,
        name="estadio_listar",
    ),

    path(
        "estadios/novo/",
        views.estadio_criar,
        name="estadio_criar",
    ),

    path(
        "estadios/<int:pk>/",
        views.estadio_detalhar,
        name="estadio_detalhar",
    ),

    path(
        "estadios/<int:pk>/editar/",
        views.estadio_editar,
        name="estadio_editar",
    ),

    path(
        "estadios/<int:pk>/excluir/",
        views.estadio_excluir,
        name="estadio_excluir",
    ),


    # TIMES

    path(
        "times/",
        views.time_listar,
        name="time_listar",
    ),

    path(
        "times/novo/",
        views.time_criar,
        name="time_criar",
    ),

    path(
        "times/<int:pk>/",
        views.time_detalhar,
        name="time_detalhar",
    ),

    path(
        "times/<int:pk>/editar/",
        views.time_editar,
        name="time_editar",
    ),

    path(
        "times/<int:pk>/excluir/",
        views.time_excluir,
        name="time_excluir",
    ),


    # INSCRIÇÕES

    path(
        "inscricoes/",
        views.inscricao_listar,
        name="inscricao_listar",
    ),

    path(
        "inscricoes/nova/",
        views.inscricao_criar,
        name="inscricao_criar",
    ),


    # PARTIDAS

    path(
        "partidas/",
        views.partida_listar,
        name="partida_listar",
    ),

    path(
        "partidas/nova/",
        views.partida_criar,
        name="partida_criar",
    ),

    path(
        "partidas/<int:pk>/",
        views.partida_detalhar,
        name="partida_detalhar",
    ),

    path(
        "partidas/<int:pk>/editar/",
        views.partida_editar,
        name="partida_editar",
    ),

    path(
        "partidas/<int:pk>/excluir/",
        views.partida_excluir,
        name="partida_excluir",
    ),


    # ELENCOS

    path(
        "elencos/",
        views.elenco_listar,
        name="elenco_listar",
    ),

    path(
        "elencos/novo/",
        views.elenco_criar,
        name="elenco_criar",
    ),
]