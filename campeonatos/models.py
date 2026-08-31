from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


# =========================================================
# PESSOA
# =========================================================

class Pessoa(models.Model):
    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField()

    def clean(self):
        super().clean()

        if (
            self.data_nascimento
            and self.data_nascimento > timezone.localdate()
        ):
            raise ValidationError({
                "data_nascimento": (
                    "A data de nascimento não pode estar no futuro."
                )
            })

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"
        ordering = ["nome"]


# =========================================================
# CAMPEONATO
# =========================================================

class Campeonato(models.Model):
    nome = models.CharField(max_length=150)
    temporada = models.IntegerField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    descricao = models.TextField()
    ativo = models.BooleanField(default=True)

    def clean(self):
        super().clean()

        erros = {}

        # Temporada precisa ser válida.
        if self.temporada is not None and self.temporada <= 0:
            erros["temporada"] = (
                "Informe uma temporada válida."
            )

        # Campeonato não pode terminar antes de começar.
        if (
            self.data_inicio
            and self.data_fim
            and self.data_fim < self.data_inicio
        ):
            erros["data_fim"] = (
                "A data final não pode ser anterior à data inicial."
            )

        # Se o campeonato já possui partidas, suas datas
        # não podem ser alteradas de modo que alguma partida
        # fique fora do novo período.
        if (
            self.pk
            and self.data_inicio
            and self.data_fim
        ):
            partida_fora_do_periodo = self.partidas.filter(
                Q(data__lt=self.data_inicio)
                | Q(data__gt=self.data_fim)
            ).exists()

            if partida_fora_do_periodo:
                erros["data_inicio"] = (
                    "Existem partidas cadastradas fora do novo "
                    "período informado para o campeonato."
                )

        # A nova data de início também não pode tornar
        # inscrições existentes inválidas.
        if self.pk and self.data_inicio:
            inscricao_invalida = self.inscricoes.filter(
                data_inscricao__gt=self.data_inicio
            ).exists()

            if inscricao_invalida:
                erros["data_inicio"] = (
                    "Existem inscrições realizadas depois da nova "
                    "data de início informada."
                )

        if erros:
            raise ValidationError(erros)

    def quantidade_times(self):
        return self.inscricoes.count()

    def partidas_por_rodada(self):
        quantidade = self.quantidade_times()

        if quantidade >= 2 and quantidade % 2 == 0:
            return quantidade // 2

        return 0

    def total_rodadas_previstas(self):
        quantidade = self.quantidade_times()

        if quantidade >= 2:
            return 2 * (quantidade - 1)

        return 0

    def total_partidas_previstas(self):
        quantidade = self.quantidade_times()

        if quantidade >= 2:
            return quantidade * (quantidade - 1)

        return 0

    def __str__(self):
        return f"{self.nome} - {self.temporada}"

    class Meta:
        verbose_name = "Campeonato"
        verbose_name_plural = "Campeonatos"
        ordering = ["-temporada", "nome"]

        constraints = [
            models.UniqueConstraint(
                fields=["nome", "temporada"],
                name="unique_campeonato_temporada",
            )
        ]


# =========================================================
# ESTÁDIO
# =========================================================

class Estadio(models.Model):
    nome = models.CharField(max_length=150)
    cidade = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255)
    capacidade = models.PositiveIntegerField()

    def clean(self):
        super().clean()

        if (
            self.capacidade is not None
            and self.capacidade <= 0
        ):
            raise ValidationError({
                "capacidade": (
                    "A capacidade do estádio deve ser maior que zero."
                )
            })

    def __str__(self):
        return f"{self.nome} - {self.cidade}"

    class Meta:
        verbose_name = "Estádio"
        verbose_name_plural = "Estádios"
        ordering = ["nome"]


# =========================================================
# TIME
# =========================================================

class Time(models.Model):
    nome = models.CharField(max_length=150)
    cidade = models.CharField(max_length=100)

    tecnico = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        related_name="times_como_tecnico",
    )

    escudo = models.ImageField(
        upload_to="escudos/"
    )

    ano_fundacao = models.IntegerField()

    def clean(self):
        super().clean()

        erros = {}

        # Ano de fundação.
        if self.ano_fundacao is not None:
            if self.ano_fundacao <= 0:
                erros["ano_fundacao"] = (
                    "Informe um ano de fundação válido."
                )

            elif self.ano_fundacao > timezone.localdate().year:
                erros["ano_fundacao"] = (
                    "O ano de fundação não pode estar no futuro."
                )

        # Se o time já participa de campeonatos, ao trocar
        # o técnico verificamos se ele já comanda outro time
        # em algum desses mesmos campeonatos.
        if self.pk and self.tecnico_id:
            campeonatos_do_time = self.inscricoes.values_list(
                "campeonato_id",
                flat=True,
            )

            conflito = Inscricao.objects.filter(
                campeonato_id__in=campeonatos_do_time,
                time__tecnico_id=self.tecnico_id,
            ).exclude(
                time_id=self.pk,
            )

            if conflito.exists():
                inscricao_conflitante = conflito.first()

                erros["tecnico"] = (
                    f"{self.tecnico.nome} já comanda o time "
                    f"{inscricao_conflitante.time.nome} no campeonato "
                    f"{inscricao_conflitante.campeonato}."
                )

        if erros:
            raise ValidationError(erros)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Time"
        verbose_name_plural = "Times"
        ordering = ["nome"]


# =========================================================
# INSCRIÇÃO
# =========================================================

class Inscricao(models.Model):
    data_inscricao = models.DateField()

    campeonato = models.ForeignKey(
        Campeonato,
        on_delete=models.CASCADE,
        related_name="inscricoes",
    )

    time = models.ForeignKey(
        Time,
        on_delete=models.CASCADE,
        related_name="inscricoes",
    )

    def clean(self):
        super().clean()

        erros = {}

        # -------------------------------------------------
        # Data da inscrição
        # -------------------------------------------------

        if self.campeonato_id and self.data_inscricao:
            if self.data_inscricao > self.campeonato.data_inicio:
                erros["data_inscricao"] = (
                    "A inscrição deve ser realizada até a data "
                    "de início do campeonato."
                )

        # -------------------------------------------------
        # Depois que as partidas começaram a ser montadas,
        # os participantes do campeonato ficam definidos.
        # -------------------------------------------------

        if self.campeonato_id:
            if self.pk is None:
                if self.campeonato.partidas.exists():
                    erros["campeonato"] = (
                        "Não é possível adicionar novos times porque "
                        "este campeonato já possui partidas cadastradas."
                    )

            else:
                inscricao_original = Inscricao.objects.filter(
                    pk=self.pk
                ).first()

                if inscricao_original:
                    alterou_campeonato = (
                        inscricao_original.campeonato_id
                        != self.campeonato_id
                    )

                    alterou_time = (
                        inscricao_original.time_id
                        != self.time_id
                    )

                    if alterou_campeonato or alterou_time:
                        campeonato_original_tem_partidas = (
                            inscricao_original.campeonato
                            .partidas
                            .exists()
                        )

                        campeonato_novo_tem_partidas = (
                            self.campeonato.partidas.exists()
                        )

                        if (
                            campeonato_original_tem_partidas
                            or campeonato_novo_tem_partidas
                        ):
                            erros["campeonato"] = (
                                "Não é possível alterar o time ou o "
                                "campeonato desta inscrição porque já "
                                "existem partidas cadastradas."
                            )

        # -------------------------------------------------
        # Mesmo time não pode aparecer duas vezes
        # no mesmo campeonato.
        # -------------------------------------------------

        if self.campeonato_id and self.time_id:
            inscricao_duplicada = Inscricao.objects.filter(
                campeonato_id=self.campeonato_id,
                time_id=self.time_id,
            ).exclude(
                pk=self.pk,
            )

            if inscricao_duplicada.exists():
                erros["time"] = (
                    "Este time já está inscrito neste campeonato."
                )

        # -------------------------------------------------
        # Mesmo técnico não pode comandar dois times
        # dentro do mesmo campeonato.
        # -------------------------------------------------

        if self.campeonato_id and self.time_id:
            tecnico = self.time.tecnico

            conflito_tecnico = Inscricao.objects.filter(
                campeonato_id=self.campeonato_id,
                time__tecnico_id=tecnico.id,
            ).exclude(
                pk=self.pk,
            )

            if conflito_tecnico.exists():
                time_conflitante = conflito_tecnico.first().time

                erros["time"] = (
                    f"O técnico {tecnico.nome} já comanda o time "
                    f"{time_conflitante.nome} neste campeonato."
                )

        if erros:
            raise ValidationError(erros)

    def possui_partidas(self):
        if not self.campeonato_id or not self.time_id:
            return False

        return Partida.objects.filter(
            campeonato_id=self.campeonato_id
        ).filter(
            Q(time_mandante_id=self.time_id)
            | Q(time_visitante_id=self.time_id)
        ).exists()

    def __str__(self):
        return f"{self.time} - {self.campeonato}"

    class Meta:
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"
        ordering = [
            "campeonato",
            "time",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["campeonato", "time"],
                name="unique_time_por_campeonato",
            )
        ]


# =========================================================
# PARTIDA
# =========================================================

class Partida(models.Model):
    rodada = models.PositiveIntegerField()

    data = models.DateField()
    horario = models.TimeField()

    # Os campos ficam vazios enquanto a partida
    # ainda não tiver sido realizada.
    gols_mandante = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    gols_visitante = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    campeonato = models.ForeignKey(
        Campeonato,
        on_delete=models.CASCADE,
        related_name="partidas",
    )

    time_mandante = models.ForeignKey(
        Time,
        on_delete=models.PROTECT,
        related_name="partidas_como_mandante",
    )

    time_visitante = models.ForeignKey(
        Time,
        on_delete=models.PROTECT,
        related_name="partidas_como_visitante",
    )

    estadio = models.ForeignKey(
        Estadio,
        on_delete=models.PROTECT,
        related_name="partidas",
    )

    def clean(self):
        super().clean()

        erros = {}

        quantidade_times = 0
        maximo_rodadas = 0
        rodadas_por_turno = 0

        # -------------------------------------------------
        # Campeonato precisa possuir número PAR de times.
        # Essa verificação ocorre ao cadastrar partidas,
        # permitindo cadastrar as inscrições uma a uma.
        # -------------------------------------------------

        if self.campeonato_id:
            quantidade_times = (
                self.campeonato.inscricoes.count()
            )

            if quantidade_times < 2:
                erros["campeonato"] = (
                    "O campeonato precisa possuir pelo menos "
                    "dois times inscritos para receber partidas."
                )

            elif quantidade_times % 2 != 0:
                erros["campeonato"] = (
                    "O campeonato precisa possuir uma quantidade "
                    "par de times para iniciar as partidas."
                )

            else:
                rodadas_por_turno = quantidade_times - 1
                maximo_rodadas = 2 * rodadas_por_turno

        # -------------------------------------------------
        # Rodada
        # -------------------------------------------------

        if self.rodada is not None:
            if self.rodada <= 0:
                erros["rodada"] = (
                    "A rodada deve ser maior que zero."
                )

            elif (
                maximo_rodadas > 0
                and self.rodada > maximo_rodadas
            ):
                erros["rodada"] = (
                    f"Com {quantidade_times} times, o campeonato "
                    f"possui no máximo {maximo_rodadas} rodadas."
                )

        # -------------------------------------------------
        # Placar
        # -------------------------------------------------

        mandante_tem_gols = (
            self.gols_mandante is not None
        )

        visitante_tem_gols = (
            self.gols_visitante is not None
        )

        if mandante_tem_gols != visitante_tem_gols:
            mensagem = (
                "Para registrar o resultado, informe os gols "
                "dos dois times. Se a partida ainda não aconteceu, "
                "deixe os dois campos vazios."
            )

            erros["gols_mandante"] = mensagem
            erros["gols_visitante"] = mensagem

        # -------------------------------------------------
        # Mandante e visitante precisam ser diferentes.
        # -------------------------------------------------

        if (
            self.time_mandante_id
            and self.time_visitante_id
            and self.time_mandante_id
            == self.time_visitante_id
        ):
            erros["time_visitante"] = (
                "Um time não pode jogar contra ele mesmo."
            )

        # -------------------------------------------------
        # Partida dentro das datas do campeonato.
        # -------------------------------------------------

        if self.campeonato_id and self.data:
            if (
                self.data < self.campeonato.data_inicio
                or self.data > self.campeonato.data_fim
            ):
                erros["data"] = (
                    "A partida deve acontecer dentro do período "
                    "do campeonato."
                )

        # -------------------------------------------------
        # Mandante precisa estar inscrito.
        # -------------------------------------------------

        if self.campeonato_id and self.time_mandante_id:
            mandante_inscrito = Inscricao.objects.filter(
                campeonato_id=self.campeonato_id,
                time_id=self.time_mandante_id,
            ).exists()

            if not mandante_inscrito:
                erros["time_mandante"] = (
                    "O time mandante não está inscrito "
                    "neste campeonato."
                )

        # -------------------------------------------------
        # Visitante precisa estar inscrito.
        # -------------------------------------------------

        if self.campeonato_id and self.time_visitante_id:
            visitante_inscrito = Inscricao.objects.filter(
                campeonato_id=self.campeonato_id,
                time_id=self.time_visitante_id,
            ).exists()

            if not visitante_inscrito:
                erros["time_visitante"] = (
                    "O time visitante não está inscrito "
                    "neste campeonato."
                )

        # -------------------------------------------------
        # Cada time joga apenas uma vez por rodada.
        # -------------------------------------------------

        if (
            self.campeonato_id
            and self.rodada
            and self.time_mandante_id
        ):
            conflito_rodada_mandante = Partida.objects.filter(
                campeonato_id=self.campeonato_id,
                rodada=self.rodada,
            ).exclude(
                pk=self.pk,
            ).filter(
                Q(time_mandante_id=self.time_mandante_id)
                | Q(time_visitante_id=self.time_mandante_id)
            )

            if conflito_rodada_mandante.exists():
                erros["time_mandante"] = (
                    "O time mandante já possui uma partida "
                    "nesta rodada."
                )

        if (
            self.campeonato_id
            and self.rodada
            and self.time_visitante_id
        ):
            conflito_rodada_visitante = Partida.objects.filter(
                campeonato_id=self.campeonato_id,
                rodada=self.rodada,
            ).exclude(
                pk=self.pk,
            ).filter(
                Q(time_mandante_id=self.time_visitante_id)
                | Q(time_visitante_id=self.time_visitante_id)
            )

            if conflito_rodada_visitante.exists():
                erros["time_visitante"] = (
                    "O time visitante já possui uma partida "
                    "nesta rodada."
                )

        # -------------------------------------------------
        # TURNO E RETURNO
        #
        # Cada par de times pode se enfrentar apenas
        # uma vez em cada turno.
        # -------------------------------------------------

        if (
            self.campeonato_id
            and self.rodada
            and rodadas_por_turno > 0
            and self.time_mandante_id
            and self.time_visitante_id
            and self.time_mandante_id
            != self.time_visitante_id
        ):
            if self.rodada <= rodadas_por_turno:
                inicio_turno = 1
                fim_turno = rodadas_por_turno
            else:
                inicio_turno = rodadas_por_turno + 1
                fim_turno = 2 * rodadas_por_turno

            confronto_no_mesmo_turno = (
                Partida.objects.filter(
                    campeonato_id=self.campeonato_id,
                    rodada__gte=inicio_turno,
                    rodada__lte=fim_turno,
                )
                .exclude(pk=self.pk)
                .filter(
                    Q(
                        time_mandante_id=self.time_mandante_id,
                        time_visitante_id=self.time_visitante_id,
                    )
                    | Q(
                        time_mandante_id=self.time_visitante_id,
                        time_visitante_id=self.time_mandante_id,
                    )
                )
            )

            if confronto_no_mesmo_turno.exists():
                erros["time_visitante"] = (
                    "Estes dois times já se enfrentaram neste turno."
                )

        # -------------------------------------------------
        # O mesmo mando não pode se repetir.
        #
        # Exemplo:
        # Bahia x Flamengo -> permitido uma vez
        # Flamengo x Bahia -> permitido uma vez
        # Bahia x Flamengo novamente -> proibido
        # -------------------------------------------------

        if (
            self.campeonato_id
            and self.time_mandante_id
            and self.time_visitante_id
        ):
            mesmo_confronto = Partida.objects.filter(
                campeonato_id=self.campeonato_id,
                time_mandante_id=self.time_mandante_id,
                time_visitante_id=self.time_visitante_id,
            ).exclude(
                pk=self.pk,
            )

            if mesmo_confronto.exists():
                erros["time_visitante"] = (
                    "Este confronto com o mesmo mandante e "
                    "visitante já foi cadastrado neste campeonato."
                )

        # -------------------------------------------------
        # Conflitos de DATA e HORÁRIO.
        # -------------------------------------------------

        if self.data and self.horario:
            partidas_no_horario = Partida.objects.filter(
                data=self.data,
                horario=self.horario,
            ).exclude(
                pk=self.pk,
            )

            # Mesmo estádio não pode receber dois jogos
            # simultaneamente.
            if self.estadio_id:
                estadio_ocupado = partidas_no_horario.filter(
                    estadio_id=self.estadio_id
                ).exists()

                if estadio_ocupado:
                    erros["estadio"] = (
                        "Este estádio já possui outra partida "
                        "marcada nesta data e horário."
                    )

            # Mandante não pode estar jogando outra partida
            # ao mesmo tempo.
            if self.time_mandante_id:
                conflito_mandante = partidas_no_horario.filter(
                    Q(
                        time_mandante_id=self.time_mandante_id
                    )
                    | Q(
                        time_visitante_id=self.time_mandante_id
                    )
                ).exists()

                if conflito_mandante:
                    erros["time_mandante"] = (
                        "O time mandante já possui outra partida "
                        "nesta data e horário."
                    )

            # Visitante também não pode estar em outra
            # partida simultaneamente.
            if self.time_visitante_id:
                conflito_visitante = partidas_no_horario.filter(
                    Q(
                        time_mandante_id=self.time_visitante_id
                    )
                    | Q(
                        time_visitante_id=self.time_visitante_id
                    )
                ).exists()

                if conflito_visitante:
                    erros["time_visitante"] = (
                        "O time visitante já possui outra partida "
                        "nesta data e horário."
                    )

        if erros:
            raise ValidationError(erros)

    @property
    def realizada(self):
        return (
            self.gols_mandante is not None
            and self.gols_visitante is not None
        )

    def __str__(self):
        if self.realizada:
            placar = (
                f"{self.gols_mandante} x "
                f"{self.gols_visitante}"
            )
        else:
            placar = "x"

        return (
            f"Rodada {self.rodada} - "
            f"{self.time_mandante} "
            f"{placar} "
            f"{self.time_visitante}"
        )

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"

        ordering = [
            "campeonato",
            "rodada",
            "data",
            "horario",
        ]

        constraints = [
            # Mesmo estádio não pode receber duas
            # partidas na mesma data e horário.
            models.UniqueConstraint(
                fields=[
                    "data",
                    "horario",
                    "estadio",
                ],
                name="unique_partida_estadio_horario",
            ),

            # A combinação campeonato + mandante + visitante
            # só pode aparecer uma vez.
            models.UniqueConstraint(
                fields=[
                    "campeonato",
                    "time_mandante",
                    "time_visitante",
                ],
                name="unique_confronto_mando_campeonato",
            ),
        ]


# =========================================================
# JOGADOR NO TIME / ELENCO
# =========================================================

class JogadorTime(models.Model):
    time = models.ForeignKey(
        Time,
        on_delete=models.CASCADE,
        related_name="jogadores_time",
    )

    jogador = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="times_como_jogador",
    )

    posicao = models.CharField(
        max_length=50
    )

    numero_camisa = models.PositiveIntegerField()

    temporada = models.IntegerField()

    def clean(self):
        super().clean()

        erros = {}

        # -------------------------------------------------
        # Número da camisa
        # -------------------------------------------------

        if (
            self.numero_camisa is not None
            and self.numero_camisa <= 0
        ):
            erros["numero_camisa"] = (
                "O número da camisa deve ser maior que zero."
            )

        # -------------------------------------------------
        # Temporada
        # -------------------------------------------------

        if (
            self.temporada is not None
            and self.temporada <= 0
        ):
            erros["temporada"] = (
                "Informe uma temporada válida."
            )

        # -------------------------------------------------
        # Um jogador pertence a apenas um time
        # em cada temporada.
        #
        # Não estamos armazenando histórico de transferências.
        # -------------------------------------------------

        if (
            self.jogador_id
            and self.temporada
        ):
            outro_vinculo = JogadorTime.objects.filter(
                jogador_id=self.jogador_id,
                temporada=self.temporada,
            ).exclude(
                pk=self.pk,
            )

            if outro_vinculo.exists():
                vinculo = outro_vinculo.first()

                erros["jogador"] = (
                    f"Este jogador já pertence ao time "
                    f"{vinculo.time.nome} na temporada "
                    f"{self.temporada}."
                )

        # -------------------------------------------------
        # Número da camisa não pode se repetir
        # no mesmo time e temporada.
        # -------------------------------------------------

        if (
            self.time_id
            and self.numero_camisa
            and self.temporada
        ):
            camisa_ocupada = JogadorTime.objects.filter(
                time_id=self.time_id,
                numero_camisa=self.numero_camisa,
                temporada=self.temporada,
            ).exclude(
                pk=self.pk,
            )

            if camisa_ocupada.exists():
                erros["numero_camisa"] = (
                    "Este número de camisa já está sendo usado "
                    "por outro jogador deste time nesta temporada."
                )

        if erros:
            raise ValidationError(erros)

    def __str__(self):
        return (
            f"{self.jogador} - "
            f"{self.time} "
            f"({self.temporada})"
        )

    class Meta:
        verbose_name = "Jogador no Time"
        verbose_name_plural = "Jogadores nos Times"

        ordering = [
            "time",
            "numero_camisa",
        ]

        constraints = [
            # Um jogador só pode pertencer a um time
            # em determinada temporada.
            models.UniqueConstraint(
                fields=[
                    "jogador",
                    "temporada",
                ],
                name="unique_jogador_temporada",
            ),

            # Camisa única dentro do time/temporada.
            models.UniqueConstraint(
                fields=[
                    "time",
                    "numero_camisa",
                    "temporada",
                ],
                name="unique_camisa_time_temporada",
            ),
        ]