# ----------
#  LIBRIES
# ----------

import streamlit as st
import pandas as pd 
from PIL import Image

st.set_page_config (page_title='Visão Entregadores', page_icon= '🚚', layout='wide' )

# -----------------------
#.       FUNÇOES
#------------------------
def clean_code (df):
    """ Está funcao tem a resp[onsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remove os espaços vazios
        2. Remove os dadps 'NaN '
        3. Conversão de tipo de variável
        4. Conversão de data
        5. Limpeza da coluna de tempo (remoçao de texto da variavel numerica
        
        Input: DataFrame
        Output: Data Frame 
     """
    
    # Removendo os espaços vazios
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()

    # Removendo linhas NaN de City
    linhas_vazia = df['City'] != 'NaN'
    df = df.loc[linhas_vazia, :]

    # Removendo linhas NaN de Delivery_person_Age
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    #Removendo linhas NaN de Road_traffic_density
    linha_vazia = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linha_vazia, :]

    # Removendo linhas NaN de Festival
    lin_vazia = df['Festival'] != 'NaN'
    df = df.loc[lin_vazia, :]

    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    # Conversao de data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # Removendo  linhas  'NaN '  de multiple_deliveries   
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # conversão categoria multiple_deliveries 
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    # Comando para remover o texto "(min)" de Time_taken(min) do número
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split ( '(min)' )[1])

    # tranformar em int
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
    
    return df 

def delivery_rating (df):
    """"Essa funçao tem por finalidade selecionar as colunas Delivery_person_ID e Delivery_person_Ratings,
    agrupando por Delivery_person_ID a fim de calcular a avaliaçao media por entregador
    """
    avaliacao_= ( df.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                    .groupby('Delivery_person_ID')
                    .mean()
                    .reset_index() )
    return avaliacao_

def mean_traffic(df):
    """ Essa funçao tem por finalidade selecionar as colunas Delivery_person_Ratings e Road_traffic_density, 
    agrupando por Road_traffic_density a fim de calcular a media e o desvio patrao das avaliaçoes de acordo com o trafico 
    """
    mean_std_traffic = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                             .groupby('Road_traffic_density')
                             .agg({'Delivery_person_Ratings': ['mean', 'std']}))

    mean_std_traffic.columns=['Delivery_mean', 'Delivery_std']
    mean_std_traffic.reset_index()
            
    return mean_std_traffic

def mean_weatherconditions (df):
    """" Essa funçao tem por finalidade selecionar Delivery_person_Ratings e Weatherconditions,
    agrupando por Weatherconditions a fim de calcular a media e desvio padrao das avaliaçoes de acordo com tipo de clima
    """
    mean_std_weather = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                             .groupby('Weatherconditions')
                             .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            
    mean_std_weather.columns=['Delivery_mean', 'Delivery_std']
    mean_std_weather.reset_index()
            
    return mean_std_weather

def top_delivery (df, order_asc):
    """ Essa funçao tem por finalidade selecionar as colunas Delivery_person_ID, City e Time_taken(min), agrupando
    por Delivery_person_ID e City a fim de calcular os entregadores mais rapidos e mais lentos pela media do tempo
    """
    # calculo dos mais rápidos pela media do tempo
    speed_delivery=( df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                      .groupby(['City', 'Delivery_person_ID'])
                      .mean()
                      .sort_values(['City', 'Time_taken(min)'], ascending=order_asc)
                      .reset_index() )
    # selecionar as 10 primeiras linhas de cada cidade
    metro= speed_delivery.loc[speed_delivery['City']=='Metropolitian' ,:].head(10)
    urban= speed_delivery.loc[speed_delivery['City']=='Urban',:].head(10)
    semi_u= speed_delivery.loc[speed_delivery['City']=='Semi-Urban',:].head(10)

    # concatenar
    speed_= pd.concat([metro, urban, semi_u]).reset_index(drop=True)
    
    return speed_

# ---------------
# IMPORT DATASET
# ---------------
df_=pd.read_csv('train.csv')
df=df_.copy()

# ------------------------
#    LIMPEZA DATAFRANE
# ------------------------
df = clean_code(df)

#             ----- VISAO ENTREGADORES --------

st.header( ' Marketplace - Visão Entregadores') 

# =============================
#    BARRA LATERAL
# ============================= 

#image_path= 'logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""----""") 

st.sidebar.markdown('## Selecione uma Data Limite')
date_slider= st.sidebar.slider ( 
    'Até qual valor?', 
    value=pd.datetime(2022, 4, 13), 
    min_value=pd.datetime(2022, 2, 11), 
    max_value=pd.datetime(2022, 4, 6), format='DD/MM/YYYY')

st.sidebar.markdown("""----""") 
st.sidebar.markdown('## Selecione uma Condição de Trânsito')
traffics=st.sidebar.multiselect('Condições de Trânsito', 
                                 ['Low', 'Medium', 'High' , 'Jam'],
                                 default=['Low', 'Medium', 'High', 'Jam'] )
st.sidebar.markdown("""----""") 
st.sidebar.markdown('Powered by Comunidade DS') 

# filtro data
selecionadas = df['Order_Date']< date_slider
df=df.loc[selecionadas,:]

# filtro condiçao de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffics)
df = df.loc[linhas_selecionadas, :]

# =================================
#     LAYOUT VISAO ENTREGADORES
# =================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])
with tab1:
    # primeira linha com 4 colunas
    with st.container():
        st.markdown('## Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            maior_idade=df.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2:
            menor_idade=df.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            melhor=df.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor)
            
        with col4:
            pior=df.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior)
    
    # segunda linha com 2 colunas, sendo uma coluna com 2 linhas
    with st.container():
        st.markdown("""---""")
        st.markdown('## Avaliações')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avaliação média por entregador ')
            avaliacao_entregador= delivery_rating (df)
            st.dataframe(avaliacao_entregador)
            
        with col2:
            st.markdown('##### Avaliação média por trânsito ')
            media_trafico = mean_traffic(df)
            st.dataframe(media_trafico)
            
            st.markdown('##### Avaliação média por condições climáticas ')
            media_climatica = mean_weatherconditions(df)
            st.dataframe(media_climatica)
            
    # terceira linha com 2 colunas
    with st.container():
        st.markdown("""---""")
        st.markdown('## Velocidade de entrega ')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Top entregadores mais rápidos ')
            fast = top_delivery(df, order_asc=True)
            st.dataframe(fast)
            
        with col2:
            st.markdown('#### Top entregadores mais lentos ')
            slow =  top_delivery (df, order_asc=False)
            st.dataframe(slow)
  