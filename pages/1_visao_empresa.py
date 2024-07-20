# Importando as bibliotecas necessárias
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(
    page_title='Marketplace - Visão Empresa',
    layout='wide',
    initial_sidebar_state="expanded"
)

# ---------------------------------
# Funções
# ---------------------------------

def country_maps(df1):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    
    folium_static(map, width=1024 , height=600)

def order_share_by_week(df1):
    # Quantidade de pedidos por semana / Número único de entregadores por semana
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    # Juntar os dois dataframe
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    # Criando uma nova coluna
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # Gerando o gráfico de linhas
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')

    return fig

def order_by_week(df1):
    # criar a coluna da semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, 'week_of_year', y='ID')
    return fig

def traffic_order_city(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def traffic_order_share(df1):
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
    return fig

def order_metric(df1):
    cols = ['ID', 'Order_Date']
    # selecao de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()       
    # desenhar o gráfico de linhas
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig


def clean_code(df1):
    """ 
    
    Esta função tem a responsabilidade de limpar o dataframe

    Tipos de Limpeza:
    1. Remoção dos dados NaN.
    2. Mudança do tipo da coluna de dados.
    3. Remoção dos espaços das variáveis de texto.
    4. Formatação da coluna de datas.
    5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

    Input: DataFrame
    Output: DataFrame
    
    """
    # 1. Convertendo a coluna Age de texto para número
    linhasSelecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhasSelecionadas, :].copy()
    
    linhasSelecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhasSelecionadas, :].copy()
    
    linhasSelecionadas = (df1['Time_taken(min)'] != 'NaN ')
    df1 = df1.loc[linhasSelecionadas, :].copy()
    
    linhasSelecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhasSelecionadas, :].copy()
    
    linhasSelecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhasSelecionadas, :].copy()
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    # 2. convertendo a coluna Rating de texto para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # 3. convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    # 4. convertendo multiple_deliveries de texto para numero inteiro (int)
    linhasSelecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhasSelecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    ## 5. Removendo os espaços dentro de strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    # 6. Limpando a coluna de time taken
    df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].apply(lambda x: x.split(' ')[1])
    df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].astype(int)
    
    df1 = df1.reset_index(drop=True)

    return df1
# --------------------------------- Inicio da estrutura lógica do código ---------------------------------
# ---------------------
# Import dataset
# ---------------------
df = pd.read_csv('dataset/train.csv')


# ---------------------
# Limpando os dados
# ---------------------
df1 = clean_code(df)


# ====================================
# BARRA LATERAL
# ====================================

st.header('Marketplace - Visão Empresa')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=200)

st.sidebar.markdown('# Cury Company')
#st.sidebar.header('Parâmetros')
#info_sidebar = st.sidebar.empty()
# Aqui o placeholder vazio finalmente é atualizado com dados do filtered_df
#info_sidebar.info('{} entregas.'.format(df1.shape[0]))
st.sidebar.info('Análise dos dados de entregas, pedidos e avaliações disponibilizados pelo aplicativo da Cury Company, que conecta restaurantes, entregadores e consumidores. Projeto de Data Science voltado para a análise exploratória dos principais KPIs de crescimento da empresa.')
st.sidebar.markdown('---')

# Checkbox da tabela
st.sidebar.markdown('# Classificação')
st.sidebar.subheader('Tabela')
tabela = st.sidebar.empty()


st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    "Até qual valor?",
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format="DD-MM-YYYY")



st.sidebar.markdown('---')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)
st.sidebar.markdown('---')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Informações no rodapé da Sidebar
st.sidebar.markdown("""
Todos os dados usados aqui foram obtidos a partir do site [Kaggle](https://www.kaggle.com/datasets/gauravmalik26/food-delivery-dataset?select=train.csv)

Para esta análise exploratória inicial, será baixado apenas o seguinte:

`train.csv`.
""")
st.sidebar.markdown('---')
st.sidebar.markdown('\n')
st.sidebar.markdown("Redes Sociais :")
st.sidebar.markdown("- [Linkedin](https://www.linkedin.com/in/igorleonel/)")
st.sidebar.markdown("- [Portfólio](https://igorleonel.github.io/portfolio_projetos/)")
st.sidebar.markdown("- [Github](https://github.com/igorleonel)")
st.sidebar.markdown("- [Medium](https://medium.com/@igor__leonel)")


# ====================================
# LAYOUT STREAMLIT
# ====================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)   


    
with tab2:
    with st.container():
        st.markdown('# Order By Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
            

    with st.container():
        st.markdown('# Order Share By Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)


with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
    
































