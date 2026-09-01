from django.contrib import admin

from .models import (
    Campeonato,
    Estadio,
    Inscricao,
    JogadorTime,
    Partida,
    Pessoa,
    Time,
)


admin.site.site_header = "LigaHub - Administração"
admin.site.site_title = "LigaHub"
admin.site.index_title = "Gerenciamento de Campeonatos"


@admin.register(Campeonato)
class CampeonatoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "temporada",
        "data_inicio",
        "data_fim",
        "ativo",
        "quantidade_de_times",
    )

    search_fields = (
        "nome",
    )

    list_filter = (
        "temporada",
        "ativo",
    )

    ordering = (
        "-temporada",
        "nome",
    )

    @admin.display(description="Times")
    def quantidade_de_times(self, obj):
        return obj.quantidade_times()


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "data_nascimento",
        "username",
    )

    search_fields = (
        "nome",
        "username",
    )

    ordering = (
        "nome",
    )

    # O username existe apenas internamente
    # e é gerado automaticamente.
    readonly_fields = (
        "username",
    )

    fields = (
        "nome",
        "data_nascimento",
        "username",
    )


@admin.register(Estadio)
class EstadioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "cidade",
        "capacidade",
    )

    search_fields = (
        "nome",
        "cidade",
        "endereco",
    )

    list_filter = (
        "cidade",
    )

    ordering = (
        "nome",
    )


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome",
        "cidade",
        "tecnico",
        "ano_fundacao",
    )

    search_fields = (
        "nome",
        "cidade",
        "tecnico__nome",
    )

    list_filter = (
        "cidade",
    )

    ordering = (
        "nome",
    )


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "campeonato",
        "time",
        "data_inscricao",
    )

    search_fields = (
        "campeonato__nome",
        "time__nome",
        "time__tecnico__nome",
    )

    list_filter = (
        "campeonato",
        "data_inscricao",
    )

    ordering = (
        "campeonato",
        "time",
    )

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.possui_partidas():
            return False

        return super().has_delete_permission(request, obj)


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "campeonato",
        "rodada",
        "data",
        "horario",
        "time_mandante",
        "placar",
        "time_visitante",
        "estadio",
    )

    search_fields = (
        "campeonato__nome",
        "time_mandante__nome",
        "time_visitante__nome",
        "estadio__nome",
    )

    list_filter = (
        "campeonato",
        "rodada",
        "data",
        "estadio",
    )

    ordering = (
        "campeonato",
        "rodada",
        "data",
        "horario",
    )

    @admin.display(description="Placar")
    def placar(self, obj):
        if obj.realizada:
            return (
                f"{obj.gols_mandante} x "
                f"{obj.gols_visitante}"
            )

        return "— x —"


@admin.register(JogadorTime)
class JogadorTimeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "jogador",
        "time",
        "posicao",
        "numero_camisa",
        "temporada",
    )

    search_fields = (
        "jogador__nome",
        "time__nome",
        "posicao",
    )

    list_filter = (
        "time",
        "posicao",
        "temporada",
    )

    ordering = (
        "time",
        "numero_camisa",
    )