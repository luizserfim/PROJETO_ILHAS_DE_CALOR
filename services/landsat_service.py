from pathlib import Path
from datetime import date, timedelta

import geopandas as gpd
import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BATURITE_GEOJSON = PROJECT_ROOT / "data" / "processed" / "baturite.geojson"

STAC_API = "https://landsatlook.usgs.gov/stac-server"
STAC_SEARCH = f"{STAC_API}/search"

# Coleção 2, Level-2, Surface Temperature.
COLLECTION_ST = "landsat-c2l2-st"


def carregar_geometria_baturite():
    """
    Carrega o limite municipal de Baturité e retorna a geometria
    no formato GeoJSON exigido pelo parâmetro 'intersects' do STAC.
    """
    if not BATURITE_GEOJSON.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {BATURITE_GEOJSON}\n"
            "Execute primeiro services/geospatial.py."
        )

    gdf = gpd.read_file(BATURITE_GEOJSON)

    if gdf.empty:
        raise ValueError("O GeoJSON de Baturité está vazio.")

    if gdf.crs is None:
        raise ValueError("O GeoJSON de Baturité não possui CRS.")

    gdf = gdf.to_crs(epsg=4326)

    # Dissolve garante uma única geometria, mesmo que o arquivo
    # eventualmente contenha mais de uma feição.
    geometria = gdf.geometry.union_all()

    return geometria.__geo_interface__


def buscar_cenas_landsat(
    data_inicial=None,
    data_final=None,
    nuvens_max=20,
    limite=50,
):
    """
    Consulta o STAC oficial do USGS e retorna cenas Landsat
    Collection 2 Level-2 Surface Temperature que intersectam
    o município de Baturité.

    Por padrão, pesquisa os últimos 12 meses.

    Parâmetros:
        data_inicial: string YYYY-MM-DD ou None
        data_final: string YYYY-MM-DD ou None
        nuvens_max: cobertura máxima de nuvens da cena (%)
        limite: número máximo de itens retornados pelo STAC
    """
    hoje = date.today()

    if data_final is None:
        data_final = hoje.isoformat()

    if data_inicial is None:
        data_inicial = (hoje - timedelta(days=365)).isoformat()

    if not 0 <= nuvens_max <= 100:
        raise ValueError("nuvens_max deve estar entre 0 e 100.")

    if limite < 1:
        raise ValueError("limite deve ser maior que zero.")

    geometria = carregar_geometria_baturite()

    payload = {
        "collections": [COLLECTION_ST],
        "intersects": geometria,
        "datetime": f"{data_inicial}T00:00:00Z/{data_final}T23:59:59Z",
        "limit": limite,
    }

    try:
        resposta = requests.post(
            STAC_SEARCH,
            json=payload,
            timeout=60,
        )
        resposta.raise_for_status()
        dados = resposta.json()

    except requests.RequestException as erro:
        raise RuntimeError(
            f"Erro ao consultar o STAC do USGS: {erro}"
        ) from erro

    cenas = []

    for item in dados.get("features", []):
        propriedades = item.get("properties", {})

        nuvens = propriedades.get("eo:cloud_cover")

        # Alguns itens podem não informar cobertura de nuvens.
        # Mantemos apenas cenas que possuam esse metadado e
        # atendam ao limite definido.
        if nuvens is None:
            continue

        try:
            nuvens = float(nuvens)
        except (TypeError, ValueError):
            continue

        if nuvens > nuvens_max:
            continue

        plataforma = (
            propriedades.get("platform")
            or propriedades.get("constellation")
            or "Landsat"
        )

        cenas.append(
            {
                "id": item.get("id"),
                "data_hora": propriedades.get("datetime"),
                "plataforma": plataforma,
                "nuvens": nuvens,
                "collection": item.get("collection"),
                "assets": item.get("assets", {}),
            }
        )

    # Primeiro as cenas com menos nuvens; em empate, prioriza
    # a data mais recente.
    cenas.sort(
        key=lambda cena: (
            cena["nuvens"],
            cena["data_hora"] or "",
        )
    )

    return cenas


def resumir_assets(assets):
    """
    Retorna somente informações úteis dos assets de uma cena.
    Ajuda a descobrir os nomes exatos das bandas disponíveis
    antes de implementarmos o processamento raster.
    """
    resumo = {}

    for nome, asset in assets.items():
        resumo[nome] = {
            "titulo": asset.get("title"),
            "tipo": asset.get("type"),
            "href": asset.get("href"),
        }

    return resumo


def selecionar_melhor_cena(
    data_inicial=None,
    data_final=None,
    nuvens_max=20,
):
    """
    Retorna a cena de menor cobertura de nuvens encontrada
    no período solicitado.
    """
    cenas = buscar_cenas_landsat(
        data_inicial=data_inicial,
        data_final=data_final,
        nuvens_max=nuvens_max,
    )

    if not cenas:
        return None

    return cenas[0]


if __name__ == "__main__":
    try:
        print("Consultando Landsat para Baturité-CE...")
        print()

        cenas = buscar_cenas_landsat(
            nuvens_max=20,
            limite=100,
        )

        if not cenas:
            print(
                "Nenhuma cena com até 20% de cobertura de nuvens "
                "foi encontrada no período."
            )

        else:
            print(f"Cenas encontradas: {len(cenas)}")
            print()

            # Mostra até as 10 melhores.
            for numero, cena in enumerate(cenas[:10], start=1):
                print(f"{numero}. {cena['id']}")
                print(f"   Data: {cena['data_hora']}")
                print(f"   Plataforma: {cena['plataforma']}")
                print(f"   Nuvens: {cena['nuvens']:.2f}%")
                print()

            melhor = cenas[0]

            print("=" * 60)
            print("MELHOR CENA PELO CRITÉRIO DE COBERTURA DE NUVENS")
            print("=" * 60)
            print(f"ID: {melhor['id']}")
            print(f"Data: {melhor['data_hora']}")
            print(f"Plataforma: {melhor['plataforma']}")
            print(f"Nuvens: {melhor['nuvens']:.2f}%")
            print()
            print("Assets disponíveis:")

            for nome, info in resumir_assets(
                melhor["assets"]
            ).items():
                print(f"  - {nome}: {info['titulo']}")

    except Exception as erro:
        print("ERRO AO CONSULTAR O LANDSAT:")
        print(erro)
