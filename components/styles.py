import streamlit as st


def aplicar_estilos():
    """
    Aplica os estilos visuais globais da aplicação.
    Tema principal: azul.
    """

    st.markdown(
        """
        <style>

        /* ==============================
           ÁREA PRINCIPAL
        ============================== */
        .main {
            background-color: #F4F8FC;
        }


        /* ==============================
           TÍTULOS DA ÁREA PRINCIPAL
        ============================== */
        h1 {
            color: #0D47A1;
            font-weight: 700;
        }

        h2,
        h3 {
            color: #1565C0;
        }


        /* ==============================
           MÉTRICAS
        ============================== */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.10);
            border-left: 6px solid #1976D2;
        }


        /* ==============================
           BARRA LATERAL
        ============================== */
        section[data-testid="stSidebar"] {
            background-color: #EAF3FC;
        }


        /* ==============================
           TÍTULOS DA BARRA LATERAL
        ============================== */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #0D47A1 !important;
            font-weight: 700 !important;
        }


        /* ==============================
           TEXTOS DA BARRA LATERAL
        ============================== */
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {
            color: #173B63 !important;
        }


        /* ==============================
           TEXTOS EXPLICATIVOS
        ============================== */
        section[data-testid="stSidebar"]
        [data-testid="stCaptionContainer"],
        section[data-testid="stSidebar"]
        [data-testid="stCaptionContainer"] p {
            color: #496A8C !important;
        }


        /* ==============================
           SLIDERS
        ============================== */
        section[data-testid="stSidebar"]
        [data-testid="stSlider"] label p {
            color: #0D47A1 !important;
            font-weight: 600 !important;
        }


        /* ==============================
           CAMPO DE TEXTO
        ============================== */
        section[data-testid="stSidebar"]
        [data-testid="stTextInput"] label p {
            color: #0D47A1 !important;
            font-weight: 600 !important;
        }

        section[data-testid="stSidebar"]
        [data-testid="stTextInput"] input {
            color: #F5F5F5 !important;
            background-color: #102A43 !important;
            border-radius: 8px;
        }

        section[data-testid="stSidebar"]
        [data-testid="stTextInput"] input::placeholder {
            color: #B8C7D9 !important;
            opacity: 1;
        }


        /* ==============================
           BOTÕES DA BARRA LATERAL
        ============================== */
        section[data-testid="stSidebar"] button {
            color: #0D47A1;
            font-weight: 600;
        }


        /* ==============================
           MENSAGENS DA BARRA LATERAL
        ============================== */
        section[data-testid="stSidebar"]
        [data-testid="stAlert"] p {
            color: inherit !important;
        }


        /* ==============================
           MÉTRICAS NO TEMA ESCURO
        ============================== */
        @media (prefers-color-scheme: dark) {

            div[data-testid="stMetric"] {
                background-color: #172033;
                border-left: 6px solid #42A5F5;
            }

            div[data-testid="stMetric"] label,
            div[data-testid="stMetric"] p {
                color: #F5F5F5;
            }
        }


        /* ==============================
           RODAPÉ PADRÃO DO STREAMLIT
        ============================== */
        footer {
            visibility: hidden;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )