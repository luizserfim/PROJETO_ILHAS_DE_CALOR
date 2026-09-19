from config.model_config import (
    PESOS_TERMICOS,
    DELTA_T_MIN,
    DELTA_T_MAX,
)


def validar_cobertura(
    vegetacao,
    pavimento,
    edificacoes,
    solo_exposto,
    agua,
    tolerancia=0.01,
):
    coberturas = {
        "vegetacao": vegetacao,
        "pavimento": pavimento,
        "edificacoes": edificacoes,
        "solo_exposto": solo_exposto,
        "agua": agua,
    }

    for nome, valor in coberturas.items():
        if not 0 <= valor <= 100:
            raise ValueError(
                f"A cobertura '{nome}' deve estar entre 0 e 100%."
            )

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
    if pesos is None:
        pesos = PESOS_TERMICOS

    return (
        pesos["vegetacao"] * vegetacao
        + pesos["pavimento"] * pavimento
        + pesos["edificacoes"] * edificacoes
        + pesos["solo_exposto"] * solo_exposto
        + pesos["agua"] * agua
    ) / 100


def calcular_anomalia_termica(indice_termico):
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
    if percentual_convertido < 0:
        raise ValueError("O percentual convertido não pode ser negativo.")

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

    if tipo_intervencao not in origens:
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
