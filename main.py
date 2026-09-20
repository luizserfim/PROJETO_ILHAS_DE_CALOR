import streamlit as st
from matplotlib.figure import Figure

from services.funceme import ErroFunceme, obter_temperatura_atual
from models.modelo_termico import estimar_temperatura, comparar_intervencao
from components.styles import aplicar_estilos


st.set_page_config(
    page_title="Simulador de Ilhas de Calor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_estilos()

st.markdown(
    """
    # 🌍 Simulador de Ilhas de Calor Urbanas
    ### Município de Baturité - Ceará

    Ferramenta educacional para análise da influência da cobertura do solo
    sobre o comportamento térmico urbano.
    """
)

# Cenários ficam salvos apenas enquanto esta sessão do aplicativo estiver ativa.
if "cenarios_salvos" not in st.session_state:
    st.session_state.cenarios_salvos = []

if "nome_regiao" not in st.session_state:
    st.session_state.nome_regiao = ""
if "vegetacao" not in st.session_state:
    st.session_state.vegetacao = 15
if "pavimento" not in st.session_state:
    st.session_state.pavimento = 40
if "edificacoes" not in st.session_state:
    st.session_state.edificacoes = 35
if "solo_exposto" not in st.session_state:
    st.session_state.solo_exposto = 5
if "agua" not in st.session_state:
    st.session_state.agua = 5


def nova_analise():
    """Limpa somente o formulário; os cenários já salvos permanecem na sessão."""
    st.session_state.nome_regiao = ""
    st.session_state.vegetacao = 15
    st.session_state.pavimento = 40
    st.session_state.edificacoes = 35
    st.session_state.solo_exposto = 5
    st.session_state.agua = 5


aba1, aba2, aba3, aba4 = st.tabs([
    "📖 Introdução",
    "📚 Fundamentação Teórica",
    "🌡️ Simulador",
    "📊 Metodologia e Resultados",
])


with aba1:
    st.header("📖 Introdução")

    st.write(
        """
        O crescimento e a transformação das áreas urbanas modificam
        significativamente as características naturais da superfície,
        principalmente pela substituição da vegetação por edificações,
        pavimentos e outras superfícies impermeáveis.

        Este projeto apresenta um simulador computacional desenvolvido
        para estudar a influência da cobertura do solo sobre o comportamento
        térmico urbano no município de Baturité, Ceará.

        A ferramenta integra dados meteorológicos da FUNCEME com um modelo
        térmico urbano didático e permite comparar diferentes cenários de
        cobertura do solo e possíveis intervenções urbanas.
        """
    )

    st.info(
        "O simulador tem finalidade educacional. As temperaturas calculadas "
        "representam estimativas do modelo e não medições diretas dos bairros."
    )


with aba2:
    st.header("📚 Fundamentação Teórica")

    st.subheader("Ilhas de Calor Urbanas")
    st.write(
        """
        A urbanização altera as propriedades da superfície e pode modificar
        as trocas de energia entre o solo, a atmosfera e as construções.
        Regiões com maior presença de superfícies impermeáveis e menor
        cobertura vegetal podem apresentar condições térmicas diferentes
        de áreas mais vegetadas.
        """
    )

    st.subheader("Cobertura do solo")
    st.write(
        """
        No modelo são consideradas cinco classes de cobertura: vegetação,
        pavimento, edificações, solo exposto e água. Cada uma recebe um peso
        térmico no modelo didático, permitindo comparar diferentes
        configurações urbanas.
        """
    )

    st.subheader("Vegetação e urbanização")
    st.write(
        """
        A vegetação é representada no modelo com efeito de redução térmica,
        enquanto pavimentos, edificações e solo exposto contribuem
        positivamente para o índice térmico. A água também é representada
        com efeito de redução térmica.
        """
    )

    st.subheader("Temperatura de referência")
    st.write(
        """
        O simulador consulta a estação Baturité - APA, da FUNCEME, e utiliza
        a temperatura meteorológica disponível como referência para o cálculo
        dos cenários simulados.
        """
    )


with aba3:
    st.header("🌡️ Simulador")

    st.info(
        "📘 A temperatura urbana apresentada é uma estimativa do modelo "
        "didático e não uma medição meteorológica direta da região selecionada."
    )

    st.sidebar.header("⚙️ Painel de Controle")

    st.sidebar.subheader("📍 Região analisada")

    bairro_selecionado = st.sidebar.text_input(
        "Nome da região ou local:",
        placeholder="Ex.: Centro, bairro, praça ou comunidade",
        key="nome_regiao",
        max_chars=100,
    )

    st.sidebar.caption(
        "Escolha uma área que você conheça e informe abaixo uma estimativa "
        "da cobertura do solo. Assim, você poderá construir e comparar "
        "seu próprio cenário."
    )

    st.sidebar.subheader("📊 Dados da região")
    st.sidebar.caption(
        "Informe as porcentagens aproximadas de cada tipo de cobertura. "
        "A soma deve ser igual a 100%."
    )

    vegetacao = st.sidebar.slider(
        "🌳 Vegetação (%)", min_value=0, max_value=100, step=1,
        help="Árvores, gramados, jardins e outras áreas verdes.",
        key="vegetacao",
    )

    pavimento = st.sidebar.slider(
        "🛣️ Pavimento (%)", min_value=0, max_value=100, step=1,
        help="Ruas, asfalto, calçadas, concreto e outras superfícies pavimentadas.",
        key="pavimento",
    )

    edificacoes = st.sidebar.slider(
        "🏢 Edificações (%)", min_value=0, max_value=100, step=1,
        help="Casas, prédios e demais áreas ocupadas por construções.",
        key="edificacoes",
    )

    solo_exposto = st.sidebar.slider(
        "🟫 Solo exposto (%)", min_value=0, max_value=100, step=1,
        help="Terrenos ou superfícies de solo sem cobertura vegetal.",
        key="solo_exposto",
    )

    agua = st.sidebar.slider(
        "💧 Água (%)", min_value=0, max_value=100, step=1,
        help="Rios, açudes, lagos e outras superfícies de água.",
        key="agua",
    )

    st.sidebar.info(
        "💡 Você pode estimar esses valores observando a região, mapas ou "
        "imagens de satélite. Não é necessário usar uma região predefinida."
    )

    if not bairro_selecionado.strip():
        bairro_selecionado = "Cenário personalizado"

    soma_cobertura = vegetacao + pavimento + edificacoes + solo_exposto + agua
    cobertura_valida = soma_cobertura == 100

    if cobertura_valida:
        st.sidebar.success("✅ Cobertura total: 100%")
    else:
        st.sidebar.warning(
            f"⚠️ Cobertura total: {soma_cobertura}%. A soma precisa ser 100%."
        )

    col_salvar, col_novo = st.sidebar.columns(2)

    with col_salvar:
        salvar = st.button(
            "💾 Salvar",
            width="stretch",
            disabled=not cobertura_valida or len(st.session_state.cenarios_salvos) >= 50,
        )

    with col_novo:
        st.button(
            "➕ Nova análise",
            width="stretch",
            on_click=nova_analise,
        )

    if len(st.session_state.cenarios_salvos) >= 50:
        st.sidebar.info("Limite de 50 cenários por sessão atingido.")
    if st.sidebar.button("Limpar cenários salvos"):
        st.session_state.cenarios_salvos = []
        st.rerun()

    if salvar and cobertura_valida and len(st.session_state.cenarios_salvos) < 50:
        nome_salvo = bairro_selecionado.strip() or f"Cenário {len(st.session_state.cenarios_salvos) + 1}"

        st.session_state.cenarios_salvos.append(
            {
                "regiao": nome_salvo,
                "vegetacao": vegetacao,
                "pavimento": pavimento,
                "edificacoes": edificacoes,
                "solo_exposto": solo_exposto,
                "agua": agua,
            }
        )
        st.sidebar.success("Cenário salvo nesta sessão.")

    if st.session_state.cenarios_salvos:
        with st.sidebar.expander(
            f"📁 Cenários salvos ({len(st.session_state.cenarios_salvos)})"
        ):
            for i, cenario in enumerate(st.session_state.cenarios_salvos, start=1):
                st.text(
                    f"{i}. {cenario['regiao']}\n"
                    f"Vegetação: {cenario['vegetacao']}% · "
                    f"Pavimento: {cenario['pavimento']}% · "
                    f"Edificações: {cenario['edificacoes']}% · "
                    f"Solo: {cenario['solo_exposto']}% · "
                    f"Água: {cenario['agua']}%"
                )

    st.sidebar.markdown("### 🌡️ Dados meteorológicos")

    @st.cache_data(ttl=600, max_entries=1, show_spinner=False)
    def carregar_dados_funceme():
        # Falhas também são cacheadas para evitar repetição a cada slider.
        try:
            return obter_temperatura_atual()
        except ErroFunceme:
            return None

    try:
        dados_funceme = carregar_dados_funceme()
        if dados_funceme is None:
            raise ErroFunceme("Fonte indisponível.")
        temp_referencia = float(dados_funceme["temperatura_media"])
        temp_maxima = float(dados_funceme["temperatura_maxima"])
        temp_minima = float(dados_funceme["temperatura_minima"])
        horario_observacao = dados_funceme["data_hora"]
        fonte_temperatura = "FUNCEME"

        st.sidebar.success("FUNCEME — dados disponíveis")
        st.sidebar.metric("Temperatura de referência", f"{temp_referencia:.1f} °C")
        st.sidebar.caption(f"Máxima horária: {temp_maxima:.1f} °C")
        st.sidebar.caption(f"Mínima horária: {temp_minima:.1f} °C")
        st.sidebar.caption(f"Estação: {dados_funceme['estacao']}")
        st.sidebar.caption(
            "Observação: "
            f"{horario_observacao.strftime('%d/%m/%Y às %H:%M')}"
        )

    except ErroFunceme:
        dados_funceme = None
        fonte_temperatura = "Entrada manual"
        st.sidebar.warning(
            "⚠️ Não foi possível consultar a FUNCEME automaticamente."
        )
        temp_referencia = st.sidebar.number_input(
            "Temperatura de referência (°C)",
            min_value=-90.0,
            max_value=60.0,
            value=30.0,
            step=0.1,
        )
        st.sidebar.caption("Temperatura manual utilizada como contingência.")

    resultado = None

    if cobertura_valida:
        try:
            resultado = estimar_temperatura(
                temperatura_referencia=temp_referencia,
                vegetacao=vegetacao,
                pavimento=pavimento,
                edificacoes=edificacoes,
                solo_exposto=solo_exposto,
                agua=agua,
            )
        except ValueError as erro:
            st.error(f"Erro no modelo: {erro}")

    st.subheader("📊 Cenário analisado")
    st.text(bairro_selecionado)

    if resultado is not None:
        indice_termico = resultado["indice_termico"]
        delta_t = resultado["anomalia_termica"]
        temp_estimada = resultado["temperatura_estimada"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperatura de referência", f"{temp_referencia:.1f} °C")
        col2.metric("Índice térmico", f"{indice_termico:+.3f}")
        col3.metric("Anomalia térmica (ΔT)", f"{delta_t:+.2f} °C")
        col4.metric("Temperatura simulada", f"{temp_estimada:.1f} °C")

        if fonte_temperatura == "FUNCEME":
            st.caption(
                "A temperatura de referência é uma observação da estação "
                "Baturité - APA/FUNCEME. A temperatura simulada é resultado "
                "do modelo didático de cobertura do solo."
            )
    else:
        st.warning(
            "A simulação será executada quando a cobertura do solo totalizar 100%."
        )

    st.divider()
    st.subheader("🌳 Simulação de intervenção urbana")

    tipo_intervencao = st.selectbox(
        "Tipo de intervenção:",
        [
            "Pavimento → Vegetação",
            "Solo exposto → Vegetação",
            "Edificações → Vegetação",
        ],
    )

    origens = {
        "Pavimento → Vegetação": pavimento,
        "Solo exposto → Vegetação": solo_exposto,
        "Edificações → Vegetação": edificacoes,
    }

    area_disponivel = origens[tipo_intervencao]
    limite_intervencao = min(50, area_disponivel, 100 - vegetacao)

    if limite_intervencao > 0:
        percentual_convertido = st.slider(
            "Área convertida em vegetação (pontos percentuais)",
            min_value=0,
            max_value=limite_intervencao,
            value=min(10, limite_intervencao),
        )
    else:
        percentual_convertido = 0
        st.info("Não há área disponível para esta intervenção.")

    comparacao = None

    if resultado is not None:
        try:
            comparacao = comparar_intervencao(
                temperatura_referencia=temp_referencia,
                vegetacao=vegetacao,
                pavimento=pavimento,
                edificacoes=edificacoes,
                solo_exposto=solo_exposto,
                agua=agua,
                percentual_convertido=percentual_convertido,
                tipo_intervencao=tipo_intervencao,
            )
        except ValueError as erro:
            st.error(f"Erro na intervenção: {erro}")

    if comparacao is not None:
        futuro = comparacao["cenario_intervencao"]
        novas = comparacao["coberturas_intervencao"]
        reducao = comparacao["reducao_estimada"]

        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Temperatura atual simulada",
            f"{resultado['temperatura_estimada']:.1f} °C",
        )
        col2.metric(
            "Após intervenção",
            f"{futuro['temperatura_estimada']:.1f} °C",
        )
        col3.metric("Redução estimada", f"{reducao:.2f} °C")

        st.markdown("#### Alterações na cobertura do solo")

        tabela_cobertura = {
            "Cobertura": [
                "Vegetação",
                "Pavimento",
                "Edificações",
                "Solo exposto",
                "Água",
            ],
            "Atual (%)": [
                vegetacao,
                pavimento,
                edificacoes,
                solo_exposto,
                agua,
            ],
            "Após intervenção (%)": [
                novas["vegetacao"],
                novas["pavimento"],
                novas["edificacoes"],
                novas["solo_exposto"],
                novas["agua"],
            ],
        }

        st.dataframe(
            tabela_cobertura,
            hide_index=True,
            width="stretch",
        )

    st.divider()
    st.subheader("📈 Visualização dos resultados")

    if comparacao is not None:
        futuro = comparacao["cenario_intervencao"]
        novas = comparacao["coberturas_intervencao"]

        col_grafico1, col_grafico2 = st.columns(2)

        with col_grafico1:
            st.markdown("#### Temperatura: antes e depois")

            valores_temperatura = [
                resultado["temperatura_estimada"],
                futuro["temperatura_estimada"],
            ]
            categorias_temperatura = [
                "Cenário atual",
                "Após intervenção",
            ]

            fig1 = Figure(figsize=(7, 4))
            ax1 = fig1.subplots()
            barras = ax1.bar(
                categorias_temperatura,
                valores_temperatura,
            )

            ax1.axhline(
                temp_referencia,
                linestyle="--",
                label=f"Referência ({temp_referencia:.1f} °C)",
            )

            menor_temp = min(temp_referencia, *valores_temperatura)
            maior_temp = max(temp_referencia, *valores_temperatura)
            ax1.set_ylim(menor_temp - 2, maior_temp + 2)
            ax1.set_ylabel("Temperatura (°C)")
            ax1.legend()
            ax1.grid(axis="y", alpha=0.2)

            for barra, valor in zip(barras, valores_temperatura):
                ax1.text(
                    barra.get_x() + barra.get_width() / 2,
                    valor + 0.08,
                    f"{valor:.1f} °C",
                    ha="center",
                    va="bottom",
                )

            fig1.tight_layout()
            st.pyplot(fig1)

        with col_grafico2:
            st.markdown("#### Cobertura do solo")

            classes = [
                "Vegetação",
                "Pavimento",
                "Edificações",
                "Solo",
                "Água",
            ]

            valores_atuais = [
                vegetacao,
                pavimento,
                edificacoes,
                solo_exposto,
                agua,
            ]

            valores_futuros = [
                novas["vegetacao"],
                novas["pavimento"],
                novas["edificacoes"],
                novas["solo_exposto"],
                novas["agua"],
            ]

            posicoes = list(range(len(classes)))
            largura = 0.38

            fig2 = Figure(figsize=(7, 4))
            ax2 = fig2.subplots()

            ax2.bar(
                [x - largura / 2 for x in posicoes],
                valores_atuais,
                width=largura,
                label="Atual",
            )
            ax2.bar(
                [x + largura / 2 for x in posicoes],
                valores_futuros,
                width=largura,
                label="Após intervenção",
            )

            ax2.set_xticks(posicoes)
            ax2.set_xticklabels(classes, rotation=25, ha="right")
            ax2.set_ylabel("Cobertura (%)")
            ax2.set_ylim(0, 100)
            ax2.legend()
            ax2.grid(axis="y", alpha=0.2)

            fig2.tight_layout()
            st.pyplot(fig2)

    else:
        st.info(
            "As visualizações serão apresentadas quando a cobertura do solo "
            "totalizar 100%."
        )


with aba4:
    st.header("📊 Metodologia e Resultados")

    st.subheader("Modelo térmico")

    st.markdown(
        "O simulador utiliza um **Índice Térmico Urbano Didático**:"
    )

    st.latex(
        r"I_T = \frac{-0{,}35V + 0{,}40P + 0{,}30E + 0{,}15S - 0{,}20A}{100}"
    )

    st.markdown(
        """
        em que:

        - **V** representa a porcentagem de vegetação;
        - **P** representa a porcentagem de pavimento;
        - **E** representa a porcentagem de edificações;
        - **S** representa a porcentagem de solo exposto;
        - **A** representa a porcentagem de água.

        A anomalia térmica é calculada por:
        """
    )

    st.latex(r"\Delta T = 10 I_T")

    st.markdown("com limite de **-2 °C a +3 °C**.")

    st.markdown("Finalmente:")

    st.latex(
        r"T_{\mathrm{simulada}} = T_{\mathrm{referência}} + \Delta T"
    )

    st.subheader("Dados meteorológicos")
    st.write(
        """
        A temperatura de referência é obtida automaticamente da estação
        Baturité - APA, da FUNCEME. Caso a consulta automática não esteja
        disponível, o simulador permite informar uma temperatura de
        referência manualmente.
        """
    )

    st.subheader("Validação computacional")
    st.info("O projeto inclui testes automatizados do modelo, da integração meteorológica e da interface. Consulte o README para executá-los.")

    st.write(
        """
        Os testes verificam a soma das coberturas, valores inválidos,
        comportamento do cenário padrão, efeito do aumento da vegetação,
        intervenções e limites da anomalia térmica.
        """
    )

    st.subheader("Intervenções urbanas")
    st.write(
        """
        O simulador permite comparar o cenário atual com intervenções
        simplificadas que convertem pavimento, solo exposto ou edificações
        em vegetação. A ferramenta recalcula automaticamente o índice
        térmico e a temperatura simulada.
        """
    )

    st.subheader("Limitações")
    st.warning(
        "Os pesos térmicos utilizados são parâmetros de um modelo didático "
        "simplificado e não coeficientes experimentais calibrados para os "
        "bairros de Baturité. Portanto, os resultados devem ser interpretados "
        "como comparação entre cenários, e não como previsão meteorológica."
    )
