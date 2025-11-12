# 🎵 Spotify Music Analytics Dashboard

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white)

Dashboard interativo desenvolvido com **Streamlit** para análise exploratória de dados musicais do Spotify.

## 🎯 Objetivo do Dashboard

Este dashboard foi desenvolvido para explorar e visualizar um extenso dataset com **114.000+ faixas musicais** do Spotify, oferecendo insights profundos sobre:

- **🎼 Características musicais**: análise de danceabilidade, energia, valência e outras features de áudio
- **🎤 Artistas e popularidade**: identificação de tendências e padrões de sucesso  
- **🎸 Gêneros musicais**: exploração detalhada dos 114 gêneros presentes no dataset
- **⏱️ Aspectos temporais**: análise de duração, tempo (BPM) e outras métricas temporais

## 📊 Estrutura do Dashboard

### Páginas Principais:

1. **🏠 Principal** (`01_Principal.py`)
   - Página inicial com visão geral do dataset
   - Métricas principais e introdução ao projeto
   
2. **📊 Visão Geral** (`pages/02_📊_Visão_Geral.py`)
   - Distribuições gerais de popularidade e gêneros
   - Análises básicas das características musicais

3. **🎼 Características Musicais** (`pages/03_🎼_Características_Musicais.py`)  
   - Análise interativa das features de áudio
   - Correlações entre características musicais

4. **🎤 Análise de Artistas** (`pages/04_🎤_Artistas.py`)
   - Rankings de artistas mais populares e produtivos
   - Análise das características musicais por artista

5. **🎸 Gêneros Musicais** (`pages/05_🎸_Gêneros.py`)
   - Exploração detalhada dos 114 gêneros
   - Comparações entre características de diferentes gêneros

6. **⏱️ Análise Temporal** (`pages/06_⏱️_Análise_Temporal.py`)
   - Análise de duração das faixas e BPM
   - Distribuições de assinatura temporal

## 🧭 Como Navegar

1. **Menu Lateral**: Use a barra lateral esquerda para navegar entre as páginas
2. **Filtros Interativos**: Cada página possui filtros específicos que afetam todos os gráficos
3. **Gráficos Interativos**: Hover, zoom e seleção disponíveis nos gráficos Plotly

## 🔍 Funcionalidades dos Filtros

Os filtros são aplicados em tempo real e permitem:

- **Filtrar por gênero**: Selecione um ou múltiplos gêneros específicos
- **Ajustar faixas de popularidade**: Explore faixas com diferentes níveis de popularidade  
- **Selecionar características musicais**: Filtre por energia, danceabilidade, valência, etc.
- **Configurar intervalos temporais**: Analise faixas por duração ou BPM

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8+
- pip

### Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/Welto12072007/SpotifyDataset.git
cd SpotifyDataset
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute o dashboard:**
```bash
streamlit run 01_Principal.py
```

### Execução com Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual (Windows)
.venv\Scripts\activate

# Instalar dependências  
pip install -r requirements.txt

# Executar dashboard
streamlit run 01_Principal.py
```

## 📁 Estrutura do Projeto

```
SpotifyDataset/
├── 01_Principal.py           # Página principal
├── Dataset/
│   └── dataset.csv          # Dataset do Spotify (114k faixas)
├── pages/                   # Páginas do dashboard
│   ├── 02_📊_Visão_Geral.py
│   ├── 03_🎼_Características_Musicais.py  
│   ├── 04_🎤_Artistas.py
│   ├── 05_🎸_Gêneros.py
│   └── 06_⏱️_Análise_Temporal.py
├── utils/                   # Utilitários
│   └── carrega_dados.py     # Funções de carregamento de dados
├── requirements.txt         # Dependências do projeto
└── README.md               # Este arquivo
```

## 📦 Dependências

- **streamlit==1.28.2**: Framework para criação do dashboard
- **pandas==2.1.4**: Manipulação e análise de dados
- **plotly==5.17.0**: Visualizações interativas
- **matplotlib==3.8.2**: Gráficos estáticos
- **seaborn==0.13.0**: Visualizações estatísticas
- **numpy==1.24.4**: Computação numérica

## 📊 Sobre o Dataset

- **114.000+ faixas musicais** do Spotify
- **114 gêneros únicos** diferentes
- **13 características de áudio** por faixa
- Dados de **popularidade, artistas, álbuns**
- Features como **energia, danceabilidade, valência, acousticness**

## 🌐 Deploy na Nuvem

### Streamlit Community Cloud

1. **Fork este repositório** para sua conta GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Faça login com sua conta GitHub
4. Clique em "New app" e selecione este repositório
5. Configure o arquivo principal como `01_Principal.py`
6. Clique em "Deploy!"

### Heroku (Alternativa)

1. Crie um arquivo `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[server]
port = $PORT
enableCORS = false
headless = true
[theme]
base = 'dark'
" > ~/.streamlit/config.toml
```

2. Crie um `Procfile`:
```
web: sh setup.sh && streamlit run 01_Principal.py
```

3. Deploy no Heroku normalmente

## 🎨 Tecnologias Utilizadas

- **Frontend**: Streamlit
- **Visualizações**: Plotly, Matplotlib, Seaborn  
- **Processamento**: Pandas, NumPy
- **Versionamento**: Git/GitHub
- **Deploy**: Streamlit Community Cloud

## 📈 Funcionalidades Principais

- ✅ **6+ gráficos interativos** com Plotly
- ✅ **Filtros funcionais** em tempo real
- ✅ **Múltiplas páginas** organizadas  
- ✅ **Interface responsiva** e intuitiva
- ✅ **Documentação completa** integrada
- ✅ **Métricas e insights** automatizados

## 👨‍💻 Autor

**Desenvolvido por**: [Welto12072007](https://github.com/Welto12072007)

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

**🎨 Desenvolvido com Streamlit | 📊 Visualizações com Plotly | 🐍 Python & Pandas**

*Explore o dashboard e descubra insights fascinantes sobre a música no Spotify!*