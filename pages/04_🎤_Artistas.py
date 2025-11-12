import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title="Análise de Artistas - Spotify Analytics",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Análise de Artistas")
st.markdown("### Exploração detalhada dos artistas mais influentes no Spotify")

# Carrega os dados
df = carregar_dados()

# Prepare data about artists
df_artistas = df.groupby('primeiro_artista').agg({
    'track_id': 'count',  # número de faixas
    'popularity': ['mean', 'max'],
    'danceability': 'mean',
    'energy': 'mean',
    'valence': 'mean',
    'acousticness': 'mean',
    'duration_min': 'mean',
    'track_genre': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'N/A'  # gênero mais comum
}).round(3)

# Flatten column names
df_artistas.columns = ['num_faixas', 'pop_media', 'pop_maxima', 'danceability_media', 
                      'energy_media', 'valence_media', 'acousticness_media', 
                      'duracao_media', 'genero_principal']

df_artistas = df_artistas.reset_index()

# Sidebar filters
st.sidebar.header("🎛️ Filtros de Artistas")

# Filter by minimum number of tracks
min_tracks = st.sidebar.slider(
    "Mínimo de faixas por artista:",
    min_value=1,
    max_value=min(20, df_artistas['num_faixas'].max()),
    value=1,
    step=1
)

# Filter by popularity
pop_min = st.sidebar.slider(
    "Popularidade mínima média:",
    min_value=0,
    max_value=100,
    value=0,
    step=5
)

# Filter by genre
generos_artistas = ['Todos'] + sorted(df_artistas['genero_principal'].unique().tolist())
genero_filtro = st.sidebar.selectbox(
    "Filtrar por gênero principal:",
    generos_artistas
)

# Apply filters
df_artistas_filtrado = df_artistas[df_artistas['num_faixas'] >= min_tracks]
df_artistas_filtrado = df_artistas_filtrado[df_artistas_filtrado['pop_media'] >= pop_min]

if genero_filtro != 'Todos':
    df_artistas_filtrado = df_artistas_filtrado[df_artistas_filtrado['genero_principal'] == genero_filtro]

# Sort by popularity
df_artistas_filtrado = df_artistas_filtrado.sort_values('pop_media', ascending=False)

# Overview metrics
st.subheader("📈 Métricas dos Artistas Filtrados")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total de Artistas", f"{len(df_artistas_filtrado):,}")
with col2:
    if len(df_artistas_filtrado) > 0:
        st.metric("Popularidade Média", f"{df_artistas_filtrado['pop_media'].mean():.1f}")
    else:
        st.metric("Popularidade Média", "N/A")
with col3:
    if len(df_artistas_filtrado) > 0:
        st.metric("Faixas por Artista", f"{df_artistas_filtrado['num_faixas'].mean():.1f}")
    else:
        st.metric("Faixas por Artista", "N/A")
with col4:
    if len(df_artistas_filtrado) > 0:
        artista_top = df_artistas_filtrado.iloc[0]['primeiro_artista']
        st.metric("Artista + Popular", artista_top if len(artista_top) < 15 else artista_top[:12] + "...")
    else:
        st.metric("Artista + Popular", "N/A")
with col5:
    if len(df_artistas_filtrado) > 0:
        max_tracks = df_artistas_filtrado['num_faixas'].max()
        artista_produtivo = df_artistas_filtrado[df_artistas_filtrado['num_faixas'] == max_tracks].iloc[0]['primeiro_artista']
        st.metric("+ Produtivo", artista_produtivo if len(artista_produtivo) < 15 else artista_produtivo[:12] + "...")
    else:
        st.metric("+ Produtivo", "N/A")

if len(df_artistas_filtrado) == 0:
    st.warning("⚠️ Nenhum artista encontrado com os filtros aplicados. Ajuste os critérios de filtro.")
    st.stop()

# TOP ARTISTS CHARTS
col1, col2 = st.columns(2)

# Chart 1: Top Artists by Popularity
with col1:
    st.subheader("🏆 Top 15 Artistas por Popularidade")
    
    top_popular = df_artistas_filtrado.head(15)
    
    fig_popular = px.bar(
        top_popular,
        x='pop_media',
        y='primeiro_artista',
        orientation='h',
        title="Artistas com Maior Popularidade Média",
        labels={'pop_media': 'Popularidade Média', 'primeiro_artista': 'Artista'},
        color='pop_media',
        color_continuous_scale='Greens',
        text='pop_media'
    )
    fig_popular.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_popular.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_popular, use_container_width=True)

# Chart 2: Top Artists by Number of Tracks
with col2:
    st.subheader("🎵 Top 15 Artistas por Número de Faixas")
    
    top_produtivos = df_artistas_filtrado.nlargest(15, 'num_faixas')
    
    fig_produtivos = px.bar(
        top_produtivos,
        x='num_faixas',
        y='primeiro_artista',
        orientation='h',
        title="Artistas Mais Produtivos (Mais Faixas)",
        labels={'num_faixas': 'Número de Faixas', 'primeiro_artista': 'Artista'},
        color='num_faixas',
        color_continuous_scale='Blues',
        text='num_faixas'
    )
    fig_produtivos.update_traces(texttemplate='%{text}', textposition='outside')
    fig_produtivos.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_produtivos, use_container_width=True)

# INTERACTIVE SCATTER: Popularity vs Number of Tracks
st.subheader("📊 Popularidade vs Produtividade dos Artistas")

# Sample for better performance if too many artists
df_sample = df_artistas_filtrado.sample(n=min(1000, len(df_artistas_filtrado)), random_state=42)

fig_scatter = px.scatter(
    df_sample,
    x='num_faixas',
    y='pop_media',
    size='pop_maxima',
    color='genero_principal',
    hover_data=['primeiro_artista', 'danceability_media', 'energy_media'],
    title="Relação entre Número de Faixas e Popularidade Média",
    labels={
        'num_faixas': 'Número de Faixas',
        'pop_media': 'Popularidade Média',
        'pop_maxima': 'Popularidade Máxima',
        'genero_principal': 'Gênero Principal'
    }
)
fig_scatter.update_layout(height=500)
st.plotly_chart(fig_scatter, use_container_width=True)

# ARTIST PROFILE ANALYSIS
st.subheader("👤 Análise de Perfil Musical dos Artistas")

# Interactive widget to select specific artist
artistas_disponiveis = sorted(df_artistas_filtrado['primeiro_artista'].unique().tolist())

if len(artistas_disponiveis) > 0:
    artista_selecionado = st.selectbox(
        "Selecione um artista para análise detalhada:",
        artistas_disponiveis,
        index=0
    )
    
    # Get artist data
    dados_artista = df_artistas_filtrado[df_artistas_filtrado['primeiro_artista'] == artista_selecionado].iloc[0]
    faixas_artista = df[df['primeiro_artista'] == artista_selecionado]
    
    # Artist metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **📊 Estatísticas Gerais**
        
        **Faixas:** {dados_artista['num_faixas']}  
        **Popularidade Média:** {dados_artista['pop_media']:.1f}  
        **Popularidade Máxima:** {dados_artista['pop_maxima']:.1f}  
        **Gênero Principal:** {dados_artista['genero_principal']}
        """)
    
    with col2:
        st.success(f"""
        **🎵 Características Musicais**
        
        **Danceabilidade:** {dados_artista['danceability_media']:.3f}  
        **Energia:** {dados_artista['energy_media']:.3f}  
        **Valência:** {dados_artista['valence_media']:.3f}  
        **Acousticness:** {dados_artista['acousticness_media']:.3f}
        """)
    
    with col3:
        st.warning(f"""
        **⏱️ Características Temporais**
        
        **Duração Média:** {dados_artista['duracao_media']:.1f} min  
        **Tempo Médio (BPM):** {faixas_artista['tempo'].mean():.1f}  
        **Chave Mais Comum:** {faixas_artista['chave_musical'].mode().iloc[0] if len(faixas_artista['chave_musical'].mode()) > 0 else 'N/A'}  
        **Modo Mais Comum:** {faixas_artista['modo_musical'].mode().iloc[0] if len(faixas_artista['modo_musical'].mode()) > 0 else 'N/A'}
        """)
    
    # Radar chart for selected artist
    col1, col2 = st.columns(2)
    
    with col1:
        caracteristicas_radar = ['danceability_media', 'energy_media', 'valence_media', 'acousticness_media']
        valores_artista = [dados_artista[carac] for carac in caracteristicas_radar]
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_artista,
            theta=[carac.replace('_media', '').replace('_', ' ').title() for carac in caracteristicas_radar],
            fill='toself',
            name=artista_selecionado,
            line_color='#1DB954'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title=f"Perfil Musical de {artista_selecionado}",
            height=400
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col2:
        # Track popularity distribution for selected artist
        fig_pop_dist = px.histogram(
            faixas_artista,
            x='popularity',
            nbins=15,
            title=f"Distribuição de Popularidade - {artista_selecionado}",
            labels={'popularity': 'Popularidade', 'count': 'Número de Faixas'},
            color_discrete_sequence=['#FF6B35']
        )
        fig_pop_dist.update_layout(height=400)
        st.plotly_chart(fig_pop_dist, use_container_width=True)
    
    # Top tracks of the selected artist
    st.subheader(f"🎵 Top 10 Faixas de {artista_selecionado}")
    
    top_tracks = faixas_artista.nlargest(10, 'popularity')[
        ['track_name', 'album_name', 'track_genre', 'popularity', 'duration_min', 'energy', 'danceability']
    ]
    
    st.dataframe(
        top_tracks,
        column_config={
            'track_name': 'Faixa',
            'album_name': 'Álbum',
            'track_genre': 'Gênero',
            'popularity': 'Popularidade',
            'duration_min': st.column_config.NumberColumn('Duração (min)', format="%.1f"),
            'energy': st.column_config.NumberColumn('Energia', format="%.3f"),
            'danceability': st.column_config.NumberColumn('Danceabilidade', format="%.3f")
        },
        hide_index=True,
        use_container_width=True
    )

# COMPARISON BETWEEN ARTISTS
st.subheader("🥊 Comparação entre Artistas")

if len(artistas_disponiveis) >= 2:
    col1, col2 = st.columns(2)
    
    with col1:
        artista1 = st.selectbox("Primeiro artista:", artistas_disponiveis, key="comp1")
    
    with col2:
        artistas_comparacao = [a for a in artistas_disponiveis if a != artista1]
        artista2 = st.selectbox("Segundo artista:", artistas_comparacao, key="comp2")
    
    # Get data for both artists
    dados_artista1 = df_artistas_filtrado[df_artistas_filtrado['primeiro_artista'] == artista1].iloc[0]
    dados_artista2 = df_artistas_filtrado[df_artistas_filtrado['primeiro_artista'] == artista2].iloc[0]
    
    # Comparison chart
    caracteristicas_comp = ['danceability_media', 'energy_media', 'valence_media', 'acousticness_media']
    
    fig_comp = go.Figure()
    
    fig_comp.add_trace(go.Scatterpolar(
        r=[dados_artista1[carac] for carac in caracteristicas_comp],
        theta=[carac.replace('_media', '').replace('_', ' ').title() for carac in caracteristicas_comp],
        fill='toself',
        name=artista1,
        line_color='#1DB954',
        opacity=0.7
    ))
    
    fig_comp.add_trace(go.Scatterpolar(
        r=[dados_artista2[carac] for carac in caracteristicas_comp],
        theta=[carac.replace('_media', '').replace('_', ' ').title() for carac in caracteristicas_comp],
        fill='toself',
        name=artista2,
        line_color='#FF6B35',
        opacity=0.7
    ))
    
    fig_comp.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title=f"Comparação: {artista1} vs {artista2}",
        height=500
    )
    
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Comparison table
    st.subheader("📊 Tabela Comparativa")
    
    comp_data = {
        'Métrica': ['Número de Faixas', 'Popularidade Média', 'Popularidade Máxima', 
                   'Danceabilidade', 'Energia', 'Valência', 'Acousticness', 'Duração Média'],
        artista1: [
            dados_artista1['num_faixas'],
            f"{dados_artista1['pop_media']:.1f}",
            f"{dados_artista1['pop_maxima']:.1f}",
            f"{dados_artista1['danceability_media']:.3f}",
            f"{dados_artista1['energy_media']:.3f}",
            f"{dados_artista1['valence_media']:.3f}",
            f"{dados_artista1['acousticness_media']:.3f}",
            f"{dados_artista1['duracao_media']:.1f}"
        ],
        artista2: [
            dados_artista2['num_faixas'],
            f"{dados_artista2['pop_media']:.1f}",
            f"{dados_artista2['pop_maxima']:.1f}",
            f"{dados_artista2['danceability_media']:.3f}",
            f"{dados_artista2['energy_media']:.3f}",
            f"{dados_artista2['valence_media']:.3f}",
            f"{dados_artista2['acousticness_media']:.3f}",
            f"{dados_artista2['duracao_media']:.1f}"
        ]
    }
    
    df_comp = pd.DataFrame(comp_data)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

# Analysis by genre
st.subheader("🎸 Análise de Artistas por Gênero Musical")

generos_analise = df_artistas_filtrado['genero_principal'].value_counts().head(8).index.tolist()

if len(generos_analise) > 1:
    # Average characteristics by genre
    stats_genero = df_artistas_filtrado[df_artistas_filtrado['genero_principal'].isin(generos_analise)].groupby('genero_principal')[
        ['pop_media', 'num_faixas', 'danceability_media', 'energy_media', 'valence_media']
    ].mean().round(3)
    
    fig_genero_stats = px.bar(
        stats_genero.reset_index(),
        x='genero_principal',
        y=['pop_media', 'danceability_media', 'energy_media', 'valence_media'],
        title="Características Médias dos Artistas por Gênero",
        labels={'value': 'Valor Médio', 'genero_principal': 'Gênero Musical'},
        barmode='group'
    )
    fig_genero_stats.update_layout(height=500, xaxis={'tickangle': 45})
    st.plotly_chart(fig_genero_stats, use_container_width=True)

# Sidebar with insights
with st.sidebar:
    st.markdown("---")
    st.subheader("🎵 Insights dos Artistas")
    
    if len(df_artistas_filtrado) > 0:
        # Most productive artist
        artista_produtivo = df_artistas_filtrado.loc[df_artistas_filtrado['num_faixas'].idxmax()]
        st.metric("Mais Produtivo", 
                 artista_produtivo['primeiro_artista'][:20] + ("..." if len(artista_produtivo['primeiro_artista']) > 20 else ""),
                 f"{artista_produtivo['num_faixas']} faixas")
        
        # Most popular artist
        artista_popular = df_artistas_filtrado.loc[df_artistas_filtrado['pop_media'].idxmax()]
        st.metric("Mais Popular", 
                 artista_popular['primeiro_artista'][:20] + ("..." if len(artista_popular['primeiro_artista']) > 20 else ""),
                 f"{artista_popular['pop_media']:.1f}/100")
        
        # Correlation insight
        corr_pop_tracks = df_artistas_filtrado['pop_media'].corr(df_artistas_filtrado['num_faixas'])
        st.metric("Correlação Pop/Faixas", f"{corr_pop_tracks:.3f}")
        
        if corr_pop_tracks > 0.1:
            st.success("✅ Artistas com mais faixas tendem a ser mais populares!")
        elif corr_pop_tracks < -0.1:
            st.warning("⚠️ Artistas com mais faixas tendem a ser menos populares")
        else:
            st.info("ℹ️ Pouca correlação entre número de faixas e popularidade")
    
    st.markdown("---")
    st.info("💡 Use os filtros acima para focar em artistas específicos por produtividade, gênero ou popularidade!")