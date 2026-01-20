import streamlit as st
import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador Nexus", page_icon="🤖", layout="wide")

st.title("🤖 Proyecto Nexus: Simulador de Clientes")
st.markdown("Genera situaciones realistas para probar la resistencia de tus Bots.")

# --- 2. BARRA LATERAL (PARAMETRIZACIÓN) ---
with st.sidebar:
    st.header("⚙️ Configuración del Cliente")
    st.info("Define aquí la personalidad de tu Agente")
    
    # Tu API KEY (Para que no se vea en el código principal si compartes pantalla)
    api_key = st.text_input("Tu Google API Key:", type="password")
    
    st.markdown("---")
    
    # Parámetros del Proyecto
    p_perfil = st.text_area("Perfil Demográfico", "Hombre de 40 años, impaciente y sarcástico")
    p_animo = st.selectbox("Estado de Ánimo", ["Normal", "Confundido", "Enojado", "Furioso (Nivel Dios)"])
    p_contexto = st.text_input("Contexto", "Lleva 3 horas sin internet.")
    p_intencion = st.text_input("Intención/Objetivo", "Quiere solución inmediata o cancelar.")
    
    # Botón de reinicio
    if st.button("🔄 Iniciar Nueva Simulación", type="primary"):
        st.session_state.mensajes = []
        st.session_state.turno = 0
        st.session_state.simulacion_activa = True
        # Mensaje inicial del Bot de Soporte
        st.session_state.mensajes.append({"role": "assistant", "content": "Hola, bienvenido a Soporte Técnico. ¿En qué puedo ayudarte hoy?"})
        st.rerun()

# --- 3. LÓGICA DE IA (SOLO SI HAY API KEY) ---
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    
    # Configuración del Modelo (Usamos el que te funcionó: 2.5 o 2.0)
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", # <--- CAMBIA A "gemini-2.0-flash" SI TE DA ERROR DE LÍMITE
            temperature=0.9,
        )
    except Exception as e:
        st.error(f"Error configurando modelo: {e}")

    # --- TEMPLATES (CEREBROS) ---
    prompt_cliente = PromptTemplate(
        input_variables=["perfil", "animo", "contexto", "intencion", "mensaje_recibido"],
        template="""
        Eres un cliente interactuando con soporte técnico.
        PERFIL: {perfil}
        ESTADO DE ÁNIMO: {animo}
        CONTEXTO: {contexto}
        OBJETIVO: {intencion}
        
        ÚLTIMO MENSAJE DEL SOPORTE: "{mensaje_recibido}"
        
        INSTRUCCIONES:
        - Responde corto (máximo 2 frases).
        - Actúa tu rol dramáticamente.
        - Si te resuelven el problema, di "GRACIAS".
        
        TU RESPUESTA:
        """
    )
    cadena_cliente = prompt_cliente | llm

    prompt_soporte = PromptTemplate(
        input_variables=["mensaje_cliente"],
        template="""
        Eres un soporte técnico amable y corporativo.
        EL CLIENTE DIJO: "{mensaje_cliente}"
        Responde corto e intenta calmarlo.
        """
    )
    cadena_soporte = prompt_soporte | llm

    # --- 4. INTERFAZ DE CHAT (VISUALIZACIÓN) ---
    
    # Inicializar historial si no existe
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [{"role": "assistant", "content": "Hola, bienvenido a Soporte Técnico. ¿En qué puedo ayudarte hoy?"}]

    # Dibujar los mensajes antiguos
    for msg in st.session_state.mensajes:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="😡"): # Avatar de cliente enojado
                st.write(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"): # Avatar de robot
                st.write(msg["content"])

    # --- 5. BOTÓN DE ACCIÓN (EL MOTOR) ---
    if st.session_state.get("simulacion_activa", False):
        if st.button("▶️ Generar Siguiente Turno"):
            
            # 1. Obtenemos lo último que dijo el soporte
            ultimo_msg_soporte = st.session_state.mensajes[-1]["content"]
            
            with st.spinner('El Cliente Nexus está escribiendo...'):
                # 2. Generamos respuesta del Cliente
                res_cliente = cadena_cliente.invoke({
                    "perfil": p_perfil,
                    "animo": p_animo,
                    "contexto": p_contexto,
                    "intencion": p_intencion,
                    "mensaje_recibido": ultimo_msg_soporte
                })
                texto_cliente = res_cliente.content
                
                # Guardar y mostrar
                st.session_state.mensajes.append({"role": "user", "content": texto_cliente})
                with st.chat_message("user", avatar="😡"):
                    st.write(texto_cliente)
            
            # Pausa dramática pequeña
            time.sleep(0.5)

            # 3. Generamos respuesta del Soporte (Automático)
            with st.spinner('El Bot de Soporte está pensando...'):
                res_soporte = cadena_soporte.invoke({"mensaje_cliente": texto_cliente})
                texto_soporte = res_soporte.content
                
                # Guardar y mostrar
                st.session_state.mensajes.append({"role": "assistant", "content": texto_soporte})
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(texto_soporte)
            
            # Forzar actualización para que el botón esté listo de nuevo
            st.rerun()

else:
    st.warning("👈 Por favor, ingresa tu API Key en la barra lateral para comenzar.")
