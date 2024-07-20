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

st.set_page_config(
    page_title='Marketplace - Visão Restaurantes',
    layout='wide',
    initial_sidebar_state="expanded"
)

# ---------------------------------
# Funções
# ---------------------------------

def avg_std_time_on_traffic(df1):
    df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg(['mean', 'std'])
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_std_time_graph(df1):
    df_aux = df1.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg(['mean', 'std'])
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_delivery(df1, festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df: Dataframe com os dados neessários para o cálculo
                - op: tipo de operação que precisa ser calculado
                    'avg_time': Calcula o tempo médio
                    'std_time': Calcula o desvio padrão do tempo.
            Output:
                - df: Dataframe com 2 colunas e 1 linha.
    """
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg(['mean', 'std'])
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = df_aux.loc[df_aux['Festival'] == festival, op]
    for i in df_aux:
      df_aux = np.round(i, 2)
    return df_aux

def distance(df1, fig):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
        
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

st.header('Marketplace - Visão Restaurantes')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=200)

st.sidebar.markdown('# Cury Company')
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
        st.markdown('# Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores unicos', delivery_unique)
            
        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('A distância média', avg_distance) 
            
        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Tempo Médio', df_aux)
            
        with col4:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('STD Entrega', df_aux)
        
        with col5:
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric('Tempo Médio', df_aux)
            
        with col6:
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric('STD Entrega', df_aux)
            

    with st.container():
        st.markdown('---')
        # Raw data
        if tabela.checkbox('Mostrar a tabela de dados'):
            st.write(df1)
        st.markdown('## Tempo médio de entrega por área urbana')
        fig = avg_std_time_graph(df1)
        st.plotly_chart(fig)
        
        

    with st.container():
        st.markdown('---')
        st.markdown('## Distribuição do tempo')
        col1, col2 = st.columns(2)
        
        with col1:
            
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig)
            
            df_aux = df1.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg(['mean', 'std'])
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            fig = go.Figure()
            
            # fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
            # fig.update_layout(barmode='group')
            # st.plotly_chart(fig)
            # fig = distance(df1, fig=True)
            # st.plotly_chart(fig)
        
        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)

    with st.container():
        st.markdown('---')
        st.markdown('## Distribuição da distância por tipo de pedido')
        cols = ['Time_taken(min)', 'City', 'Type_of_order']
        df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg(['mean', 'std'])
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        df_aux


























