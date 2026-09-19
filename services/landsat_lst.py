from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.mask import mask
import requests

from services.landsat_service import buscar_cenas_landsat


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BATURITE_GEOJSON = PROJECT_ROOT / "data" / "processed" / "baturite.geojson"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "landsat"

ST_SCALE = 0.00341802
ST_OFFSET = 149.0
KELVIN_TO_CELSIUS = 273.15


def baixar_arquivo(url, destino):
    """Baixa um asset Landsat para um arquivo local."""
    with requests.get(url, stream=True, timeout=180) as resposta:
        resposta.raise_for_status()

        with open(destino, "wb") as arquivo:
            for bloco in resposta.iter_content(chunk_size=1024 * 1024):
                if bloco:
                    arquivo.write(bloco)

    return destino


def obter_href_asset(cena, nome):
    """Retorna a URL de um asset específico da cena."""
    asset = cena["assets"].get(nome)

    if asset is None:
        raise KeyError(
            f"O asset '{nome}' não foi encontrado na cena {cena['id']}."
        )

    href = asset.get("href")

    if not href:
        raise ValueError(
            f"O asset '{nome}' não possui URL de acesso."
        )

    return href


def carregar_limite_baturite():
    """Carrega o limite municipal de Baturité em WGS84."""
    if not BATURITE_GEOJSON.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {BATURITE_GEOJSON}"
        )

    gdf = gpd.read_file(BATURITE_GEOJSON)

    if gdf.empty:
        raise ValueError("O GeoJSON de Baturité está vazio.")

    return gdf.to_crs(epsg=4326)


def recortar_raster(caminho_raster, limite):
    """
    Recorta um raster pelo limite de Baturité.
    Retorna matriz, transform e perfil.
    """
    with rasterio.open(caminho_raster) as src:
        limite_no_crs = limite.to_crs(src.crs)

        geometrias = [
            geometria.__geo_interface__
            for geometria in limite_no_crs.geometry
        ]

        dados, transform = mask(
            src,
            geometrias,
            crop=True,
            filled=True,
            nodata=0,
        )

        perfil = src.profile.copy()
        perfil.update(
            height=dados.shape[1],
            width=dados.shape[2],
            transform=transform,
            count=1,
        )

    return dados[0], transform, perfil


def criar_mascara_pixels_validos(temperatura_dn, qa_pixel):
    """
    Cria máscara para Landsat 8/9 Collection 2 QA_PIXEL.

    Remove:
      bit 0 -> fill
      bit 1 -> nuvem dilatada
      bit 2 -> cirrus de alta confiança
      bit 3 -> nuvem de alta confiança
      bit 4 -> sombra de nuvem
      bit 5 -> neve

    Também remove DN=0 da banda de temperatura.
    """
    qa = qa_pixel.astype(np.uint16)

    mascara_ruim = (
        ((qa & (1 << 0)) != 0)
        | ((qa & (1 << 1)) != 0)
        | ((qa & (1 << 2)) != 0)
        | ((qa & (1 << 3)) != 0)
        | ((qa & (1 << 4)) != 0)
        | ((qa & (1 << 5)) != 0)
    )

    return (~mascara_ruim) & (temperatura_dn != 0)


def converter_para_celsius(temperatura_dn, mascara_valida):
    """
    Converte Landsat Collection 2 Level-2 Surface Temperature:
        Kelvin = DN * 0.00341802 + 149
        Celsius = Kelvin - 273.15
    """
    temperatura = np.full(
        temperatura_dn.shape,
        np.nan,
        dtype=np.float32,
    )

    temperatura[mascara_valida] = (
        temperatura_dn[mascara_valida].astype(np.float32)
        * ST_SCALE
        + ST_OFFSET
        - KELVIN_TO_CELSIUS
    )

    return temperatura


def salvar_geotiff(caminho, matriz, perfil):
    """Salva a LST em Celsius como GeoTIFF float32."""
    perfil_saida = perfil.copy()
    perfil_saida.update(
        dtype="float32",
        nodata=np.nan,
        compress="deflate",
    )

    with rasterio.open(caminho, "w", **perfil_saida) as dst:
        dst.write(matriz.astype(np.float32), 1)


def salvar_mapa_png(caminho, temperatura, transform, titulo):
    """Cria uma visualização simples da LST recortada."""
    altura, largura = temperatura.shape

    esquerda = transform.c
    topo = transform.f
    direita = esquerda + transform.a * largura
    baixo = topo + transform.e * altura

    fig, ax = plt.subplots(figsize=(8, 8))

    imagem = ax.imshow(
        temperatura,
        extent=[esquerda, direita, baixo, topo],
        origin="upper",
    )

    ax.set_title(titulo)
    ax.set_xlabel("Coordenada X")
    ax.set_ylabel("Coordenada Y")

    barra = fig.colorbar(imagem, ax=ax)
    barra.set_label("Temperatura da superfície (°C)")

    fig.tight_layout()
    fig.savefig(caminho, dpi=180, bbox_inches="tight")
    plt.close(fig)


def processar_lst_baturite(
    data_inicial=None,
    data_final=None,
    nuvens_max=20,
):
    """
    Seleciona a cena de menor cobertura de nuvens no período,
    baixa ST_B10 e QA_PIXEL, recorta Baturité, mascara pixels
    inadequados e gera LST em Celsius.
    """
    cenas = buscar_cenas_landsat(
        data_inicial=data_inicial,
        data_final=data_final,
        nuvens_max=nuvens_max,
        limite=100,
    )

    if not cenas:
        raise RuntimeError(
            "Nenhuma cena Landsat adequada foi encontrada."
        )

    cena = cenas[0]

    href_st = obter_href_asset(cena, "lwir11")
    href_qa = obter_href_asset(cena, "qa_pixel")

    limite = carregar_limite_baturite()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    nome_base = cena["id"].replace("_ST", "")
    saida_tif = OUTPUT_DIR / f"{nome_base}_LST_BATURITE.tif"
    saida_png = OUTPUT_DIR / f"{nome_base}_LST_BATURITE.png"

    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        arquivo_st = temp_dir / "ST_B10.TIF"
        arquivo_qa = temp_dir / "QA_PIXEL.TIF"

        print("Baixando banda de temperatura...")
        baixar_arquivo(href_st, arquivo_st)

        print("Baixando QA_PIXEL...")
        baixar_arquivo(href_qa, arquivo_qa)

        print("Recortando os rasters para Baturité...")
        st_dn, transform_st, perfil_st = recortar_raster(
            arquivo_st,
            limite,
        )
        qa_pixel, _, _ = recortar_raster(
            arquivo_qa,
            limite,
        )

    if st_dn.shape != qa_pixel.shape:
        raise RuntimeError(
            "ST_B10 e QA_PIXEL ficaram com dimensões diferentes."
        )

    mascara_valida = criar_mascara_pixels_validos(
        st_dn,
        qa_pixel,
    )

    temperatura = converter_para_celsius(
        st_dn,
        mascara_valida,
    )

    total_pixels_municipio = np.count_nonzero(st_dn != 0)
    pixels_validos = np.count_nonzero(np.isfinite(temperatura))

    if total_pixels_municipio == 0:
        raise RuntimeError(
            "Nenhum pixel Landsat válido foi encontrado no recorte."
        )

    percentual_valido = (
        pixels_validos / total_pixels_municipio * 100
    )

    valores = temperatura[np.isfinite(temperatura)]

    if valores.size == 0:
        raise RuntimeError(
            "Todos os pixels de Baturité foram removidos pela "
            "máscara de qualidade."
        )

    estatisticas = {
        "media": float(np.mean(valores)),
        "mediana": float(np.median(valores)),
        "minima": float(np.min(valores)),
        "maxima": float(np.max(valores)),
        "desvio_padrao": float(np.std(valores)),
        "pixels_validos": int(pixels_validos),
        "percentual_valido": float(percentual_valido),
    }

    salvar_geotiff(
        saida_tif,
        temperatura,
        perfil_st,
    )

    salvar_mapa_png(
        saida_png,
        temperatura,
        transform_st,
        (
            "Temperatura de Superfície (LST) — Baturité-CE\n"
            f"{cena['data_hora'][:10]} | {cena['plataforma']}"
        ),
    )

    return {
        "cena": cena,
        "estatisticas": estatisticas,
        "geotiff": saida_tif,
        "mapa_png": saida_png,
    }


if __name__ == "__main__":
    try:
        print("Processando LST de Baturité-CE...")
        print()

        resultado = processar_lst_baturite(
            nuvens_max=20,
        )

        cena = resultado["cena"]
        stats = resultado["estatisticas"]

        print()
        print("=" * 60)
        print("PROCESSAMENTO CONCLUÍDO")
        print("=" * 60)
        print(f"Cena: {cena['id']}")
        print(f"Data: {cena['data_hora']}")
        print(f"Satélite: {cena['plataforma']}")
        print(f"Nuvens da cena: {cena['nuvens']:.2f}%")
        print()
        print("Baturité após máscara de qualidade:")
        print(f"  Pixels válidos: {stats['pixels_validos']}")
        print(f"  Área raster válida: {stats['percentual_valido']:.2f}%")
        print()
        print("LST dos pixels válidos:")
        print(f"  Média: {stats['media']:.2f} °C")
        print(f"  Mediana: {stats['mediana']:.2f} °C")
        print(f"  Mínima: {stats['minima']:.2f} °C")
        print(f"  Máxima: {stats['maxima']:.2f} °C")
        print(f"  Desvio padrão: {stats['desvio_padrao']:.2f} °C")
        print()
        print(f"GeoTIFF: {resultado['geotiff']}")
        print(f"Mapa PNG: {resultado['mapa_png']}")

    except Exception as erro:
        print()
        print("ERRO AO PROCESSAR LST:")
        print(erro)
