 # ----------
#  LIBRIES
# ----------

import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas as pd 
import numpy  as np 
import plotly.express as px
from haversine import haversine
from PIL import Image


st.set_page_config (page_title='Visão Empresa', page_icon= '📊', layout='wide' )
# --------------
#.    FUNÇOES
# --------------
def clean_code(df):
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

def order_metric(df):
    """
    Essa funçao tem por finalidade selecionar as colunas de ID e Order_Date, 
    agrupando pela coluna de Order_Date a fim de plotar um gráfico com a quatidade de pedidos por dia 
    """
    
    coluns=['ID', 'Order_Date']
    data_fig=df.loc[:, coluns].groupby('Order_Date').count().reset_index()
    # gráfico barras 
    fig=px.bar(data_fig, x='Order_Date', y='ID')
    
    return fig

def traffic_order_share(df):
    """Essa funçao tem por finalidade selecionar as colunas ID e Road traffic densiti, 
    agrupando por Road traffic density a fim de plotar um gráfico com a distribuiçao de pedidos por tipo de tráfico
    """
    data= df.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    data['perc_id']= 100 * (data['ID']/data['ID'].sum())
    # gráfico pizza
    fig=px.pie(data, values='perc_id', names='Road_traffic_density')
            
    return fig

def traffic_order_city(df):
    """" Essa funçao tem por finalidade selecionar as colunas ID, City e Road traffic density,
    agrupando por City e Road traffic density a fim de plotar um gráfico com a comparação do volume de pedidos por cidade e tipo de tráfego
"""
    data=df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    #gráfico bolha
    fig=px.scatter(data, x='City', y='Road_traffic_density', size='ID', color='City')
    
    return fig

def order_by_week(df):
    """" Essa funçao tem por finalidade criar uma nova coluna chamada de Week Order, contendo a semana do ano com base na coluna Order Date.
    Selecionar as colunas Week Order e ID, agrupando por Week Order a fim de plotar um gráfico com a quantidade de pedidos por semana.
"""
    df['Week_Order']=df['Order_Date'].dt.strftime('%U')
    sel=['Week_Order', 'ID']
    data_fig=df.loc[:, sel].groupby('Week_Order').count().reset_index()
    #gráfico linha
    fig=px.line(data_fig, x='Week_Order', y='ID')
    
    return fig

def order_share_by_week(df):
    """"Essa funçao tem por finalidade selecionar as colunas ID e Week Order, agrupando por Week Order a fim de contar os pedidos por semana.
    Selecionar as colunas Delivery person ID e Week Order, agrupando por Week Order a fim selecionar a quantidade de pedidos por semana dividido por numero de entregadores unicos por semana.
    Apos as seleçoes plotar um gráfico com a quantidade de pedidos por entregador por semana.
"""
    pedi=df.loc[:, ['ID', 'Week_Order']].groupby('Week_Order').count().reset_index()
    entre=df.loc[:, ['Delivery_person_ID', 'Week_Order']].groupby('Week_Order').nunique().reset_index()
    # juntar os dois dataframe
    dfax=pd.merge(pedi, entre, how='inner')
    dfax['order_delivery']=dfax['ID'] / dfax['Delivery_person_ID']
    # gráfico linha
    fig= px.line(dfax, x='Week_Order', y='order_delivery' )
    
    return fig 

def country_map (df):
    """" Essa funçao tem por finalidade plotar um mapa com a  localização central de cada cidade por tipo de tráfego
"""
    df_ax=df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    #mapa
    mapa = folium.Map()

    for a in range(len(df_ax)):
        folium.Marker( [df_ax.loc[a, 'Delivery_location_latitude'], df_ax.loc[a, 'Delivery_location_longitude' ]], popup=df_ax.loc[a, ['City', 'Road_traffic_density']]).add_to(mapa)
        
    # plotando o mapa streamlit
    folium_static(mapa, width=1024 , height=600 )

# ---------------
# IMPORT DATASET
# ---------------
df_=pd.read_csv('train.csv')
df=df_.copy()

# ------------------------
#    LIMPEZA DATAFRANE
# ------------------------

df = clean_code(df)

#        ---------- VISAO EMPRESA --------

st.header(' Marketplace - Visão Cliente') 

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
#        LAYOUT VISAO EMPRESA
# =================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    # primeira linha e 1 coluna
    with st.container():
        # Order metric
        st.markdown('## Order by Day')
        fig1=order_metric(df)
        st.plotly_chart(fig1, use_container_width=True)
    
    #segunda linha e 2 colunas
    with st.container():
        col1, col2 = st.columns(2)
        # 
        with col1:
            st.markdown('## Traffic Order Share')
            fig2 = traffic_order_share(df)
            st.plotly_chart(fig2, use_container_width=True)
            
        with col2:
            st.markdown('## Traffic Order City')
            fig3=traffic_order_city(df)
            st.plotly_chart(fig3, use_container_width=True)

# Aba visao tatica  
with tab2:
    with st.container():
        st.markdown('## Order by Week')
        fig2=order_by_week(df)
        st.plotly_chart(fig2, use_container_width=True)
        
    with st.container():
        fig3= order_share_by_week(df)
        st.plotly_chart(fig3, use_container_width=True)   

# Aba visao geografica    
with tab3: 
    st.markdown('## Country Maps')
    country_map(df)
    
    
    
