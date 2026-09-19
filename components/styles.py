import streamlit as st


def aplicar_estilos():
    """
    Aplica os estilos visuais globais da aplicação.
    """

    st.markdown(
        """
        <style>

        /* ==============================
           ÁREA PRINCIPAL
        ============================== */

        .main {
            background-color: #f4f8f7;
        }


        /* ==============================
           TÍTULOS
        ============================== */

        h1 {
            color: #1565C0;
            font-weight: 700;
        }

        h2, h3 {
            color: #2E7D32;
        }


        /* ==============================
           MÉTRICAS
        ============================== */

        div[data-testid="stMetric"] {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.10);
            border-left: 6px solid #2E7D32;
        }


        /* ==============================
           BARRA LATERAL
        ============================== */

        section[data-testid="stSidebar"] {
            background: #E8F5E9;
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
