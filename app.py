import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import requests

# --- Função para carregar animações do Lottie ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Estilo customizado ---
st.markdown("""
    <style>
    html, body, [class*="css"] {
        background-color: #0e1117;
        color: #f5f5f5;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        padding: 0.6em 1.2em;
        border-radius: 8px;
        transition: 0.3s;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff7f0e;
        color: black;
        transform: scale(1.05);
    }
    .stTextInput>div>div>input {
        background-color: #1e1e1e;
        color: white;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Lottie Animation (Topo do app) ---
lottie = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_ydo1amjm.json")
with st.container():
    col_anim, col_title = st.columns([1, 3])
    with col_anim:
        st_lottie(lottie, height=100, key="data_anim")
    with col_title:
        st.title("📊 Dashboard de Salários na Área de Dados")
        st.markdown("Explore os dados salariais da área de tecnologia com filtros e gráficos interativos.")

# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

anos_selecionados = st.sidebar.multiselect("Ano", sorted(df['ano'].unique()), default=sorted(df['ano'].unique()))
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", sorted(df['senioridade'].unique()), default=sorted(df['senioridade'].unique()))
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", sorted(df['contrato'].unique()), default=sorted(df['contrato'].unique()))
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", sorted(df['tamanho_empresa'].unique()), default=sorted(df['tamanho_empresa'].unique()))

# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Métricas Principais (KPIs) ---
st.markdown("## 📌 Métricas gerais (Salário anual em USD)")
if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Salário médio", f"${salario_medio:,.0f}")
col2.metric("🚀 Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("📄 Total de registros", f"{total_registros:,}")
col4.metric("👔 Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Gráficos ---
st.subheader("📈 Visualizações")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)'}
        )
        grafico_hist.update_layout(title_x=0.1, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1, font_color='white')
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1, geo_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados ---
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtrado, use_container_width=True)