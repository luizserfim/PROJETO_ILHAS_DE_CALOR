import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Simulador de Ilhas de Calor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================
# CSS PERSONALIZADO
# ==========================

st.markdown("""
<style>

.main{
    background-color:#f4f8f7;
}

h1{
    color:#1565C0;
    font-weight:700;
}

h2,h3{
    color:#2E7D32;
}

div[data-testid="stMetric"]{
    background:white;
    border-radius:15px;
    padding:20px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.10);
    border-left:6px solid #2E7D32;
}

section[data-testid="stSidebar"]{
    background:#E8F5E9;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# CABEÇALHO
# ==========================

st.markdown("""
# 🌍 Simulador de Ilhas de Calor Urbanas

### Município de Baturité - Ceará

Sistema de apoio à análise térmica urbana baseado
na cobertura do solo e temperatura observada.

---
""")
st.markdown("Ajuste os parâmetros dos bairros para prever a temperatura e simular cenários de arborização.")

# --- BARRA LATERAL: ENTRADA DE DADOS DO USUÁRIO (Etapas 6, 7 e 9) ---
st.sidebar.header("⚙️ Painel de Controle de Variáveis")

bairro_selecionado = st.sidebar.selectbox("Selecione o Bairro para Analisar:", 
                                         ["Centro", "Bairro Residencial", "Área Rural", "Praça Principal"])

st.sidebar.subheader("Porcentagem de Cobertura do Solo (%)")
arvores = st.sidebar.slider("Árvores / Vegetação (%)", 0, 100, 15)
asfalto = st.sidebar.slider("Asfalto / Pavimento (%)", 0, 100, 40)
construcoes = st.sidebar.slider("Construções / Prédios (%)", 0, 100, 35)
agua = st.sidebar.slider("Água / Solo Exposto (%)", 0, 100, 10)

# Alerta caso a soma passe de 100%
soma = arvores + asfalto + construcoes + agua
if soma != 100:
    st.sidebar.warning(f"⚠️ A soma das áreas é {soma}%. O ideal é fechar em 100%.")

temp_inmet = st.sidebar.number_input("Temperatura Base INMET (°C):", value=31.0)

# --- CÁLCULO DO ÍNDICE E TEMPERATURA (Etapa 10) ---
indice = (0.4 * asfalto) + (0.3 * construcoes) - (0.2 * arvores) - (0.1 * agua)
ajuste_termico = (indice - 10) * 0.15
temp_estimada = temp_inmet + ajuste_termico

# Classificação da Ilha de Calor (Etapa 11)
if temp_estimada >= 33.0:
    status = "🔴 Crítico (Muito Quente)"
elif temp_estimada >= 31.5:
    status = "🟠 Moderado (Quente)"
else:
    status = "🟢 Ideal (Fresco)"

# --- PAINEL PRINCIPAL (RESULTADOS E SIMULAÇÃO) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📊 Diagnóstico: {bairro_selecionado}")
    st.metric("Temperatura Estimada", f"{temp_estimada:.1f} °C")
    st.metric("Índice Térmico Calculado", f"{indice:.1f}")
    st.write(f"**Classificação:** {status}")

with col2:
    st.subheader("🧪 Simulação de Intervenção Urbana (Etapa 12)")
    st.write("O que acontece se plantarmos mais árvores?")
    
    arvores_novas = st.slider("Simular acréscimo de árvores (%)", 0, 50, 10)
    
    # Recálculo simulado
    asfalto_simulado = max(0, asfalto - arvores_novas)
    arvores_simuladas = arvores + arvores_novas
    
    novo_indice = (0.4 * asfalto_simulado) + (0.3 * construcoes) - (0.2 * arvores_simuladas) - (0.1 * agua)
    nova_temp = temp_inmet + ((novo_indice - 10) * 0.15)
    
    reducao = temp_estimada - nova_temp
    st.success(f"🌱 Redução Térmica Prevista: **-{reducao:.2f} °C**")
    st.write(f"Nova Temperatura do Bairro: **{nova_temp:.1f} °C**")

# --- GRÁFICO TÉRMICO INTERATIVO ---
st.divider()
st.subheader("📈 Comparativo dos Cenários")

fig, ax = plt.subplots(figsize=(8, 3))
categorias = ['Temperatura Atual', 'Após Arborização (Simulado)']
valores = [temp_estimada, nova_temp]
cores = ['#e74c3c', '#2ecc71']

ax.barh(categorias, valores, color=cores)
ax.set_xlim(25, 38)
ax.axvline(temp_inmet, color='gray', linestyle='--', label=f'Base INMET ({temp_inmet}°C)')
ax.legend()

st.pyplot(fig)
