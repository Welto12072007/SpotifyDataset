import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title="Análise Temporal - Spotify Analytics",
    page_icon="⏱️",
    layout="wide"
)

st.title("⏱️ Análise Temporal da Música")
st.markdown("### Exploração de duração, tempo (BPM) e características temporais")

# Carrega os dados
df = carregar_dados()

# Overview das características temporais
duracao_media = df['duration_min'].mean()
tempo_medio = df['tempo'].mean()
faixa_mais_longa = df.loc[df['duration_min'].idxmax()]
faixa_mais_rapida = df.loc[df['tempo'].idxmax()]

st.info(f"""
⏱️ **Estatísticas Temporais**: Duração média: {duracao_media:.1f} min | 
🎵 **Tempo médio**: {tempo_medio:.0f} BPM | 
📏 **Faixa + longa**: "{faixa_mais_longa['track_name']}" ({faixa_mais_longa['duration_min']:.1f} min) | 
🏃 **BPM + alto**: "{faixa_mais_rapida['track_name']}" ({faixa_mais_rapida['tempo']:.0f} BPM)
""")

# Sidebar com filtros
st.sidebar.header("⏰ Filtros Temporais")

# Filtro de duração
duracao_range = st.sidebar.slider(
    "Faixa de duração (minutos):",
    min_value=0.0,
    max_value=20.0,
    value=(0.0, 10.0),
    step=0.5,
    help="Filtrar faixas por duração em minutos"
)

# Filtro de BPM
bpm_range = st.sidebar.slider(
    "Faixa de BPM:",
    min_value=int(df['tempo'].min()),
    max_value=int(df['tempo'].max()),
    value=(60, 200),
    step=5,
    help="Filtrar faixas por batidas por minuto"
)

# Filtro por assinatura temporal
time_signatures = sorted(df['time_signature'].unique())
time_sig_selecionada = st.sidebar.multiselect(
    "Assinatura temporal:",
    time_signatures,
    default=time_signatures,
    help="Número de batidas por compasso"
)

# Filtro por gênero
generos_tempo = ['Todos'] + sorted(df['track_genre'].unique())
genero_temporal = st.sidebar.selectbox("Filtrar por gênero:", generos_tempo)

# Aplicar filtros
df_filtrado = df[
    (df['duration_min'] >= duracao_range[0]) & 
    (df['duration_min'] <= duracao_range[1]) &
    (df['tempo'] >= bpm_range[0]) & 
    (df['tempo'] <= bpm_range[1]) &
    (df['time_signature'].isin(time_sig_selecionada))
]

if genero_temporal != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['track_genre'] == genero_temporal]

# Métricas após filtros
st.subheader("📊 Métricas das Faixas Filtradas")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Faixas Analisadas", f"{len(df_filtrado):,}")
with col2:
    if len(df_filtrado) > 0:
        st.metric("Duração Média", f"{df_filtrado['duration_min'].mean():.1f} min")
    else:
        st.metric("Duração Média", "N/A")
with col3:
    if len(df_filtrado) > 0:
        st.metric("BPM Médio", f"{df_filtrado['tempo'].mean():.0f}")
    else:
        st.metric("BPM Médio", "N/A")
with col4:
    if len(df_filtrado) > 0:
        time_sig_comum = df_filtrado['time_signature'].mode().iloc[0] if len(df_filtrado) > 0 else "N/A"
        st.metric("Compasso + Comum", f"{time_sig_comum}/4")
    else:
        st.metric("Compasso + Comum", "N/A")
with col5:
    if len(df_filtrado) > 0:
        st.metric("Popularidade Média", f"{df_filtrado['popularity'].mean():.1f}")
    else:
        st.metric("Popularidade Média", "N/A")

if len(df_filtrado) == 0:
    st.warning("⚠️ Nenhuma faixa encontrada com os filtros aplicados. Ajuste os critérios de filtro.")
    st.stop()

# GRÁFICOS DE ANÁLISE TEMPORAL

# Gráfico 1: Distribuição de Duração
st.subheader("📏 Distribuição da Duração das Faixas")

col1, col2 = st.columns(2)

with col1:
    # Histograma de duração
    fig_duracao = px.histogram(
        df_filtrado,
        x='duration_min',
        nbins=50,
        title="Distribuição da Duração das Faixas (Minutos)",
        labels={'duration_min': 'Duração (minutos)', 'count': 'Número de Faixas'},
        color_discrete_sequence=['#1DB954']
    )
    fig_duracao.add_vline(x=df_filtrado['duration_min'].mean(), 
                         line_dash="dash", line_color="red",
                         annotation_text=f"Média: {df_filtrado['duration_min'].mean():.1f} min")
    fig_duracao.update_layout(height=400)
    st.plotly_chart(fig_duracao, use_container_width=True)

with col2:
    # Box plot de duração por categoria
    fig_box_duracao = px.box(
        df_filtrado,
        x='categoria_duracao',
        y='duration_min',
        title="Duração por Categoria",
        labels={'categoria_duracao': 'Categoria de Duração', 'duration_min': 'Duração (min)'},
        color='categoria_duracao'
    )
    fig_box_duracao.update_layout(height=400, xaxis={'tickangle': 45})
    st.plotly_chart(fig_box_duracao, use_container_width=True)

# Gráfico 2: Análise de BPM
st.subheader("🥁 Análise de Tempo (BPM)")

col1, col2 = st.columns(2)

with col1:
    # Histograma de BPM
    fig_bpm = px.histogram(
        df_filtrado,
        x='tempo',
        nbins=50,
        title="Distribuição do Tempo (BPM)",
        labels={'tempo': 'BPM', 'count': 'Número de Faixas'},
        color_discrete_sequence=['#FF6B35']
    )
    fig_bpm.add_vline(x=df_filtrado['tempo'].mean(), 
                     line_dash="dash", line_color="red",
                     annotation_text=f"Média: {df_filtrado['tempo'].mean():.0f} BPM")
    fig_bpm.update_layout(height=400)
    st.plotly_chart(fig_bpm, use_container_width=True)

with col2:
    # BPM por categoria
    fig_bpm_categoria = px.box(
        df_filtrado,
        x='categoria_tempo',
        y='tempo',
        title="BPM por Categoria de Tempo",
        labels={'categoria_tempo': 'Categoria de Tempo', 'tempo': 'BPM'},
        color='categoria_tempo'
    )
    fig_bpm_categoria.update_layout(height=400, xaxis={'tickangle': 45})
    st.plotly_chart(fig_bpm_categoria, use_container_width=True)

# GRÁFICO INTERATIVO: Duração vs BPM
st.subheader("🔄 Relação entre Duração e BPM")

# Widget para escolher variável de cor
opcoes_cor = ['track_genre', 'genero_principal', 'categoria_popularidade', 'modo_musical', 'chave_musical']
cor_selecionada = st.selectbox(
    "Colorir gráfico por:",
    opcoes_cor,
    format_func=lambda x: {
        'track_genre': 'Gênero Musical',
        'genero_principal': 'Gênero Principal',
        'categoria_popularidade': 'Categoria de Popularidade',
        'modo_musical': 'Modo Musical (Maior/Menor)',
        'chave_musical': 'Chave Musical'
    }[x]
)

# Amostra para melhor performance
df_sample = df_filtrado.sample(n=min(3000, len(df_filtrado)), random_state=42)

fig_duracao_bpm = px.scatter(
    df_sample,
    x='tempo',
    y='duration_min',
    color=cor_selecionada,
    size='popularity',
    hover_data=['track_name', 'primeiro_artista', 'energy', 'danceability'],
    title=f"Relação Duração vs BPM (colorido por {cor_selecionada.replace('_', ' ').title()})",
    labels={
        'tempo': 'BPM',
        'duration_min': 'Duração (minutos)',
        'popularity': 'Popularidade',
        cor_selecionada: cor_selecionada.replace('_', ' ').title()
    },
    opacity=0.7
)
fig_duracao_bpm.update_layout(height=500)
st.plotly_chart(fig_duracao_bpm, use_container_width=True)

# Análise por Assinatura Temporal
st.subheader("🎼 Análise por Assinatura Temporal")

# Estatísticas por time signature
stats_time_sig = df_filtrado.groupby('time_signature').agg({
    'track_id': 'count',
    'popularity': 'mean',
    'duration_min': 'mean',
    'tempo': 'mean',
    'energy': 'mean',
    'danceability': 'mean'
}).round(2)

stats_time_sig.columns = ['num_faixas', 'pop_media', 'duracao_media', 'bpm_medio', 'energia_media', 'dance_media']
stats_time_sig = stats_time_sig.reset_index()

col1, col2 = st.columns(2)

with col1:
    # Gráfico de pizza para distribuição de time signatures
    fig_time_sig = px.pie(
        stats_time_sig,
        values='num_faixas',
        names='time_signature',
        title="Distribuição por Assinatura Temporal"
    )
    fig_time_sig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_time_sig, use_container_width=True)

with col2:
    # Características por time signature
    fig_time_char = px.bar(
        stats_time_sig,
        x='time_signature',
        y=['duracao_media', 'bpm_medio', 'energia_media', 'dance_media'],
        title="Características Médias por Assinatura Temporal",
        labels={'value': 'Valor Médio', 'time_signature': 'Assinatura Temporal'},
        barmode='group'
    )
    st.plotly_chart(fig_time_char, use_container_width=True)

# Análise por Gênero e Características Temporais
st.subheader("🎸 Características Temporais por Gênero")

# Top 15 gêneros para análise
top_generos_tempo = df_filtrado['track_genre'].value_counts().head(15).index.tolist()
df_top_generos = df_filtrado[df_filtrado['track_genre'].isin(top_generos_tempo)]

# Características temporais médias por gênero
stats_genero_tempo = df_top_generos.groupby('track_genre').agg({
    'duration_min': 'mean',
    'tempo': 'mean',
    'popularity': 'mean',
    'energy': 'mean'
}).round(2)

stats_genero_tempo = stats_genero_tempo.reset_index()

# Widget para escolher métrica
metrica_genero = st.selectbox(
    "Escolha a métrica temporal para análise por gênero:",
    ['duration_min', 'tempo'],
    format_func=lambda x: 'Duração Média (min)' if x == 'duration_min' else 'BPM Médio'
)

fig_genero_tempo = px.bar(
    stats_genero_tempo.sort_values(metrica_genero, ascending=False),
    x='track_genre',
    y=metrica_genero,
    color='energy',
    title=f"{'Duração Média' if metrica_genero == 'duration_min' else 'BPM Médio'} por Gênero (Top 15)",
    labels={
        'track_genre': 'Gênero Musical',
        metrica_genero: 'Duração Média (min)' if metrica_genero == 'duration_min' else 'BPM Médio',
        'energy': 'Energia'
    },
    color_continuous_scale='Viridis',
    text=metrica_genero
)
fig_genero_tempo.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig_genero_tempo.update_layout(height=500, xaxis={'tickangle': 45})
st.plotly_chart(fig_genero_tempo, use_container_width=True)

# Análise de Correlações Temporais
st.subheader("🔗 Correlações com Características Temporais")

# Matriz de correlação focada em características temporais
caracteristicas_correlacao = ['duration_min', 'tempo', 'popularity', 'energy', 'danceability', 
                             'valence', 'acousticness', 'loudness']

correlacao_temporal = df_filtrado[caracteristicas_correlacao].corr()

fig_corr_tempo = px.imshow(
    correlacao_temporal,
    text_auto=True,
    aspect="auto",
    title="Matrix de Correlação - Foco em Características Temporais",
    color_continuous_scale='RdBu_r'
)
fig_corr_tempo.update_layout(height=600)
st.plotly_chart(fig_corr_tempo, use_container_width=True)

# Análise Avançada: Clusters Temporais
st.subheader("🎯 Clusters de Características Temporais")

# Criamos bins para análise de clusters
df_filtrado_cluster = df_filtrado.copy()
df_filtrado_cluster['duracao_categoria'] = pd.cut(df_filtrado_cluster['duration_min'], 
                                                 bins=5, labels=['Muito Curta', 'Curta', 'Média', 'Longa', 'Muito Longa'])
df_filtrado_cluster['bpm_categoria'] = pd.cut(df_filtrado_cluster['tempo'], 
                                             bins=5, labels=['Muito Lento', 'Lento', 'Médio', 'Rápido', 'Muito Rápido'])

# Heatmap de clusters
cluster_stats = df_filtrado_cluster.groupby(['duracao_categoria', 'bpm_categoria']).agg({
    'track_id': 'count',
    'popularity': 'mean'
}).round(1)

cluster_counts = cluster_stats['track_id'].unstack(fill_value=0)
cluster_popularity = cluster_stats['popularity'].unstack(fill_value=0)

col1, col2 = st.columns(2)

with col1:
    fig_cluster_count = px.imshow(
        cluster_counts.values,
        x=cluster_counts.columns,
        y=cluster_counts.index,
        text_auto=True,
        aspect="auto",
        title="Número de Faixas por Cluster (Duração x BPM)",
        labels={'color': 'Número de Faixas'},
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_cluster_count, use_container_width=True)

with col2:
    fig_cluster_pop = px.imshow(
        cluster_popularity.values,
        x=cluster_popularity.columns,
        y=cluster_popularity.index,
        text_auto=True,
        aspect="auto",
        title="Popularidade Média por Cluster (Duração x BPM)",
        labels={'color': 'Popularidade Média'},
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_cluster_pop, use_container_width=True)

# Análise de Extremos Temporais
st.subheader("⚡ Análise de Extremos Temporais")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🐌 Faixas Mais Lentas (BPM)")
    mais_lentas = df_filtrado.nsmallest(5, 'tempo')[['track_name', 'primeiro_artista', 'track_genre', 'tempo']]
    st.dataframe(mais_lentas, hide_index=True, use_container_width=True)

with col2:
    st.markdown("#### ⚡ Faixas Mais Rápidas (BPM)")
    mais_rapidas = df_filtrado.nlargest(5, 'tempo')[['track_name', 'primeiro_artista', 'track_genre', 'tempo']]
    st.dataframe(mais_rapidas, hide_index=True, use_container_width=True)

with col3:
    st.markdown("#### 📏 Faixas Mais Longas")
    mais_longas = df_filtrado.nlargest(5, 'duration_min')[['track_name', 'primeiro_artista', 'track_genre', 'duration_min']]
    st.dataframe(mais_longas, hide_index=True, 
                column_config={'duration_min': st.column_config.NumberColumn('Duração (min)', format="%.1f")},
                use_container_width=True)

# Sidebar com insights temporais
with st.sidebar:
    st.markdown("---")
    st.subheader("⏰ Insights Temporais")
    
    if len(df_filtrado) > 0:
        # Duração mais comum
        duracao_comum = df_filtrado['categoria_duracao'].mode().iloc[0]
        st.metric("Duração + Comum", duracao_comum)
        
        # BPM mais comum
        bpm_comum = df_filtrado['categoria_tempo'].mode().iloc[0]
        st.metric("BPM + Comum", bpm_comum)
        
        # Correlação duração-popularidade
        corr_dur_pop = df_filtrado['duration_min'].corr(df_filtrado['popularity'])
        st.metric("Corr. Duração-Pop.", f"{corr_dur_pop:.3f}")
        
        # Correlação BPM-energia
        corr_bpm_energy = df_filtrado['tempo'].corr(df_filtrado['energy'])
        st.metric("Corr. BPM-Energia", f"{corr_bpm_energy:.3f}")
        
        # Insights automáticos
        st.markdown("---")
        st.subheader("🔍 Insights Automáticos")
        
        if corr_dur_pop > 0.1:
            st.success("✅ Faixas mais longas tendem a ser mais populares!")
        elif corr_dur_pop < -0.1:
            st.warning("⚠️ Faixas mais longas tendem a ser menos populares")
        else:
            st.info("ℹ️ Duração não afeta muito a popularidade")
            
        if corr_bpm_energy > 0.3:
            st.success("✅ BPM alto correlaciona com alta energia!")
        elif corr_bpm_energy < -0.1:
            st.warning("⚠️ Correlação negativa BPM-energia")
        else:
            st.info("ℹ️ BPM e energia têm correlação moderada")
    
    st.markdown("---")
    st.info("💡 Use os filtros para explorar diferentes faixas de tempo e duração!")