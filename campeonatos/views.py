from django.contrib import messages

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

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

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

            messages.success(
                request,
                "Login realizado com sucesso.",
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

            messages.success(
                request,
                (
                    "Conta criada com sucesso. "
                    "Faça login para continuar."
                ),
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

    messages.info(
        request,
        "Você saiu da sua conta.",
    )

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
def campeonato_detalhar(request, pk):

    campeonato = get_object_or_404(
        Campeonato,
        pk=pk,
    )

    inscricoes = (
        campeonato
        .inscricoes
        .select_related(
            "time",
            "time__tecnico",
        )
        .all()
    )

    partidas = (
        campeonato
        .partidas
        .select_related(
            "time_mandante",
            "time_visitante",
            "estadio",
        )
        .order_by(
            "rodada",
            "data",
            "horario",
        )
    )

    partidas_realizadas = partidas.filter(
        gols_mandante__isnull=False,
        gols_visitante__isnull=False,
    ).count()

    contexto = {
        "campeonato": campeonato,
        "inscricoes": inscricoes,
        "partidas": partidas,
        "partidas_realizadas": partidas_realizadas,
    }

    return render(
        request,
        "campeonatos/campeonato_detalhar.html",
        contexto,
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

            campeonato = form.save()

            messages.success(
                request,
                (
                    f'Campeonato "{campeonato.nome}" '
                    "cadastrado com sucesso."
                ),
            )

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
def pessoa_detalhar(request, pk):

    pessoa = get_object_or_404(
        Pessoa,
        pk=pk,
    )

    times_como_tecnico = (
        pessoa
        .times_como_tecnico
        .all()
    )

    vinculos_como_jogador = (
        pessoa
        .times_como_jogador
        .select_related(
            "time"
        )
        .order_by(
            "-temporada",
            "time__nome",
        )
    )

    contexto = {
        "pessoa": pessoa,
        "times_como_tecnico": times_como_tecnico,
        "vinculos_como_jogador": vinculos_como_jogador,
    }

    return render(
        request,
        "campeonatos/pessoa_detalhar.html",
        contexto,
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

            pessoa = form.save()

            messages.success(
                request,
                (
                    f'Pessoa "{pessoa.nome}" '
                    "cadastrada com sucesso."
                ),
            )

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
def estadio_detalhar(request, pk):

    estadio = get_object_or_404(
        Estadio,
        pk=pk,
    )

    partidas = (
        estadio
        .partidas
        .select_related(
            "campeonato",
            "time_mandante",
            "time_visitante",
        )
        .order_by(
            "-data",
            "-horario",
        )
    )

    contexto = {
        "estadio": estadio,
        "partidas": partidas,
    }

    return render(
        request,
        "campeonatos/estadio_detalhar.html",
        contexto,
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

            estadio = form.save()

            messages.success(
                request,
                (
                    f'Estádio "{estadio.nome}" '
                    "cadastrado com sucesso."
                ),
            )

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
def time_detalhar(request, pk):

    time = get_object_or_404(
        Time.objects.select_related(
            "tecnico"
        ),
        pk=pk,
    )

    elenco = (
        time
        .jogadores_time
        .select_related(
            "jogador"
        )
        .order_by(
            "-temporada",
            "numero_camisa",
        )
    )

    inscricoes = (
        time
        .inscricoes
        .select_related(
            "campeonato"
        )
        .order_by(
            "-campeonato__temporada",
            "campeonato__nome",
        )
    )

    contexto = {
        "time": time,
        "elenco": elenco,
        "inscricoes": inscricoes,
    }

    return render(
        request,
        "campeonatos/time_detalhar.html",
        contexto,
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

            time = form.save()

            messages.success(
                request,
                (
                    f'Time "{time.nome}" '
                    "cadastrado com sucesso."
                ),
            )

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

            messages.success(
                request,
                (
                    "Time inscrito no campeonato "
                    "com sucesso."
                ),
            )

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
def partida_detalhar(request, pk):

    partida = get_object_or_404(
        Partida.objects.select_related(
            "campeonato",
            "time_mandante",
            "time_visitante",
            "estadio",
        ),
        pk=pk,
    )

    contexto = {
        "partida": partida,
    }

    return render(
        request,
        "campeonatos/partida_detalhar.html",
        contexto,
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

            messages.success(
                request,
                "Partida cadastrada com sucesso.",
            )

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

            vinculo = form.save()

            messages.success(
                request,
                (
                    f'"{vinculo.jogador.nome}" '
                    "adicionado ao elenco com sucesso."
                ),
            )

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