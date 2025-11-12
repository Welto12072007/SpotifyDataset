import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title="Características Musicais - Spotify Analytics",
    page_icon="🎼",
    layout="wide"
)

st.title("🎼 Análise de Características Musicais")
st.markdown("### Exploração detalhada das features de áudio do Spotify")

# Carrega os dados
df = carregar_dados()

# Explicação das características
with st.expander("ℹ️ O que significam as características musicais?"):
    st.markdown("""
    **🎵 Features de Áudio do Spotify (0.0 a 1.0):**
    
    - **Danceability**: O quão adequada uma faixa é para dançar (ritmo, tempo, regularidade da batida)
    - **Energy**: Intensidade e poder percebido (dinâmica, ruído percebido, timbre, ataque)
    - **Valence**: Positividade musical (feliz, eufórico vs. triste, deprimido, raivoso)
    - **Acousticness**: Probabilidade da faixa ser acústica
    - **Instrumentalness**: Probabilidade da faixa não conter vocais
    - **Liveness**: Presença de audiência na gravação
    - **Speechiness**: Presença de palavras faladas
    
    **🎼 Outras Características:**
    - **Loudness**: Volume geral em decibéis (dB)
    - **Tempo**: Batidas por minuto (BPM)
    - **Key**: Chave musical (0=C, 1=C#/Db, 2=D, etc.)
    - **Mode**: Modalidade (0=Menor, 1=Maior)
    """)

# Sidebar com filtros avançados
st.sidebar.header("🎛️ Filtros Interativos")

# Filtros principais
genero_selecionado = st.sidebar.selectbox(
    "🎸 Gênero Musical:",
    ['Todos'] + sorted(df['track_genre'].unique().tolist())
)

# Filtro de popularidade
pop_range = st.sidebar.slider(
    "⭐ Faixa de Popularidade:",
    0, 100, (0, 100), 5
)

# Filtros para características específicas
st.sidebar.markdown("### 🎵 Filtros de Características")

energy_range = st.sidebar.slider(
    "⚡ Energia:",
    0.0, 1.0, (0.0, 1.0), 0.1
)

danceability_range = st.sidebar.slider(
    "💃 Danceabilidade:",
    0.0, 1.0, (0.0, 1.0), 0.1
)

valence_range = st.sidebar.slider(
    "😊 Valência (Positividade):",
    0.0, 1.0, (0.0, 1.0), 0.1
)

# Aplicar filtros
df_filtrado = df.copy()

if genero_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['track_genre'] == genero_selecionado]

df_filtrado = df_filtrado[
    (df_filtrado['popularity'] >= pop_range[0]) & 
    (df_filtrado['popularity'] <= pop_range[1]) &
    (df_filtrado['energy'] >= energy_range[0]) & 
    (df_filtrado['energy'] <= energy_range[1]) &
    (df_filtrado['danceability'] >= danceability_range[0]) & 
    (df_filtrado['danceability'] <= danceability_range[1]) &
    (df_filtrado['valence'] >= valence_range[0]) & 
    (df_filtrado['valence'] <= valence_range[1])
]

# Métricas resumo
st.subheader("📊 Resumo dos Dados Filtrados")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Faixas", f"{len(df_filtrado):,}")
with col2:
    st.metric("Energia Média", f"{df_filtrado['energy'].mean():.3f}")
with col3:
    st.metric("Danceabilidade Média", f"{df_filtrado['danceability'].mean():.3f}")
with col4:
    st.metric("Valência Média", f"{df_filtrado['valence'].mean():.3f}")

# GRÁFICO INTERATIVO 1: Scatter Matrix das principais características
st.subheader("🔍 Matriz de Dispersão Interativa - Características Principais")

caracteristicas_principais = ['danceability', 'energy', 'valence', 'acousticness']

# Widget para seleção de características para a matriz
col1, col2 = st.columns(2)
with col1:
    x_axis = st.selectbox("Escolha a característica para o eixo X:", caracteristicas_principais, index=0)
with col2:
    y_axis = st.selectbox("Escolha a característica para o eixo Y:", caracteristicas_principais, index=1)

# Amostra para melhor performance
df_sample = df_filtrado.sample(n=min(3000, len(df_filtrado)), random_state=42) if len(df_filtrado) > 3000 else df_filtrado

fig_scatter = px.scatter(
    df_sample,
    x=x_axis,
    y=y_axis,
    color='popularity',
    size='duration_min',
    hover_data=['track_name', 'primeiro_artista', 'track_genre'],
    title=f"Relação entre {x_axis.title()} e {y_axis.title()}",
    labels={
        x_axis: x_axis.replace('_', ' ').title(),
        y_axis: y_axis.replace('_', ' ').title(),
        'popularity': 'Popularidade'
    },
    color_continuous_scale='Viridis'
)
fig_scatter.update_layout(height=500)
st.plotly_chart(fig_scatter, use_container_width=True)

# GRÁFICO INTERATIVO 2: Radar Chart Comparativo
st.subheader("📡 Comparação Radar de Gêneros Musicais")

# Widget para seleção de gêneros
generos_disponiveis = sorted(df_filtrado['genero_principal'].unique())
generos_comparar = st.multiselect(
    "Selecione até 4 gêneros para comparação:",
    generos_disponiveis,
    default=generos_disponiveis[:3] if len(generos_disponiveis) >= 3 else generos_disponiveis
)

if generos_comparar:
    caracteristicas_radar = ['danceability', 'energy', 'speechiness', 'acousticness', 
                           'instrumentalness', 'liveness', 'valence']
    
    fig_radar = go.Figure()
    
    cores = ['#1DB954', '#FF6B35', '#4ECDC4', '#45B7D1']
    
    for i, genero in enumerate(generos_comparar[:4]):
        dados_genero = df_filtrado[df_filtrado['genero_principal'] == genero]
        if len(dados_genero) > 0:
            valores_medios = [dados_genero[carac].mean() for carac in caracteristicas_radar]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=valores_medios,
                theta=[carac.replace('_', ' ').title() for carac in caracteristicas_radar],
                fill='toself',
                name=f"{genero} (n={len(dados_genero)})",
                line_color=cores[i % len(cores)],
                opacity=0.7
            ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Perfil de Características Musicais por Gênero",
        height=600
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

# GRÁFICO 3: Histogramas das características
st.subheader("📈 Distribuição das Características Musicais")

col1, col2 = st.columns(2)

caracteristicas_hist = ['danceability', 'energy', 'valence', 'acousticness', 
                       'instrumentalness', 'liveness', 'speechiness', 'loudness']

with col1:
    caracteristica_hist1 = st.selectbox("Primeira característica:", caracteristicas_hist, index=0)
    
    fig_hist1 = px.histogram(
        df_filtrado,
        x=caracteristica_hist1,
        nbins=30,
        title=f"Distribuição: {caracteristica_hist1.replace('_', ' ').title()}",
        labels={caracteristica_hist1: caracteristica_hist1.replace('_', ' ').title()},
        color_discrete_sequence=['#1DB954']
    )
    fig_hist1.update_layout(height=400)
    st.plotly_chart(fig_hist1, use_container_width=True)

with col2:
    caracteristica_hist2 = st.selectbox("Segunda característica:", caracteristicas_hist, index=1)
    
    fig_hist2 = px.histogram(
        df_filtrado,
        x=caracteristica_hist2,
        nbins=30,
        title=f"Distribuição: {caracteristica_hist2.replace('_', ' ').title()}",
        labels={caracteristica_hist2: caracteristica_hist2.replace('_', ' ').title()},
        color_discrete_sequence=['#FF6B35']
    )
    fig_hist2.update_layout(height=400)
    st.plotly_chart(fig_hist2, use_container_width=True)

# GRÁFICO INTERATIVO 4: Box Plot por Gênero
st.subheader("📦 Box Plot - Variação por Gênero Musical")

# Widget para seleção da característica
caracteristica_box = st.selectbox(
    "Escolha a característica para análise:",
    ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness'],
    index=0
)

# Pegamos apenas os top 10 gêneros para melhor visualização
top_generos = df_filtrado['track_genre'].value_counts().head(10).index.tolist()
df_top_generos = df_filtrado[df_filtrado['track_genre'].isin(top_generos)]

fig_box = px.box(
    df_top_generos,
    x='track_genre',
    y=caracteristica_box,
    title=f"Variação de {caracteristica_box.replace('_', ' ').title()} por Gênero Musical (Top 10)",
    labels={
        'track_genre': 'Gênero Musical',
        caracteristica_box: caracteristica_box.replace('_', ' ').title()
    }
)
fig_box.update_layout(height=500)
fig_box.update_layout(xaxis={'tickangle': 45})
st.plotly_chart(fig_box, use_container_width=True)

# ANÁLISE AVANÇADA: Mapa de calor de correlações
st.subheader("🌡️ Mapa de Calor - Correlações entre Características")

caracteristicas_corr = ['popularity', 'danceability', 'energy', 'loudness', 'speechiness',
                       'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']

correlacao_matrix = df_filtrado[caracteristicas_corr].corr()

fig_heatmap = px.imshow(
    correlacao_matrix,
    text_auto=True,
    aspect="auto",
    title="Correlações entre Características Musicais",
    color_continuous_scale='RdBu_r'
)
fig_heatmap.update_layout(height=600)
st.plotly_chart(fig_heatmap, use_container_width=True)

# GRÁFICO INTERATIVO 5: Violin Plot
st.subheader("🎻 Violin Plot - Densidade de Distribuição")

col1, col2 = st.columns(2)

with col1:
    caracteristica_violin = st.selectbox(
        "Característica para Violin Plot:",
        ['danceability', 'energy', 'valence', 'acousticness'],
        index=0,
        key="violin_char"
    )

with col2:
    agrupamento_violin = st.selectbox(
        "Agrupar por:",
        ['genero_principal', 'categoria_popularidade', 'modo_musical'],
        index=0
    )

fig_violin = px.violin(
    df_filtrado,
    x=agrupamento_violin,
    y=caracteristica_violin,
    title=f"Densidade de {caracteristica_violin.replace('_', ' ').title()} por {agrupamento_violin.replace('_', ' ').title()}",
    labels={
        agrupamento_violin: agrupamento_violin.replace('_', ' ').title(),
        caracteristica_violin: caracteristica_violin.replace('_', ' ').title()
    }
)
fig_violin.update_layout(height=500)
fig_violin.update_layout(xaxis={'tickangle': 45})
st.plotly_chart(fig_violin, use_container_width=True)

# Análise de clusters usando características principais
st.subheader("🎯 Análise de Clusters Musicais")

if len(df_filtrado) > 0:
    # Calculamos estatísticas por gênero principal
    stats_por_genero = df_filtrado.groupby('genero_principal')[
        ['danceability', 'energy', 'valence', 'acousticness']
    ].mean().reset_index()
    
    # Criamos um gráfico 3D
    fig_3d = px.scatter_3d(
        stats_por_genero,
        x='danceability',
        y='energy',
        z='valence',
        color='acousticness',
        size=[1]*len(stats_por_genero),
        hover_data=['genero_principal'],
        title="Clusters 3D de Gêneros por Características Musicais",
        labels={
            'danceability': 'Danceabilidade',
            'energy': 'Energia',
            'valence': 'Valência',
            'acousticness': 'Acousticness'
        },
        color_continuous_scale='Viridis'
    )
    fig_3d.update_layout(height=600)
    st.plotly_chart(fig_3d, use_container_width=True)

# Sidebar com insights
with st.sidebar:
    st.markdown("---")
    st.subheader("🎵 Insights dos Filtros")
    
    if len(df_filtrado) > 0:
        st.write(f"**{len(df_filtrado):,}** faixas analisadas")
        
        # Característica predominante
        caracteristicas = ['danceability', 'energy', 'valence', 'acousticness']
        medias = {carac: df_filtrado[carac].mean() for carac in caracteristicas}
        caracteristica_dominante = max(medias, key=medias.get)
        
        st.metric(
            "Característica Dominante",
            caracteristica_dominante.replace('_', ' ').title(),
            f"{medias[caracteristica_dominante]:.3f}"
        )
        
        # Gênero mais representativo
        if len(df_filtrado['genero_principal'].unique()) > 0:
            genero_top = df_filtrado['genero_principal'].value_counts().index[0]
            st.metric("Gênero Principal", genero_top)
        
        # Correlação mais forte
        corr_matrix = df_filtrado[caracteristicas].corr()
        np.fill_diagonal(corr_matrix.values, 0)  # Remove diagonal
        max_corr = corr_matrix.abs().max().max()
        
        if max_corr > 0:
            st.metric("Correlação Máxima", f"{max_corr:.3f}")
    else:
        st.warning("Ajuste os filtros para ver dados")
    
    st.markdown("---")
    st.info("💡 Explore diferentes combinações de filtros para descobrir padrões únicos nas características musicais!")