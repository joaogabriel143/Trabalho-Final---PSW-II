from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)

from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)

from django.contrib.auth.models import Permission

from django.shortcuts import redirect, render

from django.utils.http import (
    url_has_allowed_host_and_scheme,
)

from django.views.decorators.http import require_POST


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
# AUTENTICAÇÃO
# =========================================================

def entrar(request):

    if request.user.is_authenticated:
        return redirect(
            "campeonatos:inicio"
        )

    next_url = request.GET.get(
        "next",
        "",
    )

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST,
        )

        next_url = request.POST.get(
            "next",
            "",
        )

        if form.is_valid():

            usuario = form.get_user()

            auth_login(
                request,
                usuario,
            )

            if (
                next_url
                and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={
                        request.get_host()
                    },
                    require_https=request.is_secure(),
                )
            ):

                return redirect(
                    next_url
                )

            return redirect(
                "campeonatos:inicio"
            )

    else:

        form = AuthenticationForm(
            request
        )

    contexto = {
        "form": form,
        "next": next_url,
    }

    return render(
        request,
        "campeonatos/login.html",
        contexto,
    )


def criar_conta(request):

    if request.user.is_authenticated:

        return redirect(
            "campeonatos:inicio"
        )

    if request.method == "POST":

        form = UserCreationForm(
            request.POST
        )

        if form.is_valid():

            usuario = form.save()

            # Todo usuário que cria uma conta no LigaHub
            # poderá gerenciar os dados do sistema.
            permissoes = Permission.objects.filter(
                content_type__app_label="campeonatos"
            )

            usuario.user_permissions.add(
                *permissoes
            )

            return redirect(
                "campeonatos:login"
            )

    else:

        form = UserCreationForm()

    return render(
        request,
        "campeonatos/criar_conta.html",
        {
            "form": form,
        },
    )


@login_required
@require_POST
def sair(request):

    auth_logout(request)

    return redirect(
        "campeonatos:inicio"
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
# CAMPEONATOS
# =========================================================

@login_required
def campeonato_listar(request):

    campeonatos = Campeonato.objects.all()

    return render(
        request,
        "campeonatos/campeonato_listar.html",
        {
            "campeonatos": campeonatos,
        },
    )


@login_required
@permission_required(
    "campeonatos.add_campeonato",
    raise_exception=True,
)
def campeonato_criar(request):

    if request.method == "POST":

        form = CampeonatoForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "campeonatos:campeonato_listar"
            )

    else:

        form = CampeonatoForm()

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Novo campeonato",
        },
    )


# =========================================================
# PESSOAS
# =========================================================

@login_required
def pessoa_listar(request):

    pessoas = Pessoa.objects.all()

    return render(
        request,
        "campeonatos/pessoa_listar.html",
        {
            "pessoas": pessoas,
        },
    )


@login_required
@permission_required(
    "campeonatos.add_pessoa",
    raise_exception=True,
)
def pessoa_criar(request):

    if request.method == "POST":

        form = PessoaForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "campeonatos:pessoa_listar"
            )

    else:

        form = PessoaForm()

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Nova pessoa",
        },
    )


# =========================================================
# ESTÁDIOS
# =========================================================

@login_required
def estadio_listar(request):

    estadios = Estadio.objects.all()

    return render(
        request,
        "campeonatos/estadio_listar.html",
        {
            "estadios": estadios,
        },
    )


@login_required
@permission_required(
    "campeonatos.add_estadio",
    raise_exception=True,
)
def estadio_criar(request):

    if request.method == "POST":

        form = EstadioForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "campeonatos:estadio_listar"
            )

    else:

        form = EstadioForm()

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Novo estádio",
        },
    )


# =========================================================
# TIMES
# =========================================================

@login_required
def time_listar(request):

    times = Time.objects.all()

    return render(
        request,
        "campeonatos/time_listar.html",
        {
            "times": times,
        },
    )


@login_required
@permission_required(
    "campeonatos.add_time",
    raise_exception=True,
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

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Novo time",
        },
    )


# =========================================================
# INSCRIÇÕES
# =========================================================

@login_required
def inscricao_listar(request):

    inscricoes = Inscricao.objects.all()

    return render(
        request,
        "campeonatos/inscricao_listar.html",
        {
            "inscricoes": inscricoes,
        },
    )


@login_required
@permission_required(
    "campeonatos.add_inscricao",
    raise_exception=True,
)
def inscricao_criar(request):

    if request.method == "POST":

        form = InscricaoForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "campeonatos:inscricao_listar"
            )

    else:

        form = InscricaoForm()

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Nova inscrição",
        },
    )


# =========================================================
# PARTIDAS
# =========================================================

@login_required
def partida_listar(request):

    partidas = Partida.objects.all()

    return render(
        request,
        "campeonatos/partida_listar.html",
        {
            "partidas": partidas,
        },
    )


@login_required
@permission_required(
    "campeonatos.add_partida",
    raise_exception=True,
)
def partida_criar(request):

    if request.method == "POST":

        form = PartidaForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "campeonatos:partida_listar"
            )

    else:

        form = PartidaForm()

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Nova partida",
        },
    )


# =========================================================
# ELENCOS
# =========================================================

@login_required
def elenco_listar(request):

    jogadores = JogadorTime.objects.all()

    return render(
        request,
        "campeonatos/elenco_listar.html",
        {
            "jogadores": jogadores,
        },
    )


@login_required
@permission_required(
    "campeonatos.add_jogadortime",
    raise_exception=True,
)
def elenco_criar(request):

    if request.method == "POST":

        form = JogadorTimeForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "campeonatos:elenco_listar"
            )

    else:

        form = JogadorTimeForm()

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": (
                "Adicionar jogador ao elenco"
            ),
        },
    )