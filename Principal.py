import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.carrega_dados import carregar_dados, obter_estatisticas_basicas

st.set_page_config(
    page_title="Spotify Music Analytics",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Spotify Music Analytics")
st.markdown("### Dashboard Interativo para Análise de Dados Musicais do Spotify")

# Carrega os dados usando a função cacheada
df = carregar_dados()
stats = obter_estatisticas_basicas()

# Header com métricas principais
st.markdown("---")
st.subheader("📊 Visão Geral do Dataset")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total de Faixas", f"{stats['total_tracks']:,}")
with col2:
    st.metric("Artistas Únicos", f"{stats['total_artists']:,}")
with col3:
    st.metric("Álbuns", f"{stats['total_albums']:,}")
with col4:
    st.metric("Gêneros", stats['total_genres'])
with col5:
    st.metric("Duração Média", f"{stats['duracao_media_min']:.1f} min")

# Introdução ao dashboard
st.markdown(f"""
---

## 🎯 Objetivo do Dashboard

Bem-vindo(a) ao **Spotify Music Analytics**! Este dashboard interativo foi desenvolvido para explorar e visualizar 
um extenso dataset com **{stats['total_tracks']:,} faixas musicais** do Spotify, oferecendo insights profundos sobre:

* **🎼 Características musicais**: análise de danceabilidade, energia, valência e outras features de áudio
* **🎤 Artistas e popularidade**: identificação de tendências e padrões de sucesso
* **🎸 Gêneros musicais**: exploração detalhada dos {stats['total_genres']} gêneros presentes no dataset
* **⏱️ Aspectos temporais**: análise de duração, tempo (BPM) e outras métricas temporais

### 🧭 Como Navegar no Dashboard

Use o **menu de navegação na barra lateral** para explorar as diferentes seções:

* **📊 Visão Geral**: Distribuições gerais de popularidade, gêneros e características básicas
* **🎼 Características Musicais**: Análise interativa das features de áudio (energia, danceabilidade, valência, etc.)
* **🎤 Análise de Artistas**: Insights sobre artistas mais populares, produtivos e suas características musicais
* **🎸 Gêneros Musicais**: Exploração detalhada dos 114 gêneros e suas peculiaridades
* **⏱️ Análise Temporal**: Estudo sobre duração das faixas, BPM e assinatura temporal

### 🔍 Funcionalidades dos Filtros

Cada página possui **filtros interativos** que permitem:

- **Filtrar por gênero**: Selecione um ou múltiplos gêneros específicos
- **Ajustar faixas de popularidade**: Explore faixas com diferentes níveis de popularidade
- **Selecionar características musicais**: Filtre por energia, danceabilidade, valência, etc.
- **Configurar intervalos temporais**: Analise faixas por duração ou BPM

**💡 Dica**: Os filtros são aplicados em tempo real e afetam todos os gráficos da página!

---

## 🏆 Destaques do Dataset

""")

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    **🎵 Faixa Mais Popular**
    
    **"{stats['track_mais_popular']}"**  
    por *{stats['artista_track_mais_popular']}*
    """)

with col2:
    st.success(f"""
    **🎸 Gênero Mais Comum**
    
    **{stats['genero_mais_comum'].title()}**  
    ({df['track_genre'].value_counts().iloc[0]:,} faixas)
    """)

# Gráfico de popularidade geral
st.markdown("---")
st.subheader("🎯 Distribuição de Popularidade das Faixas")

fig_pop = px.histogram(
    df, 
    x='categoria_popularidade',
    title="Distribuição das Faixas por Categoria de Popularidade",
    labels={'categoria_popularidade': 'Categoria de Popularidade', 'count': 'Número de Faixas'},
    color_discrete_sequence=['#1DB954']
)
fig_pop.update_layout(height=400)
st.plotly_chart(fig_pop, use_container_width=True)

# Preview dos dados
st.markdown("---")
st.subheader("📋 Preview dos Dados")
st.markdown("Primeiras 10 faixas do dataset ordenadas por popularidade:")

preview_cols = ['track_name', 'primeiro_artista', 'album_name', 'track_genre', 'popularity', 'duration_min', 'energy', 'danceability']
st.dataframe(
    df[preview_cols].head(10),
    column_config={
        'track_name': 'Faixa',
        'primeiro_artista': 'Artista',
        'album_name': 'Álbum', 
        'track_genre': 'Gênero',
        'popularity': 'Popularidade',
        'duration_min': st.column_config.NumberColumn('Duração (min)', format="%.1f"),
        'energy': st.column_config.NumberColumn('Energia', format="%.2f"),
        'danceability': st.column_config.NumberColumn('Danceabilidade', format="%.2f")
    },
    hide_index=True
)

# Informações adicionais
st.markdown("---")
st.subheader("ℹ️ Sobre o Dataset")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **📊 Estatísticas Gerais:**
    - **Total de faixas**: {stats['total_tracks']:,}
    - **Artistas únicos**: {stats['total_artists']:,}
    - **Álbuns únicos**: {stats['total_albums']:,}
    - **Gêneros musicais**: {stats['total_genres']}
    - **Faixas explícitas**: {stats['tracks_explicitas']:,} ({stats['percentual_explicitas']}%)
    """)

with col2:
    st.markdown(f"""
    **🎵 Características Musicais:**
    - **Duração média**: {stats['duracao_media_min']:.1f} minutos
    - **Popularidade média**: {stats['popularidade_media']}/100
    - **Features de áudio**: 13 características diferentes
    - **Assinaturas temporais**: de 0 a 5 batidas por compasso
    """)

st.markdown("""
---
**🎨 Desenvolvido com Streamlit | 📊 Visualizações com Plotly | 🐍 Python & Pandas**

*Explore as páginas do menu lateral para descobrir insights fascinantes sobre a música no Spotify!*
""")

# Sidebar com informações adicionais
with st.sidebar:
    st.header("🎵 Spotify Analytics")
    st.markdown("**Dashboard de Análise Musical**")
    
    st.markdown("---")
    st.subheader("📊 Quick Stats")
    st.metric("Faixas", f"{stats['total_tracks']:,}")
    st.metric("Artistas", f"{stats['total_artists']:,}")
    st.metric("Gêneros", stats['total_genres'])
    
    st.markdown("---")
    st.subheader("🎯 Top Gênero")
    top_genre = df['track_genre'].value_counts().head(1)
    st.write(f"**{top_genre.index[0]}**")
    st.write(f"{top_genre.iloc[0]:,} faixas")
    
    st.markdown("---")
    st.info("💡 Use as páginas do menu para explorar análises detalhadas!")
