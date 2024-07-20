# Importando as bibliotecas necessárias
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

# ---------------------------------
# Funções
# ---------------------------------

st.set_page_config(
    page_title='Marketplace - Visão Entregadores',
    layout='wide',
    initial_sidebar_state="expanded"
)

def top_delivers(df1, top_asc):
    df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).max().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index()
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df3
    

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

# import dataset
df = pd.read_csv('dataset/train.csv')

# limpando os dados
df1 = clean_code(df)

# ====================================
# BARRA LATERAL
# ====================================

st.header('Marketplace - Visão Entregadores')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            # A maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)

        with col2:
            # A menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor de idade', menor_idade)
            
        with col3:
            # A melhor condicao
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condicao', melhor_condicao)
    
        with col4:
            # A pior condicao
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condicao', pior_condicao)

    with st.container():

        st.markdown('---')
        # Raw data
        if tabela.checkbox('Mostrar a tabela de dados'):
            st.write(df1)

        st.title('Avaliacoes')

        col1, col2 = st.columns(2)

        with col1:
            
            st.markdown('#### Avaliacoes media por entregador')
            cols = ['Delivery_person_Ratings', 'Delivery_person_ID']
            df_avg_ratings_per_deliver = df1.loc[:, cols].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(df_avg_ratings_per_deliver)

        with col2:

            st.markdown('##### Avaliacao media por transito')
            df_avg_std_rating_by_traffic = ( df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']].groupby('Road_traffic_density')
                           .agg({'Delivery_person_Ratings': ['mean', 'std']}) )
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)


            st.markdown('##### Avaliacao media por clima')
            df_avg_std_rating_by_weather = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions')
                           .agg({'Delivery_person_Ratings': ['mean', 'std']}) )

            # Mudança de nome das colunas
            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
            
            # reset do index
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe(df_avg_std_rating_by_weather)


        with st.container():

            st.markdown('---')

            st.title('Velocidade de entrega')

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('##### Top entregadores mais rapidos')
                df3 = top_delivers(df1, top_asc=True)
                st.dataframe(df3)

            with col2:
                st.markdown('##### Top entregadores mais lentos')
                df3 = top_delivers(df1, top_asc=False)
                st.dataframe(df3)


            



































