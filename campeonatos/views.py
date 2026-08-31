from django.shortcuts import redirect, render

from .forms import (
    CampeonatoForm,
    EstadioForm,
    InscricaoForm,
    JogadorTimeForm,
    PartidaForm,
    PessoaForm,
    TimeForm,
)

from .models import (
    Campeonato,
    Estadio,
    Inscricao,
    JogadorTime,
    Partida,
    Pessoa,
    Time,
)


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
# PESSOA
# =========================================================

def pessoa_listar(request):
    pessoas = Pessoa.objects.all()

    contexto = {
        "pessoas": pessoas,
    }

    return render(
        request,
        "campeonatos/pessoa_listar.html",
        contexto,
    )


def pessoa_criar(request):
    if request.method == "POST":
        form = PessoaForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect(
                "campeonatos:pessoa_listar"
            )

    else:
        form = PessoaForm()

    contexto = {
        "form": form,
        "titulo": "Cadastrar pessoa",
    }

    return render(
        request,
        "campeonatos/formulario.html",
        contexto,
    )


# =========================================================
# ESTÁDIO
# =========================================================

def estadio_listar(request):
    estadios = Estadio.objects.all()

    contexto = {
        "estadios": estadios,
    }

    return render(
        request,
        "campeonatos/estadio_listar.html",
        contexto,
    )


def estadio_criar(request):
    if request.method == "POST":
        form = EstadioForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect(
                "campeonatos:estadio_listar"
            )

    else:
        form = EstadioForm()

    contexto = {
        "form": form,
        "titulo": "Cadastrar estádio",
    }

    return render(
        request,
        "campeonatos/formulario.html",
        contexto,
    )


# =========================================================
# TIME
# =========================================================

def time_listar(request):
    times = Time.objects.all()

    contexto = {
        "times": times,
    }

    return render(
        request,
        "campeonatos/time_listar.html",
        contexto,
    )


def time_criar(request):
    if request.method == "POST":
        form = TimeForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "campeonatos:time_listar"
            )

    else:
        form = TimeForm()

    contexto = {
        "form": form,
        "titulo": "Cadastrar time",
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


# =========================================================
# ELENCO
# =========================================================

def elenco_listar(request):
    jogadores = JogadorTime.objects.all()

    contexto = {
        "jogadores": jogadores,
    }

    return render(
        request,
        "campeonatos/elenco_listar.html",
        contexto,
    )


def elenco_criar(request):
    if request.method == "POST":
        form = JogadorTimeForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect(
                "campeonatos:elenco_listar"
            )

    else:
        form = JogadorTimeForm()

    contexto = {
        "form": form,
        "titulo": "Adicionar jogador ao elenco",
    }

    return render(
        request,
        "campeonatos/formulario.html",
        contexto,
    )