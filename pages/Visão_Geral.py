import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title="Visão Geral - Spotify Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Visão Geral dos Dados Musicais")
st.markdown("### Análise exploratória das principais características do dataset")

# Carrega os dados
df = carregar_dados()

# Sidebar com filtros
st.sidebar.header("🔧 Filtros de Análise")

# Filtro por gênero principal
generos_disponiveis = ['Todos'] + sorted(df['genero_principal'].unique().tolist())
genero_selecionado = st.sidebar.selectbox(
    "Selecione o Gênero Principal:",
    generos_disponiveis
)

# Filtro por faixa de popularidade
popularidade_min, popularidade_max = st.sidebar.slider(
    "Faixa de Popularidade:",
    min_value=0,
    max_value=100,
    value=(0, 100),
    step=5
)

# Filtro por explícito
filtro_explicito = st.sidebar.radio(
    "Conteúdo Explícito:",
    ["Todos", "Apenas Explícitas", "Apenas Não Explícitas"]
)

# Aplicar filtros
df_filtrado = df.copy()

if genero_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['genero_principal'] == genero_selecionado]

df_filtrado = df_filtrado[
    (df_filtrado['popularity'] >= popularidade_min) & 
    (df_filtrado['popularity'] <= popularidade_max)
]

if filtro_explicito == "Apenas Explícitas":
    df_filtrado = df_filtrado[df_filtrado['explicit'] == True]
elif filtro_explicito == "Apenas Não Explícitas":
    df_filtrado = df_filtrado[df_filtrado['explicit'] == False]

# Métricas após filtros
st.subheader("📈 Métricas dos Dados Filtrados")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Faixas Filtradas", f"{len(df_filtrado):,}")
with col2:
    st.metric("Artistas Únicos", f"{df_filtrado['primeiro_artista'].nunique():,}")
with col3:
    st.metric("Popularidade Média", f"{df_filtrado['popularity'].mean():.1f}")
with col4:
    st.metric("Duração Média", f"{df_filtrado['duration_min'].mean():.1f} min")
with col5:
    st.metric("% Explícitas", f"{(df_filtrado['explicit'].sum() / len(df_filtrado) * 100):.1f}%")

# Layout em duas colunas para gráficos
col1, col2 = st.columns(2)

# Gráfico 1: Top 10 Gêneros
with col1:
    st.subheader("🎸 Top 10 Gêneros Musicais")
    
    top_genres = df_filtrado['track_genre'].value_counts().head(10)
    
    fig_genres = px.bar(
        x=top_genres.values,
        y=top_genres.index,
        orientation='h',
        title="Distribuição dos Gêneros Mais Populares",
        labels={'x': 'Número de Faixas', 'y': 'Gênero Musical'},
        color=top_genres.values,
        color_continuous_scale='Viridis'
    )
    fig_genres.update_layout(height=400, showlegend=False, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_genres, use_container_width=True)

# Gráfico 2: Distribuição de Popularidade
with col2:
    st.subheader("⭐ Distribuição de Popularidade")
    
    fig_pop = px.histogram(
        df_filtrado,
        x='popularity',
        nbins=20,
        title="Distribuição da Popularidade das Faixas",
        labels={'popularity': 'Popularidade', 'count': 'Número de Faixas'},
        color_discrete_sequence=['#1DB954']
    )
    fig_pop.update_layout(height=400)
    st.plotly_chart(fig_pop, use_container_width=True)

# Gráfico 3: Gêneros Principais (Pizza)
st.subheader("🎼 Distribuição por Gêneros Principais")
col1, col2 = st.columns(2)

with col1:
    generos_principais = df_filtrado['genero_principal'].value_counts()
    
    fig_pizza = px.pie(
        values=generos_principais.values,
        names=generos_principais.index,
        title="Proporção dos Gêneros Principais"
    )
    fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
    fig_pizza.update_layout(height=400)
    st.plotly_chart(fig_pizza, use_container_width=True)

# Gráfico 4: Duração vs Popularidade (Scatter)
with col2:
    st.subheader("⏱️ Duração vs Popularidade")
    
    # Amostra para melhor visualização
    df_sample = df_filtrado.sample(n=min(2000, len(df_filtrado)), random_state=42)
    
    fig_scatter = px.scatter(
        df_sample,
        x='duration_min',
        y='popularity',
        color='genero_principal',
        title="Relação entre Duração e Popularidade",
        labels={'duration_min': 'Duração (minutos)', 'popularity': 'Popularidade'},
        opacity=0.6
    )
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)

# Gráfico 5: Características Musicais Médias (Radar Chart) - INTERATIVO
st.subheader("🎵 Características Musicais Médias por Gênero Principal")

# Widget para seleção de gênero para o radar
generos_radar = st.multiselect(
    "Selecione até 3 gêneros para comparação:",
    options=sorted(df_filtrado['genero_principal'].unique()),
    default=sorted(df_filtrado['genero_principal'].unique())[:3] if len(df_filtrado['genero_principal'].unique()) >= 3 else sorted(df_filtrado['genero_principal'].unique()),
    max_selections=3
)

if generos_radar:
    # Características musicais para análise
    caracteristicas = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']
    
    fig_radar = go.Figure()
    
    cores = ['#1DB954', '#FF6B35', '#4ECDC4']
    
    for i, genero in enumerate(generos_radar):
        dados_genero = df_filtrado[df_filtrado['genero_principal'] == genero]
        valores_medios = [dados_genero[carac].mean() for carac in caracteristicas]
        
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_medios,
            theta=caracteristicas,
            fill='toself',
            name=genero,
            line_color=cores[i % len(cores)]
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Perfil de Características Musicais por Gênero",
        height=500
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

# Gráfico 6: Matriz de Correlação (Heatmap)
st.subheader("🔗 Matriz de Correlação das Características Musicais")

# Seleciona apenas colunas numéricas para correlação
caracteristicas_numericas = ['popularity', 'duration_min', 'danceability', 'energy', 'loudness', 
                           'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']

correlacao = df_filtrado[caracteristicas_numericas].corr()

fig_corr = px.imshow(
    correlacao,
    text_auto=True,
    aspect="auto",
    title="Correlações entre Características Musicais",
    color_continuous_scale='RdBu_r'
)
fig_corr.update_layout(height=600)
st.plotly_chart(fig_corr, use_container_width=True)

# Análise adicional - Top Artistas
st.subheader("🎤 Top 15 Artistas por Número de Faixas")

top_artistas = df_filtrado['primeiro_artista'].value_counts().head(15)

fig_artistas = px.bar(
    x=top_artistas.index,
    y=top_artistas.values,
    title="Artistas com Mais Faixas no Dataset",
    labels={'x': 'Artista', 'y': 'Número de Faixas'},
    color=top_artistas.values,
    color_continuous_scale='Blues'
)
fig_artistas.update_layout(height=400, showlegend=False, xaxis={'tickangle': 45})
st.plotly_chart(fig_artistas, use_container_width=True)

# Sidebar com estatísticas adicionais
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Estatísticas Atuais")
    
    if len(df_filtrado) > 0:
        st.metric("Faixas Analisadas", f"{len(df_filtrado):,}")
        st.metric("Gênero + Popular", df_filtrado['track_genre'].value_counts().index[0])
        st.metric("Energia Média", f"{df_filtrado['energy'].mean():.2f}")
        st.metric("Danceabilidade Média", f"{df_filtrado['danceability'].mean():.2f}")
        
        st.markdown("---")
        st.subheader("🎯 Faixa + Popular Filtrada")
        faixa_popular = df_filtrado.loc[df_filtrado['popularity'].idxmax()]
        st.write(f"**{faixa_popular['track_name']}**")
        st.write(f"*{faixa_popular['primeiro_artista']}*")
        st.write(f"Pop: {faixa_popular['popularity']}")
    else:
        st.warning("Nenhuma faixa encontrada com os filtros aplicados.")
        
    st.markdown("---")
    st.info("💡 Dica: Ajuste os filtros acima para explorar diferentes segmentos dos dados!")