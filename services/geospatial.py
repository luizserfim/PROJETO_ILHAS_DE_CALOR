from pathlib import Path

import geopandas as gpd


# Diretórios do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
IBGE_DIR = PROJECT_ROOT / "data" / "raw" / "ibge"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_GEOJSON = PROCESSED_DIR / "baturite.geojson"


def localizar_shapefile_ibge():
    """
    Localiza automaticamente o shapefile de municípios
    dentro de data/raw/ibge.
    """
    arquivos = list(IBGE_DIR.rglob("*.shp"))

    if not arquivos:
        raise FileNotFoundError(
            "Nenhum arquivo .shp foi encontrado em "
            f"{IBGE_DIR}. Verifique se a malha do IBGE foi extraída."
        )

    # Dá preferência ao arquivo de municípios, caso existam vários shapefiles.
    candidatos = [
        arquivo
        for arquivo in arquivos
        if "municip" in arquivo.name.lower()
    ]

    if candidatos:
        return candidatos[0]

    if len(arquivos) == 1:
        return arquivos[0]

    raise RuntimeError(
        "Foram encontrados vários shapefiles e não foi possível "
        "identificar automaticamente a malha municipal."
    )


def carregar_baturite():
    """
    Carrega a malha municipal do IBGE e retorna somente
    o município de Baturité-CE.
    """
    shapefile = localizar_shapefile_ibge()
    gdf = gpd.read_file(shapefile)

    if "NM_MUN" not in gdf.columns:
        raise KeyError(
            "A coluna 'NM_MUN' não foi encontrada na malha do IBGE. "
            f"Colunas disponíveis: {list(gdf.columns)}"
        )

    baturite = gdf[
        gdf["NM_MUN"].astype(str).str.strip().str.casefold()
        == "baturité".casefold()
    ].copy()

    if baturite.empty:
        raise ValueError(
            "O município de Baturité não foi encontrado na malha."
        )

    # GeoJSON usa normalmente o sistema geográfico WGS84.
    if baturite.crs is None:
        raise ValueError(
            "A malha não possui sistema de referência espacial (CRS)."
        )

    baturite = baturite.to_crs(epsg=4326)

    return baturite


def gerar_geojson_baturite():
    """
    Gera data/processed/baturite.geojson e retorna
    o caminho do arquivo criado.
    """
    baturite = carregar_baturite()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    baturite.to_file(
        OUTPUT_GEOJSON,
        driver="GeoJSON",
    )

    return OUTPUT_GEOJSON


def obter_bbox_baturite():
    """
    Retorna a caixa envolvente de Baturité em WGS84.

    Retorno:
        {
            "oeste": ...,
            "sul": ...,
            "leste": ...,
            "norte": ...
        }
    """
    baturite = carregar_baturite()

    oeste, sul, leste, norte = baturite.total_bounds

    return {
        "oeste": float(oeste),
        "sul": float(sul),
        "leste": float(leste),
        "norte": float(norte),
    }


if __name__ == "__main__":
    try:
        arquivo = gerar_geojson_baturite()
        bbox = obter_bbox_baturite()

        print("Baturité localizado com sucesso.")
        print(f"GeoJSON criado em: {arquivo}")
        print("Limites geográficos (WGS84):")
        print(f"  Oeste: {bbox['oeste']:.6f}")
        print(f"  Sul:   {bbox['sul']:.6f}")
        print(f"  Leste: {bbox['leste']:.6f}")
        print(f"  Norte: {bbox['norte']:.6f}")

    except Exception as erro:
        print("ERRO AO PROCESSAR A MALHA DO IBGE:")
        print(erro)
