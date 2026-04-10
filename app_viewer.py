import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import io

# =================================================================
# CONFIGURAÇÕES V900 - DESIGN INDUSTRIAL (WHITE, GREEN & BLUE DOTS)
# =================================================================
st.set_page_config(page_title="EAF | Central de Auditoria", layout="wide", initial_sidebar_state="collapsed")

# --- CSS DE ALTA FIDELIDADE (CÓPIA DO SEU LAYOUT) ---
st.markdown("""
    <style>
    /* Base Dark */
    .stApp { background-color: #0B0E14; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Uploader Integrado */
    [data-testid="stFileUploader"] { background-color: #161B22; border: 1px dashed #3FB950; border-radius: 4px; padding: 10px; }
    [data-testid="stFileUploader"] section { background-color: #3FB950 !important; }

    /* KPIs de Auditoria */
    [data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 4px; padding: 15px !important; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #3FB950 !important; font-weight: bold !important; font-size: 13px !important; }

    /* CARD DA OS */
    .audit-card { background-color: #0B0E14; border-bottom: 2px solid #161B22; padding: 30px 0; margin-bottom: 10px; }

    /* TEXTOS: BRANCO E VERDE NEON */
    .os-header { font-size: 24px; font-weight: 800; color: #FFFFFF; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
    .label-line { color: #FFFFFF; font-size: 14px; font-weight: 600; margin-top: 8px; }
    .value-green { color: #3FB950; font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 500; }
    
    /* CAIXA DE PARECER (AZUL MARINHO DO SEU PROJETO) */
    .parecer-box {
        background-color: #16212E;
        border: 1px solid #1F3A5D;
        border-radius: 6px;
        padding: 16px;
        margin: 20px 0;
        color: #3FB950;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* DISTÂNCIAS E COORDENADAS */
    .metric-row { color: #3FB950; font-weight: 700; font-size: 14px; margin: 10px 0; }
    .coord-text { color: #3FB950; font-family: monospace; font-size: 13px; margin: 4px 0; }

    /* BOTÕES VERDES COM TEXTO PRETO (PRO) */
    .stLinkButton a {
        background-color: #3FB950 !important;
        color: #000000 !important;
        border-radius: 4px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        border: none !important;
        padding: 12px !important;
        font-size: 13px !important;
        text-align: center;
    }
    .stLinkButton a:hover { background-color: #3FB950 !important; }

    /* Badges de Veredito */
    .v-red { color: #F85149; font-weight: 800; }
    .v-green { color: #3FB950; font-weight: 800; }
    .v-orange { color: #D29922; font-weight: 800; }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

try:
    here_api_key = st.secrets["here_api_key"]
except:
    here_api_key = "TK2TmYxxD8AC0wB5DdG6V07idsfb_iIrtYU5T7CAJMo"

st.markdown("<h1 style='color:white; margin-top:-50px;'>Auditoria </h1>", unsafe_allow_html=True)

up = st.file_uploader("📂 Upload do arquivo de auditoria (.json)", type="json")

if up:
    # Carregamento seguro para evitar erros de versão do Python
    df = pd.DataFrame.from_records(json.load(up))
    
    # Lógica de extração de Status para os filtros
    def clean_status(s):
        s = str(s).upper()
        if "REPROVADO" in s: return "REPROVADO"
        if "VERIFICAR" in s: return "VERIFICAR"
        return "APROVADO"
    
    df['Status_ID'] = df['Status'].apply(clean_status)

    # --- DASHBOARD KPIs ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TOTAL OS", len(df))
    c2.metric("APROVADAS", len(df[df['Status_ID'] == "APROVADO"]))
    c3.metric("A VERIFICAR", len(df[df['Status_ID'] == "VERIFICAR"]))
    c4.metric("REPROVADAS", len(df[df['Status_ID'] == "REPROVADO"]))

    st.divider()

    # --- FILTRO ---
    escolha = st.radio("FILTRAR VISÃO:", ["Todos", "✅ APROVADO", "🟡 VERIFICAR", "❌ 100% REPROVADO"], horizontal=True)
    
    if escolha == "Todos": df_v = df
    elif "APROVADO" in escolha: df_v = df[df['Status_ID'] == "APROVADO"]
    elif "VERIFICAR" in escolha: df_v = df[df['Status_ID'] == "VERIFICAR"]
    else: df_v = df[df['Status_ID'] == "REPROVADO"]

    # --- LOOP DE CARDS ---
    for _, res in df_v.iterrows():
        s_id = res['Status_ID']
        v_class = "v-green" if s_id == "APROVADO" else "v-orange" if s_id == "VERIFICAR" else "v-red"
        
        st.markdown(f"""
        <div class='audit-card'>
            <div class='os-header'>🎫 Ticket: {res['Ticket']}</div>
            <div style='margin-bottom:20px;'><b>Veredito:</b> <span class='{v_class}'>{res['Status']}</span></div>
        """, unsafe_allow_html=True)

        col_txt, col_map = st.columns([1, 1.3])

        with col_txt:
            # Informações de Endereço
            st.markdown(f"<div class='label-line'>🏠 Cadastro: <span class='value-green'>{res['End_P']}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='label-line'>📍 Conversão Direta: <span class='value-green'>{res['End_H']}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='label-line'>⚒️ Real Auditado: <span class='value-green'>{res.get('Rua_H', 'N/A')}</span></div>", unsafe_allow_html=True)

            # BOX PARECER AZUL
            st.markdown(f"""
            <div class='parecer-box'>
                📄 Parecer: {res['Obs']}
            </div>
            """, unsafe_allow_html=True)

            # Métricas de Distância
            st.markdown(f"""
            <div class='metric-row'>
                📏 Dist. Linear: {res['Dist_B']} | 📸 Dist. Fachada/Antena: {res['Dist_F']}
            </div>
            """, unsafe_allow_html=True)

            # Coordenadas
            st.markdown(f"<div class='label-line'>🎯 Fachada: <span class='value-green'>{res['LatF']}, {res['LonF']}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='label-line'>📡 Antena: <span class='value-green'>{res['LatA']}, {res['LonA']}</span></div>", unsafe_allow_html=True)

            st.write("")
            st.divider()
            
            # Botões Verdes
            b1, b2, b3 = st.columns(3)
            b1.link_button("📄 PDF", res['Url'], use_container_width=True)
            b2.link_button("🌍 Google Maps", f"https://www.google.com/maps/dir/?api=1&origin={res['LatE']},{res['LonE']}&destination={res['LatF']},{res['LonF']}&travelmode=driving", use_container_width=True)
            b3.link_button("🗺️ HERE Maps", f"https://wego.here.com/directions/drive/{res['LatE']},{res['LonE']}/{res['LatF']},{res['LonF']}", use_container_width=True)

        with col_map:
            # Mapa Satélite
            m = folium.Map(location=[res['LatF'], res['LonF']], zoom_start=18, tiles=None)
            folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Satellite').add_to(m)
            
            # --- ROTA AZUL PONTILHADA (PROJETO EAF) ---
            if 'Rota' in res and res['Rota']:
                folium.PolyLine(
                    locations=res['Rota'], 
                    color="#000080",      # Azul vibrante
                    weight=4, 
                    opacity=0.9, 
                    dash_array='2, 5'    # Padrão pontilhado do projeto
                ).add_to(m)
                m.fit_bounds(res['Rota'])
            
            folium.Marker([res['LatE'], res['LonE']], icon=folium.Icon(color='blue', icon='home')).add_to(m)
            folium.Marker([res['LatF'], res['LonF']], icon=folium.Icon(color='red', icon='user')).add_to(m)
            
            st_folium(m, height=520, key=f"m_{res['Ticket']}", use_container_width=True, returned_objects=[])

        st.markdown("</div>", unsafe_allow_html=True)
