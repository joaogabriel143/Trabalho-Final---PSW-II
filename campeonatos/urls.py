from django.urls import path

from . import views


app_name = "campeonatos"


urlpatterns = [
    # Início
    path(
        "",
        views.inicio,
        name="inicio",
    ),

    # Campeonato
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

    # Pessoa
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

    # Estádio
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

    # Time
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

    # Inscrição
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

    # Partida
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

    # Elenco
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