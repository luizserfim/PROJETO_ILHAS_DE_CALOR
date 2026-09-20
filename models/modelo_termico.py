from math import isfinite
from numbers import Real
from collections.abc import Mapping

from config.model_config import (
    PESOS_TERMICOS,
    DELTA_T_MIN,
    DELTA_T_MAX,
)


def validar_numero(valor, nome, minimo=None, maximo=None):
    """Rejeita booleanos, strings, NaN e infinitos nas fronteiras do modelo."""
    if isinstance(valor, bool) or not isinstance(valor, Real):
        raise ValueError(f"{nome} deve ser um número real finito.")
    try:
        finito = isfinite(valor)
    except OverflowError:
        finito = False
    if not finito:
        raise ValueError(f"{nome} deve ser um número real finito.")
    if minimo is not None and valor < minimo:
        raise ValueError(f"{nome} deve ser maior ou igual a {minimo}.")
    if maximo is not None and valor > maximo:
        raise ValueError(f"{nome} deve ser menor ou igual a {maximo}.")
    return valor


def validar_cobertura(
    vegetacao,
    pavimento,
    edificacoes,
    solo_exposto,
    agua,
    tolerancia=0.01,
):
    validar_numero(tolerancia, "Tolerância", 0, 0.01)
    coberturas = {
        "vegetacao": vegetacao,
        "pavimento": pavimento,
        "edificacoes": edificacoes,
        "solo_exposto": solo_exposto,
        "agua": agua,
    }

    for nome, valor in coberturas.items():
        validar_numero(valor, nome, 0, 100)

    total = sum(coberturas.values())

    if abs(total - 100) > tolerancia:
        raise ValueError(
            f"As coberturas totalizam {total:.1f}%. "
            "A soma deve ser igual a 100%."
        )

    return True


def calcular_indice_termico(
    vegetacao,
    pavimento,
    edificacoes,
    solo_exposto,
    agua,
    pesos=None,
):
    validar_cobertura(vegetacao, pavimento, edificacoes, solo_exposto, agua)
    if pesos is None:
        pesos = PESOS_TERMICOS

    if not isinstance(pesos, Mapping) or set(pesos) != set(PESOS_TERMICOS):
        raise ValueError("Os pesos devem conter exatamente as cinco coberturas.")
    for nome, peso in pesos.items():
        validar_numero(peso, f"Peso de {nome}", -1, 1)
    return (
        pesos["vegetacao"] * vegetacao
        + pesos["pavimento"] * pavimento
        + pesos["edificacoes"] * edificacoes
        + pesos["solo_exposto"] * solo_exposto
        + pesos["agua"] * agua
    ) / 100


def calcular_anomalia_termica(indice_termico):
    validar_numero(indice_termico, "Índice térmico")
    delta_t = indice_termico * 10
    return max(DELTA_T_MIN, min(DELTA_T_MAX, delta_t))


def estimar_temperatura(
    temperatura_referencia,
    vegetacao,
    pavimento,
    edificacoes,
    solo_exposto,
    agua,
):
    validar_numero(temperatura_referencia, "Temperatura de referência", -90, 60)
    validar_cobertura(
        vegetacao,
        pavimento,
        edificacoes,
        solo_exposto,
        agua,
    )

    indice = calcular_indice_termico(
        vegetacao,
        pavimento,
        edificacoes,
        solo_exposto,
        agua,
    )

    delta_t = calcular_anomalia_termica(indice)

    return {
        "temperatura_referencia": temperatura_referencia,
        "indice_termico": indice,
        "anomalia_termica": delta_t,
        "temperatura_estimada": temperatura_referencia + delta_t,
    }


def comparar_intervencao(
    temperatura_referencia,
    vegetacao,
    pavimento,
    edificacoes,
    solo_exposto,
    agua,
    percentual_convertido,
    tipo_intervencao="Pavimento → Vegetação",
):
    """
    Compara o cenário atual com uma intervenção que converte
    determinada cobertura em vegetação.
    """
    validar_numero(percentual_convertido, "Percentual convertido", 0, 100)
    validar_cobertura(vegetacao, pavimento, edificacoes, solo_exposto, agua)

    coberturas = {
        "vegetacao": vegetacao,
        "pavimento": pavimento,
        "edificacoes": edificacoes,
        "solo_exposto": solo_exposto,
        "agua": agua,
    }

    origens = {
        "Pavimento → Vegetação": "pavimento",
        "Solo exposto → Vegetação": "solo_exposto",
        "Edificações → Vegetação": "edificacoes",
    }

    if not isinstance(tipo_intervencao, str) or tipo_intervencao not in origens:
        raise ValueError("Tipo de intervenção não reconhecido.")

    origem = origens[tipo_intervencao]

    if percentual_convertido > coberturas[origem]:
        raise ValueError(
            "Não é possível converter uma área maior do que a disponível."
        )

    atual = estimar_temperatura(
        temperatura_referencia,
        vegetacao,
        pavimento,
        edificacoes,
        solo_exposto,
        agua,
    )

    novas = coberturas.copy()
    novas[origem] -= percentual_convertido
    novas["vegetacao"] += percentual_convertido

    futuro = estimar_temperatura(
        temperatura_referencia,
        novas["vegetacao"],
        novas["pavimento"],
        novas["edificacoes"],
        novas["solo_exposto"],
        novas["agua"],
    )

    return {
        "cenario_atual": atual,
        "cenario_intervencao": futuro,
        "reducao_estimada": (
            atual["temperatura_estimada"]
            - futuro["temperatura_estimada"]
        ),
        "coberturas_intervencao": novas,
        "tipo_intervencao": tipo_intervencao,
    }
