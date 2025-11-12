import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title="Análise de Gêneros - Spotify Analytics",
    page_icon="🎸",
    layout="wide"
)

st.title("🎸 Análise de Gêneros Musicais")
st.markdown("### Exploração detalhada dos 114 gêneros musicais do Spotify")

# Carrega os dados
df = carregar_dados()

# Overview dos gêneros
total_generos = df['track_genre'].nunique()
genero_mais_comum = df['track_genre'].value_counts().index[0]
tracks_genero_mais_comum = df['track_genre'].value_counts().iloc[0]

st.info(f"""
🎵 **Dataset Musical**: {total_generos} gêneros únicos | 
🏆 **Gênero líder**: {genero_mais_comum} ({tracks_genero_mais_comum:,} faixas) | 
📊 **Total de faixas**: {len(df):,}
""")

# Sidebar com filtros
st.sidebar.header("🎛️ Filtros de Gêneros")

# Filtro por número mínimo de faixas
min_tracks_genero = st.sidebar.slider(
    "Mínimo de faixas por gênero:",
    min_value=1,
    max_value=1000,
    value=100,
    step=50,
    help="Filtra gêneros com pelo menos X faixas"
)

# Filtro por popularidade média
pop_media_min = st.sidebar.slider(
    "Popularidade média mínima:",
    min_value=0,
    max_value=100,
    value=0,
    step=5
)

# Filtro por características musicais
st.sidebar.subheader("🎵 Filtros de Características")

energy_filter = st.sidebar.slider("Energia mínima:", 0.0, 1.0, 0.0, 0.1)
danceability_filter = st.sidebar.slider("Danceabilidade mínima:", 0.0, 1.0, 0.0, 0.1)

# Calcular estatísticas por gênero
stats_generos = df.groupby('track_genre').agg({
    'track_id': 'count',  # número de faixas
    'popularity': ['mean', 'std', 'max'],
    'danceability': 'mean',
    'energy': 'mean',
    'valence': 'mean',
    'acousticness': 'mean',
    'instrumentalness': 'mean',
    'liveness': 'mean',
    'speechiness': 'mean',
    'tempo': 'mean',
    'duration_min': 'mean',
    'loudness': 'mean'
}).round(3)

# Flatten column names
stats_generos.columns = ['num_faixas', 'pop_media', 'pop_std', 'pop_maxima', 'danceability', 'energy', 
                        'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness', 
                        'tempo', 'duration_min', 'loudness']

stats_generos = stats_generos.reset_index()

# Aplicar filtros
stats_filtrados = stats_generos[
    (stats_generos['num_faixas'] >= min_tracks_genero) &
    (stats_generos['pop_media'] >= pop_media_min) &
    (stats_generos['energy'] >= energy_filter) &
    (stats_generos['danceability'] >= danceability_filter)
]

# Métricas após filtros
st.subheader("📈 Estatísticas dos Gêneros Filtrados")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Gêneros Analisados", f"{len(stats_filtrados)}/{total_generos}")
with col2:
    if len(stats_filtrados) > 0:
        st.metric("Popularidade Média", f"{stats_filtrados['pop_media'].mean():.1f}")
    else:
        st.metric("Popularidade Média", "N/A")
with col3:
    if len(stats_filtrados) > 0:
        st.metric("Energia Média", f"{stats_filtrados['energy'].mean():.3f}")
    else:
        st.metric("Energia Média", "N/A")
with col4:
    if len(stats_filtrados) > 0:
        st.metric("Danceabilidade Média", f"{stats_filtrados['danceability'].mean():.3f}")
    else:
        st.metric("Danceabilidade Média", "N/A")
with col5:
    if len(stats_filtrados) > 0:
        faixas_totais = stats_filtrados['num_faixas'].sum()
        st.metric("Total de Faixas", f"{faixas_totais:,}")
    else:
        st.metric("Total de Faixas", "0")

if len(stats_filtrados) == 0:
    st.warning("⚠️ Nenhum gênero encontrado com os filtros aplicados. Ajuste os critérios de filtro.")
    st.stop()

# CHARTS SECTION

# Chart 1: Top Genres by Number of Tracks
st.subheader("🏆 Top 20 Gêneros por Número de Faixas")

top_20_generos = stats_filtrados.nlargest(20, 'num_faixas')

fig_top_generos = px.bar(
    top_20_generos,
    x='track_genre',
    y='num_faixas',
    title="Gêneros com Mais Faixas no Dataset",
    labels={'track_genre': 'Gênero Musical', 'num_faixas': 'Número de Faixas'},
    color='num_faixas',
    color_continuous_scale='Blues',
    text='num_faixas'
)
fig_top_generos.update_traces(texttemplate='%{text}', textposition='outside')
fig_top_generos.update_layout(height=500, xaxis={'tickangle': 45})
st.plotly_chart(fig_top_generos, use_container_width=True)

# Chart 2: Popularity vs Energy (Bubble Chart)
st.subheader("⭐ Popularidade vs Energia dos Gêneros")

fig_bubble = px.scatter(
    stats_filtrados,
    x='energy',
    y='pop_media',
    size='num_faixas',
    color='danceability',
    hover_data=['track_genre', 'valence', 'tempo'],
    title="Relação entre Energia e Popularidade (tamanho = nº faixas, cor = danceabilidade)",
    labels={
        'energy': 'Energia Média',
        'pop_media': 'Popularidade Média',
        'num_faixas': 'Número de Faixas',
        'danceability': 'Danceabilidade'
    },
    color_continuous_scale='Viridis'
)
fig_bubble.update_layout(height=500)
st.plotly_chart(fig_bubble, use_container_width=True)

# INTERACTIVE ANALYSIS: Genre Comparison
st.subheader("🔍 Comparação Detalhada de Gêneros")

# Widget para seleção de gêneros
generos_disponiveis = sorted(stats_filtrados['track_genre'].tolist())

if len(generos_disponiveis) > 0:
    generos_selecionados = st.multiselect(
        "Selecione até 5 gêneros para comparação detalhada:",
        generos_disponiveis,
        default=generos_disponiveis[:3] if len(generos_disponiveis) >= 3 else generos_disponiveis,
        max_selections=5
    )
    
    if len(generos_selecionados) > 0:
        # Radar chart comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📡 Perfil Musical Comparativo")
            
            caracteristicas_radar = ['danceability', 'energy', 'valence', 'acousticness', 
                                   'instrumentalness', 'liveness', 'speechiness']
            
            fig_radar = go.Figure()
            cores = ['#1DB954', '#FF6B35', '#4ECDC4', '#45B7D1', '#96CEB4']
            
            for i, genero in enumerate(generos_selecionados):
                dados_genero = stats_filtrados[stats_filtrados['track_genre'] == genero].iloc[0]
                valores = [dados_genero[carac] for carac in caracteristicas_radar]
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=valores,
                    theta=[carac.replace('_', ' ').title() for carac in caracteristicas_radar],
                    fill='toself',
                    name=f"{genero} (n={dados_genero['num_faixas']})",
                    line_color=cores[i % len(cores)],
                    opacity=0.7
                ))
            
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title="Características Musicais por Gênero",
                height=500
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            st.subheader("📊 Métricas Comparativas")
            
            # Comparative bar chart
            metricas_comp = ['pop_media', 'num_faixas', 'tempo', 'duration_min']
            dados_comparacao = stats_filtrados[stats_filtrados['track_genre'].isin(generos_selecionados)]
            
            metrica_selecionada = st.selectbox(
                "Escolha a métrica para comparação:",
                options=['pop_media', 'num_faixas', 'tempo', 'duration_min', 'loudness'],
                format_func=lambda x: {
                    'pop_media': 'Popularidade Média',
                    'num_faixas': 'Número de Faixas',
                    'tempo': 'Tempo (BPM)',
                    'duration_min': 'Duração Média (min)',
                    'loudness': 'Volume (dB)'
                }[x]
            )
            
            fig_comp_bar = px.bar(
                dados_comparacao,
                x='track_genre',
                y=metrica_selecionada,
                title=f"Comparação: {metrica_selecionada.replace('_', ' ').title()}",
                labels={'track_genre': 'Gênero', metrica_selecionada: metrica_selecionada.replace('_', ' ').title()},
                color=metrica_selecionada,
                color_continuous_scale='Plasma',
                text=metrica_selecionada
            )
            fig_comp_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_comp_bar.update_layout(height=500, xaxis={'tickangle': 45})
            st.plotly_chart(fig_comp_bar, use_container_width=True)
        
        # Detailed comparison table
        st.subheader("📋 Tabela Comparativa Detalhada")
        
        colunas_exibir = ['track_genre', 'num_faixas', 'pop_media', 'danceability', 'energy', 
                         'valence', 'acousticness', 'tempo', 'duration_min']
        
        tabela_comparativa = dados_comparacao[colunas_exibir].copy()
        
        st.dataframe(
            tabela_comparativa,
            column_config={
                'track_genre': 'Gênero',
                'num_faixas': 'Nº Faixas',
                'pop_media': st.column_config.NumberColumn('Popularidade', format="%.1f"),
                'danceability': st.column_config.NumberColumn('Danceabilidade', format="%.3f"),
                'energy': st.column_config.NumberColumn('Energia', format="%.3f"),
                'valence': st.column_config.NumberColumn('Valência', format="%.3f"),
                'acousticness': st.column_config.NumberColumn('Acousticness', format="%.3f"),
                'tempo': st.column_config.NumberColumn('BPM', format="%.1f"),
                'duration_min': st.column_config.NumberColumn('Duração (min)', format="%.1f")
            },
            hide_index=True,
            use_container_width=True
        )

# GENRE ANALYSIS BY CATEGORIES
st.subheader("📂 Análise por Categorias de Gêneros")

# Group genres by main categories
categorias_generos = {
    'Electronic': ['electronic', 'edm', 'electro', 'house', 'techno', 'trance', 'dubstep', 
                  'drum-and-bass', 'detroit-techno', 'deep-house', 'progressive-house', 'minimal-techno',
                  'chicago-house', 'garage', 'breakbeat', 'dub', 'idm'],
    'Rock': ['rock', 'alt-rock', 'alternative', 'hard-rock', 'punk-rock', 'punk', 'rock-n-roll', 
             'grunge', 'psych-rock', 'rockabilly', 'indie', 'emo', 'garage'],
    'Pop': ['pop', 'pop-film', 'power-pop', 'indie-pop', 'k-pop', 'j-pop', 'mandopop', 'cantopop'],
    'Metal': ['metal', 'black-metal', 'death-metal', 'heavy-metal', 'metalcore', 'grindcore', 'hardcore'],
    'Hip-Hop/R&B': ['hip-hop', 'r-n-b'],
    'Jazz/Blues': ['jazz', 'blues', 'soul'],
    'Latin/World': ['latin', 'latino', 'samba', 'salsa', 'reggaeton', 'tango', 'sertanejo', 'forro', 
                   'pagode', 'afrobeat', 'reggae', 'dancehall', 'world-music'],
    'Folk/Country': ['folk', 'country', 'bluegrass', 'honky-tonk', 'acoustic', 'singer-songwriter', 'songwriter'],
    'Classical': ['classical', 'opera', 'piano', 'new-age'],
    'Funk/Disco': ['funk', 'disco', 'groove'],
    'Ambient/Chill': ['ambient', 'chill', 'sleep', 'study']
}

# Calculate stats by category
stats_categorias = []
for categoria, generos_cat in categorias_generos.items():
    generos_presentes = [g for g in generos_cat if g in df['track_genre'].unique()]
    if generos_presentes:
        dados_categoria = df[df['track_genre'].isin(generos_presentes)]
        if len(dados_categoria) > 0:
            stats_cat = {
                'categoria': categoria,
                'num_generos': len(generos_presentes),
                'num_faixas': len(dados_categoria),
                'pop_media': dados_categoria['popularity'].mean(),
                'danceability': dados_categoria['danceability'].mean(),
                'energy': dados_categoria['energy'].mean(),
                'valence': dados_categoria['valence'].mean(),
                'acousticness': dados_categoria['acousticness'].mean(),
                'tempo': dados_categoria['tempo'].mean()
            }
            stats_categorias.append(stats_cat)

if stats_categorias:
    df_categorias = pd.DataFrame(stats_categorias)
    
    # Category comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_cat_tracks = px.pie(
            df_categorias,
            values='num_faixas',
            names='categoria',
            title="Distribuição de Faixas por Categoria Musical"
        )
        fig_cat_tracks.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_cat_tracks, use_container_width=True)
    
    with col2:
        fig_cat_pop = px.bar(
            df_categorias.sort_values('pop_media', ascending=True),
            x='pop_media',
            y='categoria',
            orientation='h',
            title="Popularidade Média por Categoria",
            labels={'pop_media': 'Popularidade Média', 'categoria': 'Categoria'},
            color='pop_media',
            color_continuous_scale='RdYlGn',
            text='pop_media'
        )
        fig_cat_pop.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig_cat_pop, use_container_width=True)

# DETAILED GENRE EXPLORER
st.subheader("🔎 Explorador Detalhado de Gêneros")

# Single genre deep dive
genero_detalhado = st.selectbox(
    "Selecione um gênero para análise detalhada:",
    sorted(stats_filtrados['track_genre'].tolist()),
    key="genero_detalhado"
)

if genero_detalhado:
    dados_genero_detalhado = stats_filtrados[stats_filtrados['track_genre'] == genero_detalhado].iloc[0]
    faixas_genero = df[df['track_genre'] == genero_detalhado]
    
    # Genre overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Faixas", f"{dados_genero_detalhado['num_faixas']:,}")
    with col2:
        st.metric("Popularidade Média", f"{dados_genero_detalhado['pop_media']:.1f}")
    with col3:
        st.metric("Energia Média", f"{dados_genero_detalhado['energy']:.3f}")
    with col4:
        st.metric("BPM Médio", f"{dados_genero_detalhado['tempo']:.0f}")
    
    # Detailed charts for the genre
    col1, col2 = st.columns(2)
    
    with col1:
        # Popularity distribution
        fig_pop_genero = px.histogram(
            faixas_genero,
            x='popularity',
            nbins=20,
            title=f"Distribuição de Popularidade - {genero_detalhado}",
            labels={'popularity': 'Popularidade', 'count': 'Número de Faixas'},
            color_discrete_sequence=['#1DB954']
        )
        st.plotly_chart(fig_pop_genero, use_container_width=True)
    
    with col2:
        # Top artists in genre
        top_artistas_genero = faixas_genero['primeiro_artista'].value_counts().head(10)
        
        fig_artistas_genero = px.bar(
            x=top_artistas_genero.values,
            y=top_artistas_genero.index,
            orientation='h',
            title=f"Top 10 Artistas - {genero_detalhado}",
            labels={'x': 'Número de Faixas', 'y': 'Artista'},
            color=top_artistas_genero.values,
            color_continuous_scale='Oranges'
        )
        fig_artistas_genero.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_artistas_genero, use_container_width=True)
    
    # Top tracks of the genre
    st.subheader(f"🎵 Top 10 Faixas Mais Populares - {genero_detalhado}")
    
    top_tracks_genero = faixas_genero.nlargest(10, 'popularity')[
        ['track_name', 'primeiro_artista', 'album_name', 'popularity', 'duration_min', 'energy', 'danceability']
    ]
    
    st.dataframe(
        top_tracks_genero,
        column_config={
            'track_name': 'Faixa',
            'primeiro_artista': 'Artista',
            'album_name': 'Álbum',
            'popularity': 'Popularidade',
            'duration_min': st.column_config.NumberColumn('Duração (min)', format="%.1f"),
            'energy': st.column_config.NumberColumn('Energia', format="%.3f"),
            'danceability': st.column_config.NumberColumn('Danceabilidade', format="%.3f")
        },
        hide_index=True,
        use_container_width=True
    )

# Sidebar with insights
with st.sidebar:
    st.markdown("---")
    st.subheader("🎸 Insights dos Gêneros")
    
    if len(stats_filtrados) > 0:
        # Most popular genre
        genero_popular = stats_filtrados.loc[stats_filtrados['pop_media'].idxmax()]
        st.metric("Mais Popular", 
                 genero_popular['track_genre'],
                 f"{genero_popular['pop_media']:.1f}/100")
        
        # Most energetic genre
        genero_energetico = stats_filtrados.loc[stats_filtrados['energy'].idxmax()]
        st.metric("Mais Energético", 
                 genero_energetico['track_genre'],
                 f"{genero_energetico['energy']:.3f}")
        
        # Most danceable genre
        genero_dancavel = stats_filtrados.loc[stats_filtrados['danceability'].idxmax()]
        st.metric("Mais Dançável", 
                 genero_dancavel['track_genre'],
                 f"{genero_dancavel['danceability']:.3f}")
        
        # Fastest BPM genre
        genero_rapido = stats_filtrados.loc[stats_filtrados['tempo'].idxmax()]
        st.metric("BPM Mais Alto", 
                 genero_rapido['track_genre'],
                 f"{genero_rapido['tempo']:.0f}")
        
        # Most acoustic genre
        genero_acustico = stats_filtrados.loc[stats_filtrados['acousticness'].idxmax()]
        st.metric("Mais Acústico", 
                 genero_acustico['track_genre'],
                 f"{genero_acustico['acousticness']:.3f}")
    
    st.markdown("---")
    st.info("💡 Explore diferentes filtros para descobrir nichos musicais interessantes!")
    
    # Quick stats
    st.markdown("### 📈 Estatísticas Rápidas")
    if len(stats_filtrados) > 0:
        st.write(f"**Gêneros analisados**: {len(stats_filtrados)}")
        st.write(f"**Mais produtivo**: {stats_filtrados.loc[stats_filtrados['num_faixas'].idxmax(), 'track_genre']}")
        st.write(f"**Média de energia**: {stats_filtrados['energy'].mean():.3f}")
        st.write(f"**Média de valência**: {stats_filtrados['valence'].mean():.3f}")