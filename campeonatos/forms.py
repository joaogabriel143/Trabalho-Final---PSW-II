from django import forms

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
# CAMPEONATO
# =========================================================

class CampeonatoForm(forms.ModelForm):
    class Meta:
        model = Campeonato

        fields = [
            "nome",
            "temporada",
            "data_inicio",
            "data_fim",
            "descricao",
            "ativo",
        ]

        widgets = {
            "data_inicio": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "data_fim": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }


# =========================================================
# PESSOA
# =========================================================

class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa

        fields = [
            "nome",
            "data_nascimento",
        ]

        widgets = {
            "data_nascimento": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }


# =========================================================
# ESTÁDIO
# =========================================================

class EstadioForm(forms.ModelForm):
    class Meta:
        model = Estadio

        fields = [
            "nome",
            "cidade",
            "endereco",
            "capacidade",
        ]


# =========================================================
# TIME
# =========================================================

class TimeForm(forms.ModelForm):
    class Meta:
        model = Time

        fields = [
            "nome",
            "cidade",
            "tecnico",
            "escudo",
            "ano_fundacao",
        ]


# =========================================================
# INSCRIÇÃO
# =========================================================

class InscricaoForm(forms.ModelForm):
    class Meta:
        model = Inscricao

        fields = [
            "data_inscricao",
            "campeonato",
            "time",
        ]

        widgets = {
            "data_inscricao": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }


# =========================================================
# PARTIDA
# =========================================================

class PartidaForm(forms.ModelForm):
    class Meta:
        model = Partida

        fields = [
            "campeonato",
            "rodada",
            "data",
            "horario",
            "time_mandante",
            "gols_mandante",
            "gols_visitante",
            "time_visitante",
            "estadio",
        ]

        widgets = {
            "data": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "horario": forms.TimeInput(
                attrs={"type": "time"},
                format="%H:%M",
            ),
        }


# =========================================================
# ELENCO
# =========================================================

class JogadorTimeForm(forms.ModelForm):
    class Meta:
        model = JogadorTime

        fields = [
            "time",
            "jogador",
            "posicao",
            "numero_camisa",
            "temporada",
        ]