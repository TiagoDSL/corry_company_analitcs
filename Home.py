#------------------------
#      LIBRIES
#------------------------

import streamlit as st
from PIL import Image

#-----------------------
# IMPORT IMAGE HOME
#-----------------------

st.set_page_config(
    page_title='Home',
    page_icon='🎲'
)

#image_path = '/Users/tiagoleite/Desktop/Materiais_FTC/project/'
image=Image.open( 'logo.png')
st.sidebar.image(image, width=120)

#-----------------------
#    BARRA LATERAL
#-----------------------

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""----""") 

st.write('# Curry Company Growth Dashboard')

st.markdown (
   """ 
    Growth Dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dasboard?
    - VISÃO EMPRESA:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de comportamento.
        - Visão Geográfica: Insights de geolocalização.
        
    - VISÃO ENTREGADOR:
        - Acompanhamento dos indicadores semanais de crescimento.
          
    - VISÃO RESTAURANTES:
        - Indicadores semanais de crescimento dos restaurantes.
          
          
  ### Ask for Help
    - Time Data Science no Discord
    @TiagoL
        
   """ )

