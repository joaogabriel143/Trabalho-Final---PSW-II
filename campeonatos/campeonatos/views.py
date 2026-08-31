from django.shortcuts import redirect, render

from .forms import CampeonatoForm, InscricaoForm, PartidaForm
from .models import Campeonato, Inscricao, Partida


# =========================================================
# INÍCIO
# =========================================================

def inicio(request):
    return render(
        request,
        "campeonatos/inicio.html",
    )


# =========================================================
# CAMPEONATO
# =========================================================

def campeonato_listar(request):
    campeonatos = Campeonato.objects.all()

    contexto = {
        "campeonatos": campeonatos,
    }

    return render(
        request,
        "campeonatos/campeonato_listar.html",
        contexto,
    )


def campeonato_criar(request):
    if request.method == "POST":
        form = CampeonatoForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect(
                "campeonatos:campeonato_listar"
            )

    else:
        form = CampeonatoForm()

    contexto = {
        "form": form,
        "titulo": "Cadastrar campeonato",
    }

    return render(
        request,
        "campeonatos/formulario.html",
        contexto,
    )


# =========================================================
# INSCRIÇÃO
# =========================================================

def inscricao_listar(request):
    inscricoes = Inscricao.objects.all()

    contexto = {
        "inscricoes": inscricoes,
    }

    return render(
        request,
        "campeonatos/inscricao_listar.html",
        contexto,
    )


def inscricao_criar(request):
    if request.method == "POST":
        form = InscricaoForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect(
                "campeonatos:inscricao_listar"
            )

    else:
        form = InscricaoForm()

    contexto = {
        "form": form,
        "titulo": "Inscrever time",
    }

    return render(
        request,
        "campeonatos/formulario.html",
        contexto,
    )


# =========================================================
# PARTIDA
# =========================================================

def partida_listar(request):
    partidas = Partida.objects.all()

    contexto = {
        "partidas": partidas,
    }

    return render(
        request,
        "campeonatos/partida_listar.html",
        contexto,
    )


def partida_criar(request):
    if request.method == "POST":
        form = PartidaForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect(
                "campeonatos:partida_listar"
            )

    else:
        form = PartidaForm()

    contexto = {
        "form": form,
        "titulo": "Cadastrar partida",
    }

    return render(
        request,
        "campeonatos/formulario.html",
        contexto,
    )