from django.urls import path

from . import views


app_name = "campeonatos"


urlpatterns = [
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
]