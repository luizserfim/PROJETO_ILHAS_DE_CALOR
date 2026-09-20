"""Cliente limitado à estação Baturité; respostas externas nunca são executadas."""
import json
import math
import time

import pandas as pd
import requests

URL_FUNCEME = "https://api1.funceme.br/rpc/v1/dado-sensor-grafico"
ESTACAO_BATURITE = 35852
MAX_BYTES = 2_000_000
MAX_REGISTROS = 10_000
PRAZO_SEGUNDOS = 20
FUSO = "America/Fortaleza"
COLUNAS = {"2": "temperatura_media", "3": "temperatura_maxima", "4": "temperatura_minima"}


class ErroFunceme(RuntimeError):
    """Indisponibilidade ou resposta inválida da fonte meteorológica."""


def _consultar(periodo):
    if periodo != "24h":
        raise ValueError("O período suportado é 24h.")
    inicio = time.monotonic()
    try:
        with requests.get(
            URL_FUNCEME,
            params={"estacao": ESTACAO_BATURITE, "sensor": "2,3,4", "periodo": periodo},
            timeout=(5, 10), allow_redirects=False, stream=True,
        ) as resposta:
            if resposta.status_code != 200:
                raise ErroFunceme("A FUNCEME não retornou uma resposta válida.")
            conteudo = bytearray()
            for bloco in resposta.iter_content(chunk_size=8192):
                if time.monotonic() - inicio > PRAZO_SEGUNDOS:
                    raise ErroFunceme("A consulta à FUNCEME excedeu o prazo.")
                if len(conteudo) + len(bloco) > MAX_BYTES:
                    raise ErroFunceme("A resposta da FUNCEME excedeu o limite de tamanho.")
                conteudo.extend(bloco)
            return json.loads(conteudo)
    except requests.RequestException as erro:
        raise ErroFunceme("Não foi possível consultar a FUNCEME.") from erro
    except (ValueError, UnicodeError, RecursionError) as erro:
        raise ErroFunceme("A FUNCEME retornou um documento inválido.") from erro


def _horario(valor):
    if not isinstance(valor, str) or len(valor) > 64:
        raise ValueError("Horário inválido.")
    horario = pd.Timestamp(valor).as_unit("ns")
    if pd.isna(horario):
        raise ValueError("Horário ausente.")
    # A API original usa horários locais sem offset; offsets explícitos são preservados.
    if horario.tzinfo is None:
        horario = horario.tz_localize(FUSO)
    return horario.tz_convert(FUSO)


def obter_dados_temperatura(periodo="24h"):
    dados = _consultar(periodo)
    try:
        sensores = dados["data"]["list"]
        if not isinstance(sensores, list) or len(sensores) > 20:
            raise ValueError("Lista de sensores inválida.")
        registros = {}
        quantidade = 0
        for sensor in sensores:
            identificador = str(sensor["name"])
            if identificador not in COLUNAS:
                continue
            serie = sensor["series"]
            if not isinstance(serie, list):
                raise ValueError("Série inválida.")
            quantidade += len(serie)
            if quantidade > MAX_REGISTROS:
                raise ValueError("Registros em excesso.")
            for registro in serie:
                try:
                    horario = _horario(registro["name"])
                    bruto = registro["value"]
                    if isinstance(bruto, bool):
                        continue
                    valor = float(bruto)
                    if not math.isfinite(valor) or not -90 <= valor <= 60:
                        continue
                except (KeyError, TypeError, ValueError, OverflowError):
                    continue
                linha = registros.setdefault(horario, {})
                coluna = COLUNAS[identificador]
                if coluna in linha and linha[coluna] != valor:
                    raise ValueError("Observações conflitantes no mesmo horário.")
                linha[coluna] = valor
        return pd.DataFrame.from_dict(registros, orient="index").reindex(
            columns=list(COLUNAS.values())
        ).sort_index()
    except (KeyError, TypeError, ValueError, AttributeError) as erro:
        raise ErroFunceme("A estrutura dos dados da FUNCEME é inválida.") from erro


def obter_temperatura_atual():
    df = obter_dados_temperatura()
    completos = df.dropna(subset=list(COLUNAS.values()))
    validos = completos[
        (completos.temperatura_minima <= completos.temperatura_media)
        & (completos.temperatura_media <= completos.temperatura_maxima)
    ]
    if validos.empty:
        raise ErroFunceme("Não há observações completas e consistentes na FUNCEME.")
    horario = validos.index[-1]
    idade = pd.Timestamp.now(tz=FUSO) - horario
    if idade > pd.Timedelta(hours=3) or idade < -pd.Timedelta(minutes=15):
        raise ErroFunceme("A observação da FUNCEME está desatualizada ou no futuro.")
    ultimo = validos.iloc[-1]
    return {
        "estacao": "Baturité - APA", "codigo_estacao": ESTACAO_BATURITE,
        "data_hora": horario,
        **{coluna: float(ultimo[coluna]) for coluna in COLUNAS.values()},
    }
