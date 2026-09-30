from django.contrib import messages
from django.db.models import Prefetch

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

from django.db.models.deletion import ProtectedError

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from django.urls import reverse

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
# CLASSIFICAÇÃO
# =========================================================

def calcular_classificacao(campeonato):

    inscricoes = (
        campeonato
        .inscricoes
        .select_related("time")
        .all()
    )

    tabela = {}

    for inscricao in inscricoes:

        time = inscricao.time

        tabela[time.pk] = {
            "time": time,
            "jogos": 0,
            "vitorias": 0,
            "empates": 0,
            "derrotas": 0,
            "gols_pro": 0,
            "gols_contra": 0,
            "saldo_gols": 0,
            "pontos": 0,
        }

    partidas = (
        campeonato
        .partidas
        .filter(
            gols_mandante__isnull=False,
            gols_visitante__isnull=False,
        )
        .select_related(
            "time_mandante",
            "time_visitante",
        )
    )

    for partida in partidas:

        mandante = tabela.get(
            partida.time_mandante_id
        )

        visitante = tabela.get(
            partida.time_visitante_id
        )

        if not mandante or not visitante:
            continue

        gols_mandante = partida.gols_mandante
        gols_visitante = partida.gols_visitante

        mandante["jogos"] += 1
        visitante["jogos"] += 1

        mandante["gols_pro"] += gols_mandante
        mandante["gols_contra"] += gols_visitante

        visitante["gols_pro"] += gols_visitante
        visitante["gols_contra"] += gols_mandante

        if gols_mandante > gols_visitante:

            mandante["vitorias"] += 1
            mandante["pontos"] += 3

            visitante["derrotas"] += 1

        elif gols_visitante > gols_mandante:

            visitante["vitorias"] += 1
            visitante["pontos"] += 3

            mandante["derrotas"] += 1

        else:

            mandante["empates"] += 1
            visitante["empates"] += 1

            mandante["pontos"] += 1
            visitante["pontos"] += 1

    classificacao = list(
        tabela.values()
    )

    for item in classificacao:

        item["saldo_gols"] = (
            item["gols_pro"]
            - item["gols_contra"]
        )

    classificacao.sort(
        key=lambda item: (
            -item["pontos"],
            -item["vitorias"],
            -item["saldo_gols"],
            -item["gols_pro"],
            item["time"].nome.lower(),
        )
    )

    for posicao, item in enumerate(
        classificacao,
        start=1,
    ):
        item["posicao"] = posicao

    return classificacao


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

    classificacao = calcular_classificacao(
        campeonato
    )

    contexto = {
        "campeonato": campeonato,
        "inscricoes": inscricoes,
        "partidas": partidas,
        "partidas_realizadas": partidas_realizadas,
        "classificacao": classificacao,
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


@login_required
@permission_required(
    "campeonatos.change_campeonato",
    raise_exception=True,
)
def campeonato_editar(request, pk):

    campeonato = get_object_or_404(
        Campeonato,
        pk=pk,
    )

    if request.method == "POST":

        form = CampeonatoForm(
            request.POST,
            instance=campeonato,
        )

        if form.is_valid():

            campeonato = form.save()

            messages.success(
                request,
                "Campeonato atualizado com sucesso.",
            )

            return redirect(
                "campeonatos:campeonato_detalhar",
                pk=campeonato.pk,
            )

    else:

        form = CampeonatoForm(
            instance=campeonato
        )

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Editar campeonato",
        },
    )


@login_required
@permission_required(
    "campeonatos.delete_campeonato",
    raise_exception=True,
)
def campeonato_excluir(request, pk):

    campeonato = get_object_or_404(
        Campeonato,
        pk=pk,
    )

    if request.method == "POST":

        nome = str(campeonato)

        campeonato.delete()

        messages.success(
            request,
            f'Campeonato "{nome}" excluído com sucesso.',
        )

        return redirect(
            "campeonatos:campeonato_listar"
        )

    return render(
        request,
        "campeonatos/confirmar_exclusao.html",
        {
            "titulo": "Excluir campeonato",
            "objeto": campeonato,
            "aviso": (
                "As inscrições e partidas deste campeonato "
                "também serão removidas."
            ),
            "url_cancelar": reverse(
                "campeonatos:campeonato_detalhar",
                args=[campeonato.pk],
            ),
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
        .select_related("time")
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


@login_required
@permission_required(
    "campeonatos.change_pessoa",
    raise_exception=True,
)
def pessoa_editar(request, pk):

    pessoa = get_object_or_404(
        Pessoa,
        pk=pk,
    )

    if request.method == "POST":

        form = PessoaForm(
            request.POST,
            instance=pessoa,
        )

        if form.is_valid():

            pessoa = form.save()

            messages.success(
                request,
                "Pessoa atualizada com sucesso.",
            )

            return redirect(
                "campeonatos:pessoa_detalhar",
                pk=pessoa.pk,
            )

    else:

        form = PessoaForm(
            instance=pessoa
        )

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Editar pessoa",
        },
    )


@login_required
@permission_required(
    "campeonatos.delete_pessoa",
    raise_exception=True,
)
def pessoa_excluir(request, pk):

    pessoa = get_object_or_404(
        Pessoa,
        pk=pk,
    )

    if request.method == "POST":

        nome = pessoa.nome

        try:

            pessoa.delete()

            messages.success(
                request,
                f'Pessoa "{nome}" excluída com sucesso.',
            )

            return redirect(
                "campeonatos:pessoa_listar"
            )

        except ProtectedError:

            messages.error(
                request,
                (
                    "Não é possível excluir esta pessoa "
                    "porque ela está cadastrada como técnico "
                    "de um time."
                ),
            )

            return redirect(
                "campeonatos:pessoa_detalhar",
                pk=pessoa.pk,
            )

    return render(
        request,
        "campeonatos/confirmar_exclusao.html",
        {
            "titulo": "Excluir pessoa",
            "objeto": pessoa,
            "aviso": (
                "Vínculos desta pessoa como jogador "
                "também poderão ser removidos."
            ),
            "url_cancelar": reverse(
                "campeonatos:pessoa_detalhar",
                args=[pessoa.pk],
            ),
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


@login_required
@permission_required(
    "campeonatos.change_estadio",
    raise_exception=True,
)
def estadio_editar(request, pk):

    estadio = get_object_or_404(
        Estadio,
        pk=pk,
    )

    if request.method == "POST":

        form = EstadioForm(
            request.POST,
            instance=estadio,
        )

        if form.is_valid():

            estadio = form.save()

            messages.success(
                request,
                "Estádio atualizado com sucesso.",
            )

            return redirect(
                "campeonatos:estadio_detalhar",
                pk=estadio.pk,
            )

    else:

        form = EstadioForm(
            instance=estadio
        )

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Editar estádio",
        },
    )


@login_required
@permission_required(
    "campeonatos.delete_estadio",
    raise_exception=True,
)
def estadio_excluir(request, pk):

    estadio = get_object_or_404(
        Estadio,
        pk=pk,
    )

    if request.method == "POST":

        nome = estadio.nome

        try:

            estadio.delete()

            messages.success(
                request,
                f'Estádio "{nome}" excluído com sucesso.',
            )

            return redirect(
                "campeonatos:estadio_listar"
            )

        except ProtectedError:

            messages.error(
                request,
                (
                    "Não é possível excluir este estádio "
                    "porque existem partidas vinculadas a ele."
                ),
            )

            return redirect(
                "campeonatos:estadio_detalhar",
                pk=estadio.pk,
            )

    return render(
        request,
        "campeonatos/confirmar_exclusao.html",
        {
            "titulo": "Excluir estádio",
            "objeto": estadio,
            "aviso": (
                "A exclusão não será permitida se houver "
                "partidas utilizando este estádio."
            ),
            "url_cancelar": reverse(
                "campeonatos:estadio_detalhar",
                args=[estadio.pk],
            ),
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
        .select_related("jogador")
        .order_by(
            "-temporada",
            "numero_camisa",
        )
    )

    inscricoes = (
        time
        .inscricoes
        .select_related("campeonato")
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


@login_required
@permission_required(
    "campeonatos.change_time",
    raise_exception=True,
)
def time_editar(request, pk):

    time = get_object_or_404(
        Time,
        pk=pk,
    )

    if request.method == "POST":

        form = TimeForm(
            request.POST,
            request.FILES,
            instance=time,
        )

        if form.is_valid():

            time = form.save()

            messages.success(
                request,
                "Time atualizado com sucesso.",
            )

            return redirect(
                "campeonatos:time_detalhar",
                pk=time.pk,
            )

    else:

        form = TimeForm(
            instance=time
        )

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Editar time",
        },
    )


@login_required
@permission_required(
    "campeonatos.delete_time",
    raise_exception=True,
)
def time_excluir(request, pk):

    time = get_object_or_404(
        Time,
        pk=pk,
    )

    if request.method == "POST":

        nome = time.nome

        try:

            time.delete()

            messages.success(
                request,
                f'Time "{nome}" excluído com sucesso.',
            )

            return redirect(
                "campeonatos:time_listar"
            )

        except ProtectedError:

            messages.error(
                request,
                (
                    "Não é possível excluir este time "
                    "porque existem partidas vinculadas a ele."
                ),
            )

            return redirect(
                "campeonatos:time_detalhar",
                pk=time.pk,
            )

    return render(
        request,
        "campeonatos/confirmar_exclusao.html",
        {
            "titulo": "Excluir time",
            "objeto": time,
            "aviso": (
                "Inscrições e vínculos de elenco poderão "
                "ser removidos. Times utilizados em partidas "
                "não podem ser excluídos."
            ),
            "url_cancelar": reverse(
                "campeonatos:time_detalhar",
                args=[time.pk],
            ),
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
                "Time inscrito no campeonato com sucesso.",
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

    return render(
        request,
        "campeonatos/partida_detalhar.html",
        {
            "partida": partida,
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


@login_required
@permission_required(
    "campeonatos.change_partida",
    raise_exception=True,
)
def partida_editar(request, pk):

    partida = get_object_or_404(
        Partida,
        pk=pk,
    )

    if request.method == "POST":

        form = PartidaForm(
            request.POST,
            instance=partida,
        )

        if form.is_valid():

            partida = form.save()

            messages.success(
                request,
                "Partida atualizada com sucesso.",
            )

            return redirect(
                "campeonatos:partida_detalhar",
                pk=partida.pk,
            )

    else:

        form = PartidaForm(
            instance=partida
        )

    return render(
        request,
        "campeonatos/formulario.html",
        {
            "form": form,
            "titulo": "Editar partida",
        },
    )


@login_required
@permission_required(
    "campeonatos.delete_partida",
    raise_exception=True,
)
def partida_excluir(request, pk):

    partida = get_object_or_404(
        Partida,
        pk=pk,
    )

    if request.method == "POST":

        partida.delete()

        messages.success(
            request,
            "Partida excluída com sucesso.",
        )

        return redirect(
            "campeonatos:partida_listar"
        )

    return render(
        request,
        "campeonatos/confirmar_exclusao.html",
        {
            "titulo": "Excluir partida",
            "objeto": partida,
            "aviso": (
                "Esta ação removerá definitivamente "
                "a partida e seu resultado."
            ),
            "url_cancelar": reverse(
                "campeonatos:partida_detalhar",
                args=[partida.pk],
            ),
        },
    )


# =========================================================
# ELENCOS
# =========================================================

@login_required
def elenco_listar(request):

    jogadores_ordenados = (
        JogadorTime.objects
        .select_related("jogador")
        .order_by(
            "-temporada",
            "numero_camisa",
            "jogador__nome",
        )
    )

    times = (
        Time.objects
        .select_related("tecnico")
        .prefetch_related(
            Prefetch(
                "jogadores_time",
                queryset=jogadores_ordenados,
                to_attr="elenco_ordenado",
            )
        )
        .order_by("nome")
    )

    return render(
        request,
        "campeonatos/elenco_listar.html",
        {
            "times": times,
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