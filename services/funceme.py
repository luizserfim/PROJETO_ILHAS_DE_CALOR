import requests
import pandas as pd


URL_FUNCEME = "https://api1.funceme.br/rpc/v1/dado-sensor-grafico"
ESTACAO_BATURITE = 35852

def obter_dados_temperatura(periodo="24h"):

    parametros = {
        "estacao": ESTACAO_BATURITE,
        "sensor": "2,3,4",
        "periodo": periodo
    }
    try:
        resposta = requests.get(
            URL_FUNCEME,
            params=parametros,
            timeout=30
        )

        resposta.raise_for_status()

        dados = resposta.json()

    except requests.exceptions.RequestException as erro:
        raise RuntimeError(
            f"Erro ao consultar a FUNCEME: {erro}"
        )

    lista_sensores = dados["data"]["list"]

    registros = {}

    for sensor in lista_sensores:

        id_sensor = sensor["name"]

        for registro in sensor["series"]:

            horario = registro["name"]
            valor = float(registro["value"])

            if horario not in registros:
                registros[horario] = {}

            registros[horario][id_sensor] = valor

    df = pd.DataFrame.from_dict(
        registros,
        orient="index"
    )

    df.index = pd.to_datetime(df.index)

    df = df.sort_index()

    df = df.rename(
        columns={
            2: "temperatura_media",
            3: "temperatura_maxima",
            4: "temperatura_minima"
        }
    )

    return df

def obter_temperatura_atual():

    df = obter_dados_temperatura()

    if df.empty:
        raise RuntimeError(
            "A FUNCEME não retornou dados de temperatura."
        )

    # Remove linhas sem temperatura média
    df_validos = df.dropna(subset=["temperatura_media"])

    if df_validos.empty:
        raise RuntimeError(
            "Não há registros válidos de temperatura."
        )

    horario = df_validos.index[-1]
    ultimo = df_validos.iloc[-1]

    return {
        "estacao": "Baturité - APA",
        "codigo_estacao": ESTACAO_BATURITE,
        "data_hora": horario,
        "temperatura_media": ultimo["temperatura_media"],
        "temperatura_maxima": ultimo["temperatura_maxima"],
        "temperatura_minima": ultimo["temperatura_minima"]
    }