import streamlit as st
import serial
import pandas as pd
import serial.tools.list_ports
import time

# Configuração da página
st.set_page_config(page_title="Monitor Serial", layout="wide")
col1, col2 = st.columns([1, 4])
with col1:
    st.image("baja.webp", width=100)
with col2:
    st.title("📡 Monitoramento dos dados via LoRa CABIPAJA")

# Cabeçalhos esperados
colunas = [
    "⛽Nivel de combustivel",
    "💨Velocidade",
    "🌡️Temperatura motor",
    "🌡️Temperatura CVT",
    "🛰️Odometro",
    "🪫Bateria",
    "🚨Farol",
    "🛰️Sinal LoRa"
]

# Inicializa estados
if "serial_conexao" not in st.session_state:
    st.session_state.serial_conexao = None
if "dados_recebidos" not in st.session_state:
    st.session_state.dados_recebidos = []

# Entrada da porta
porta_usuario = st.text_input("Informe a porta serial (ex: COM3, COM5):", value="COM7")
if st.button("Conectar"):
    try:
        ser = serial.Serial(porta_usuario, 9600, timeout=1)
        st.session_state.serial_conexao = ser
        st.success(f"Conectado à {porta_usuario}")
    except Exception as e:
        st.error(f"Erro ao conectar: {e}")

# Leitura automática após conexão
if st.session_state.serial_conexao:
    ser = st.session_state.serial_conexao
    buffer = ""
    tabela_area = st.empty()

    # Loop de leitura contínua (limitado a 100 ciclos para evitar travamento)
    for _ in range(100):
        if ser.in_waiting > 0:
            dados = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            buffer += dados

            while '\r\n' in buffer:
                linha_completa, buffer = buffer.split('\r\n', 1)
                partes = linha_completa.strip().split(',')

                if len(partes) == 8:
                    try:
                        valores = [float(p.strip()) for p in partes]
                        st.session_state.dados_recebidos.append(valores)
                    except ValueError:
                        st.warning("Erro ao converter dados.")

        df = pd.DataFrame(st.session_state.dados_recebidos, columns=colunas)
        tabela_area.dataframe(df.tail(10), use_container_width=True)
        time.sleep(1)
