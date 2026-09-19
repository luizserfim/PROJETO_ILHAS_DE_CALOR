"""

import requests

url = "https://api1.funceme.br/rpc/v1/dado-sensor-grafico"

parametros = {
    "estacao": 35852,
    "sensor":"2,3,4",
    "periodo": "24h"
}

try:
    resposta = requests.get(
        url,
        params=parametros,
        timeout=30
    )

    print("Status HTTP:", resposta.status_code)
    print("URL consultada:", resposta.url)
    print()

    if resposta.status_code == 200:
        dados = resposta.json()

        print("Dados recebidos:")
        print(dados)

    else:
        print("Resposta do servidor:")
        print(resposta.text)

except requests.exceptions.Timeout:
    print("ERRO: A FUNCEME demorou demais para responder.")

except requests.exceptions.RequestException as erro:
    print("ERRO na requisição:")
    print(erro)
    """

from services.funceme import obter_dados_temperatura, obter_temperatura_atual


df = obter_dados_temperatura()

print("Dados da FUNCEME:")
print(df)

print()
print("Última observação:")

atual = obter_temperatura_atual()

print("Estação:", atual["estacao"])
print("Horário:", atual["data_hora"])
print("Temperatura média:", atual["temperatura_media"], "°C")
print("Temperatura máxima:", atual["temperatura_maxima"], "°C")
print("Temperatura mínima:", atual["temperatura_minima"], "°C")

