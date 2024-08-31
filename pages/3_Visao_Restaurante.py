# ----------
#  LIBRIES
# ----------

import streamlit as st
import pandas as pd 
from PIL import Image
from haversine import haversine
import numpy  as np 
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config (page_title='Visão Restaurantes', page_icon= '🍟', layout='wide' )

# ---------------
#   FUNÇOES
# ---------------

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

def mean_distance (df):
    """ Essa funçao tem por finalidade calcular distancia entre os pontos,
    criar uma coluna com a distancia,
    plotar um gráfico com a distancia média por tráfico
    """
    cols=['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df['Distance']=(df.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude'] ), 
                                               (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ) )

    mean_distance_delivery = np.round(df['Distance'].mean(), 2)
    
    return mean_distance_delivery

def mean_std_festival (df, op, fest):
    """ Essa funçao tem por finalidade selecionar as colunas Festival e Time_taken(min), agrupando por festival
    a fim de calcular a média e desvio padrao do tempo no festival, 
    plotando a media do tempo com o festival
        Parametros:
        
        INPUT: * df = Dataframe, dados necessarios para calculo;
               * op = Tipo de operaçao que precisa ser calculado:
                    - 'mean_time': calcula o tempo médio
                    - 'std_time': calcula o desvio padrao do tempo;
               * fest = Dizer se é com festival ou sem:
                   - 'Yes': com fetival
                   - 'No' : sem festival.
                   
        OUTPUT: * df: Dataframe com 2 colunas e 1 linha.
    """
    
    dfms = ( df.loc[:, ['Festival', 'Time_taken(min)']]
               .groupby('Festival')
               .agg({'Time_taken(min)': [ 'mean', 'std']}) )

    dfms.columns=['mean_time', 'std_time']
    dfms= dfms.reset_index()

    dfms=np.round(dfms.loc[dfms['Festival']== fest, op], 2)
            
    return dfms

def mean_time_delivery (df):
    """" Essa funçao tem por finalidade selecionar as colunas City e Time_taken(min), agrupando por City
    a fim de calcular o tempo médio e desvio padrão de entrega por cidade.
    Plotando um gráfico de barra.
    """
    dfms = df.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': [ 'mean', 'std']})
    dfms.columns=['mean_time', 'std_time']
    dfms= dfms.reset_index()
    # gráfico barra
    fig=go.Figure()
    fig.add_trace(go.Bar(y=dfms['mean_time'],
                         x=dfms['City'],
                         name='Control',
                         error_y=dict(type='data', array=dfms['std_time'])))
    
    fig.update_layout(barmode='group')
            
    return fig

def std_mean_city_order (df):
    """" Essa funçao tem por finalidade selecionar as colunas Type_of_order, City e Time_taken(min), agrupando por Type_of_order e City
    a fim de calcular a média e o desvio padrao de entrega por cidade e tipo de serviço.
    """
    cols= ['Type_of_order', 'City', 'Time_taken(min)']
    dfms = df.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': [ 'mean', 'std']})
                    
    dfms.columns=['mean_time', 'std_time']
    dfms= dfms.reset_index()
    
    return dfms

def distance_time (df):
    """" Essa funçao tem por finalidade selecionar as colunas de localizaçao dos restaurantes e pontos de entregar.
    Criar uma coluna com o valor dessas distancia.
    Realizar a media da distancia por cidade.
    Plotar um grafico com a media de distancia por cidade
    """
    cols=['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df['Distance']=(df.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude'] ), 
                                               (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ) )

    avg_distance=df.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()
                    
    fig=go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['Distance'], pull=[0, 0.1, 0])])
            
    return fig 

def mean_std_city_traffic (df):
    """" Essa funcao tem por finalidade selecionar as colunas Road_traffic_density, City e Time_taken(min), agrupando por Road_traffic_density e City
    a fim de calcular a media do tempo por cidade e tipo de grafico.
    plotar um grafico com a media e desvio padrao da media do tempo separado por cidade e tipo de trafico
    """
    dfms =( df.loc[:, ['Road_traffic_density', 'City', 'Time_taken(min)']]
              .groupby(['City', 'Road_traffic_density'])
              .agg({'Time_taken(min)': [ 'mean', 'std']}) )
    
    dfms.columns=['mean_time', 'std_time']
    dfms= dfms.reset_index()
    # gráfico solar
    fig= px.sunburst(dfms, path=['City', 'Road_traffic_density'], 
                           values='mean_time', color='std_time', 
                           color_continuous_scale='RdBu',
                           color_continuous_midpoint=np.average(dfms['std_time'])) 
    return fig

# ---------------
# IMPORT DATASET
# ---------------
df_= pd.read_csv('train.csv')
df = df_.copy()

# ------------------------
#    LIMPEZA DATAFRANE
# ------------------------

df = clean_code (df)

#             ----- VISAO RESTAURANTES --------

st.header( ' Marketplace - Visão Restaurantes') 

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
#    LAYOUT VISAO RESTAURANTES
# =================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    
# primeira linha e 1 coluna
    with st.container():
        st.markdown('### Overal Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='medium')
        with col1:
            ent=df.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos', ent)
            
        with col2:
            m_distance_delivery = mean_distance (df)
            col2.metric('Distancia média', m_distance_delivery)
            
        with col3:
            festival1= mean_std_festival (df, op='mean_time', fest='Yes')
            col3.metric('Média tempo c/ Festival', festival1)
            
        with col4:
            festival2 = mean_std_festival (df, op='std_time', fest='Yes')
            col4.metric('Desvio padrão c/ Festival', festival2)
            
        with col5:
            festival3= mean_std_festival (df, op='mean_time', fest='No')
            col5.metric('Média tempo s/ Festival', festival3)
            
        with col6:
            festival4 = mean_std_festival (df, op='std_time', fest='No')
            col6.metric('Desvio padrão s/ Festival', festival4)
   
 # segunda linha com 2 colunas
    with st.container():
        st.markdown("""---""")
        st.markdown('### Tempo medio de entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#####  Tempo médio e desvio padrão entrega por cidade')
            fig1 = mean_time_delivery (df)
            st.plotly_chart(fig1,use_container_width=True, sharing="streamlit")
        
        with col2:
            st.markdown('#####  Tempo médio e desvio padrão entrega por cidade e tipo de serviço')
            mean_std_df = std_mean_city_order (df)
            st.dataframe(mean_std_df)        
            
# terceira linha com 2 colunas        
    with st.container():
        st.markdown("""---""")
        st.markdown('### Distribuição do Tempo')
    
        col1, col2 = st.columns(2, gap='large')
        with col1:
            fig = distance_time (df)
            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            st.markdown('##### Tempo médio e desvio padrão entrega cidade e tipo de tráfego')
            fig = mean_std_city_traffic (df)
            st.plotly_chart(fig, use_container_width=True, sharing="streamlit")
            