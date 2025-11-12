import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dados():
    """
    Carrega e processa o dataset do Spotify com features de áudio
    
    Returns:
        pd.DataFrame: Dataset processado e limpo
    """
    # Carrega o dataset original
    df_original = pd.read_csv('./Dataset/dataset.csv')
    
    # Remove a coluna desnecessária
    df = df_original.drop('Unnamed: 0', axis=1)
    
    # Conversões e limpeza dos dados
    
    # Converte duração de milissegundos para segundos e minutos
    df['duration_sec'] = df['duration_ms'] / 1000
    df['duration_min'] = df['duration_sec'] / 60
    
    # Cria categorias de popularidade
    def categorizar_popularidade(pop):
        if pop == 0:
            return 'Sem dados'
        elif pop <= 20:
            return 'Baixa (1-20)'
        elif pop <= 40:
            return 'Média-baixa (21-40)'
        elif pop <= 60:
            return 'Média (41-60)'
        elif pop <= 80:
            return 'Alta (61-80)'
        else:
            return 'Muito Alta (81-100)'
    
    df['categoria_popularidade'] = df['popularity'].apply(categorizar_popularidade)
    
    # Cria categorias de energia
    def categorizar_energia(energia):
        if energia <= 0.3:
            return 'Baixa energia'
        elif energia <= 0.6:
            return 'Média energia'
        else:
            return 'Alta energia'
    
    df['categoria_energia'] = df['energy'].apply(categorizar_energia)
    
    # Cria categorias de dançabilidade
    def categorizar_dancabilidade(dance):
        if dance <= 0.3:
            return 'Pouco dançável'
        elif dance <= 0.6:
            return 'Moderadamente dançável'
        else:
            return 'Muito dançável'
    
    df['categoria_dancabilidade'] = df['danceability'].apply(categorizar_dancabilidade)
    
    # Cria categorias de tempo (duração)
    def categorizar_duracao(duracao_min):
        if duracao_min <= 2:
            return 'Muito curta (≤2min)'
        elif duracao_min <= 3.5:
            return 'Curta (2-3.5min)'
        elif duracao_min <= 5:
            return 'Média (3.5-5min)'
        elif duracao_min <= 7:
            return 'Longa (5-7min)'
        else:
            return 'Muito longa (>7min)'
    
    df['categoria_duracao'] = df['duration_min'].apply(categorizar_duracao)
    
    # Mapeamento de chaves musicais
    chaves_mapa = {
        0: 'C', 1: 'C#/D♭', 2: 'D', 3: 'D#/E♭', 4: 'E', 5: 'F',
        6: 'F#/G♭', 7: 'G', 8: 'G#/A♭', 9: 'A', 10: 'A#/B♭', 11: 'B'
    }
    df['chave_musical'] = df['key'].map(chaves_mapa)
    
    # Mapeamento de modos
    df['modo_musical'] = df['mode'].map({0: 'Menor', 1: 'Maior'})
    
    # Limpa dados de artistas (alguns têm múltiplos artistas separados por ;)
    df['primeiro_artista'] = df['artists'].str.split(';').str[0]
    df['tem_feat'] = df['artists'].str.contains(';', na=False)
    
    # Cria grupos de gêneros principais
    generos_principais = {
        'Pop': ['pop', 'pop-film', 'power-pop', 'indie-pop', 'k-pop', 'j-pop', 'mandopop', 'cantopop'],
        'Rock': ['rock', 'alt-rock', 'alternative', 'hard-rock', 'punk-rock', 'punk', 'rock-n-roll', 
                'grunge', 'psych-rock', 'rockabilly'],
        'Metal': ['metal', 'black-metal', 'death-metal', 'heavy-metal', 'metalcore', 'grindcore'],
        'Eletrônica': ['electronic', 'edm', 'electro', 'house', 'techno', 'trance', 'dubstep', 
                      'drum-and-bass', 'detroit-techno', 'deep-house', 'progressive-house', 'minimal-techno'],
        'Hip-Hop/R&B': ['hip-hop', 'r-n-b'],
        'Jazz/Blues': ['jazz', 'blues'],
        'Latino': ['latin', 'latino', 'samba', 'salsa', 'reggaeton', 'tango', 'sertanejo'],
        'Folk/Acoustic': ['folk', 'acoustic', 'singer-songwriter', 'songwriter', 'country'],
        'Clássico/Opera': ['classical', 'opera', 'piano'],
        'Mundial': ['world-music', 'afrobeat', 'brazilian', 'french', 'german', 'indian', 
                   'iranian', 'turkish', 'spanish', 'swedish', 'malay'],
        'Outros': []  # Será preenchido com o restante
    }
    
    def classificar_genero_principal(genero):
        for categoria, generos in generos_principais.items():
            if genero in generos:
                return categoria
        return 'Outros'
    
    df['genero_principal'] = df['track_genre'].apply(classificar_genero_principal)
    
    # Cria faixas de tempo (BPM)
    def categorizar_tempo(bpm):
        if bpm <= 70:
            return 'Muito Lento (≤70)'
        elif bpm <= 100:
            return 'Lento (71-100)'
        elif bpm <= 120:
            return 'Moderado (101-120)'
        elif bpm <= 140:
            return 'Rápido (121-140)'
        else:
            return 'Muito Rápido (>140)'
    
    df['categoria_tempo'] = df['tempo'].apply(categorizar_tempo)
    
    # Ordena por popularidade descendente
    df = df.sort_values('popularity', ascending=False).reset_index(drop=True)
    
    return df

@st.cache_data
def obter_estatisticas_basicas():
    """
    Retorna estatísticas básicas do dataset
    
    Returns:
        dict: Dicionário com estatísticas básicas
    """
    df = carregar_dados()
    
    stats = {
        'total_tracks': len(df),
        'total_artists': df['primeiro_artista'].nunique(),
        'total_albums': df['album_name'].nunique(),
        'total_genres': df['track_genre'].nunique(),
        'duracao_media_min': round(df['duration_min'].mean(), 2),
        'popularidade_media': round(df['popularity'].mean(), 1),
        'track_mais_popular': df.loc[df['popularity'].idxmax(), 'track_name'],
        'artista_track_mais_popular': df.loc[df['popularity'].idxmax(), 'primeiro_artista'],
        'genero_mais_comum': df['track_genre'].value_counts().index[0],
        'tracks_explicitas': df['explicit'].sum(),
        'percentual_explicitas': round((df['explicit'].sum() / len(df)) * 100, 1)
    }
    
    return stats