import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import folium
from folium.plugins import HeatMap


st.set_page_config(layout="wide")
st.sidebar.info(""" Çevre ve Şehircilik Bakanlığı - Hasar Tespit
        Bu uygulama https://hasartespit.csb.gov.tr/ sitesinde paylaşılan hasar tespiti yapılmış binaların durumunu göstermek amacıyla yapılmıştır.
    """)

@st.cache
def data():
    df = pd.read_parquet("data/binatespit.parquet.gzip")
    return df
df = data()


df_il_pivot = df.pivot_table(values="ilce",index="il",columns="aciklama",aggfunc="count").round(0).fillna(0)
df_il_pivot = df_il_pivot[['Yıkık','Acil Yıktırılacak', 'Ağır Hasarlı','Az Hasarlı', 'Hasarsız','Tespit Yapılamadı',
       'Bina Kilitli İnceleme Yapılamadı (Girilemedi)', 
        'Değerlendirme Dışı',  'Kapsam Dışı']]



with st.sidebar:
    iller = df["il"].unique().tolist()

    filtre_ilce = None
    filtre_mah = None
    filtre_durum = None
    durumlar = df["aciklama"].unique().tolist()


    filtre_il = st.multiselect("İl Seçiniz: ",iller,default=["Hatay"])


    if filtre_il:
        df = df[df["il"].isin(filtre_il)]
        ilceler = df["ilce"].unique().tolist()
        filtre_ilce = st.multiselect("İlçe Seçiniz: ",ilceler)
    

    if filtre_ilce:
        df = df[df["ilce"].isin(filtre_ilce)]
        mahalleler = df["mahalle"].unique().tolist()
        filtre_mah = st.multiselect("Mahalle Seçiniz: ",mahalleler)



    if filtre_mah:
        df = df[df["mahalle"].isin(filtre_mah)]
        durumlar = df["aciklama"].unique().tolist()



    filtre_durum = st.multiselect("Bina Durumu: ",durumlar,default=['Yıkık','Acil Yıktırılacak', 'Ağır Hasarlı'])
    if filtre_durum:
        df = df[df["aciklama"].isin(filtre_durum)]


st.write("HeatMap: Filtrelere göre hasar tespiti yapılan binalar.")

m = folium.Map(max_zoom=16)

folium.TileLayer(
        tiles='http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}',
        attr='Google Terrain',
        name='Google Satellite',
        overlay=True,
        show=True,max_zoom=16
        ).add_to(m)
df = df[df["x"].isna()==False]
coor = [[i["y"],i["x"]] for _,i in df.iterrows()]
HeatMap(coor,radius=18).add_to(m)
m.fit_bounds(m.get_bounds())



html = m.get_root().render()
components.html(html,height= 500,scrolling=False)

st.write("Filtrelere Göre Bina Sayıları: ")

df_pivot = df.pivot_table(values="binaNo",index=["il","ilce","mahalle"],columns="aciklama",aggfunc="count").fillna(0)
st.write(df_pivot.style.format(precision=0))




st.write("Deprem illerine göre hasar tespit durumu: ")

st.dataframe(df_il_pivot.style.format(precision=0))
