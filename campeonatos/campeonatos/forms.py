from django import forms

from .models import Campeonato, Inscricao, Partida


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