import streamlit as st
import os
import time
#from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
#from google.api_core.exceptions import ResourceExhausted
from langchain_groq import ChatGroq                        
import json

# Función para cargar conocimientos
def cargar_conocimiento():
    try:
        with open('knowledge_base.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "No se encontró el archivo de políticas."}

# Cargamos las políticas al iniciar
politicas_empresa = cargar_conocimiento()

def obtener_historial_como_texto():
    texto_historial = ""
    for msg in st.session_state.mensajes:
        rol = "SOPORTE" if msg["role"] == "assistant" else "CLIENTE"
        texto_historial += f"{rol}: {msg['content']}\n"
    return texto_historial

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador Nexus V2", page_icon="🤖", layout="wide")

st.title("🤖 Proyecto Nexus: Simulador de Clientes")
st.markdown("### V2.0 - Versión Estable")

# --- 2. BARRA LATERAL (PARAMETRIZACIÓN) ---
with st.sidebar:
    st.header("⚙️ Configuración del Cliente")
    
    # API KEY
    api_key = st.text_input("Tu Grok API Key:", type="password")
    
    st.markdown("---")
    
    # Parámetros (Usamos formularios para que no se recargue mientras escribes)
    with st.form("config_form"):
        st.write("📝 Define la personalidad:")
        p_perfil = st.text_area("Perfil", "Hombre de 60 años sin conocimiento de tecnologia")
        p_animo = st.selectbox("Estado de Ánimo", ["Tranquilo", "Confundido", "Molesto"])
        p_contexto = st.text_area("Contexto", "Lleva 3 horas sin internet.")
        p_intencion = st.text_area("Intención", "Quiere solución inmediata o cancelar.")
        
        # Botón para aplicar cambios
        aplicar_cambios = st.form_submit_button("💾 Aplicar Cambios y Reiniciar")

        # DICCIONARIO DE ACTUACIÓN (Traducimos la selección a instrucciones para el robot)
    instrucciones_tono = {
          "Tranquilo": "Usa un tono neutral y cooperativo. Responde de forma clara, breve y educada. No uses signos de exclamación.",
  
          "Confundido": "Muestra dudas e inseguridad al responder. Haz preguntas para aclarar la situación, usa expresiones como 'no estoy seguro' o '¿podrías explicarlo mejor?' y evita afirmaciones firmes.",
  
          "Molesto": "Usa un tono directo y cortante. Muestra impaciencia y descontento, utiliza frases breves y puede usar signos de exclamación para expresar molestia."
    }


    # Seleccionamos la instrucción oculta según lo que eligió el usuario
    instruccion_actuacion = instrucciones_tono[p_animo]

    # Si se presiona el botón del formulario, reiniciamos la memoria
    if aplicar_cambios:
        st.session_state.mensajes = []
        st.session_state.turno = 0
        st.session_state.simulacion_activa = True
        st.success("✅ Configuración actualizada y chat reiniciado.")
        st.session_state.mensajes.append({"role": "assistant", "content": "Hola, bienvenido a Soporte Técnico. ¿En qué puedo ayudarte hoy?"})

# --- 3. LÓGICA DE IA ---
if api_key:
    os.environ["GROQ_API_KEY"] = api_key
    
    # Intentamos configurar el modelo
    try:
        # USAMOS EL 2.0 FLASH QUE ES EL QUE TIENE TU CUENTA
        llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            temperature=0.9,
            max_retries=2, # Reintentar si falla una vez
        )
    except Exception as e:
        st.error(f"Error en el modelo: {e}")

    # Definimos los Templates (Guiones)
    prompt_cliente = PromptTemplate(
        input_variables=["perfil", "instruccion_actuacion", "contexto", "intencion", "mensaje_recibido","historial"],
        template="""
        Eres un cliente interactuando con soporte técnico. Sigue estrictamente tu perfil.
        PERFIL: {perfil}
        ESTADO DE ÁNIMO: {instruccion_actuacion}
        CONTEXTO: {contexto}
        OBJETIVO: {intencion}

        HISTORIAL DE LA CONVERSACIÓN (Léelo para no contradecirte):
        {historial}
        
        ÚLTIMO MENSAJE DEL SOPORTE: "{mensaje_recibido}"
        
        INSTRUCCIONES:
        - Tu respuesta debe ser CORTA (máximo 30 palabras).
        - Si el soporte resolvió tu problema, di "GRACIAS" o "ADIOS".
        - Si el soporte te niega una petición (ej. hablar con supervisor) MÁS DE DOS VECES, debes ceder y aceptar una de las otras opciones (ej. la cancelación o el técnico), aunque sea a regañadientes. ¡No te quedes en un bucle!
        
        TU RESPUESTA:
        """
    )
    cadena_cliente = prompt_cliente | llm

    prompt_soporte = PromptTemplate(
        # Agregamos la variable 'knowledge'
        input_variables=["mensaje_cliente", "knowledge", "historial"],
        template="""
        Eres un agente de soporte técnico de la empresa "NexusNet".
        
        TUS POLÍTICAS Y CONOCIMIENTO INTERNO (RAG):
        {knowledge}

        HISTORIAL DE LA CONVERSACIÓN (¡LÉELO ATENTAMENTE!):
        {historial}
        
        EL CLIENTE DIJO: "{mensaje_cliente}"
        
        INSTRUCCIONES:
        1. Responde de forma profesional basándote ESTRICTAMENTE en las políticas de arriba.
        2. Si el cliente pide algo que va contra la política, niégalo amablemente.
        3. Sé corto (máximo 40 palabras).
        4. Si el cliente dice "Adiós", "Chao", "Gracias", "Eso es todo" o se despide -> Responde cordialmente y AGREGA "[CASO CERRADO]".
        """
    )
    cadena_soporte = prompt_soporte | llm

    # --- 4. VISUALIZACIÓN DEL CHAT ---
    with st.container():
        col_titulo, col_btns = st.columns([3, 2])
        
        with col_titulo:
            st.subheader("Panel de Control de Simulación")
            
        with col_btns:
            # Inicializamos estados
            if "caso_activo" not in st.session_state:
                st.session_state.caso_activo = True
            if "simulacion_corriendo" not in st.session_state:
                st.session_state.simulacion_corriendo = False

            # LÓGICA DE BOTONES
            if not st.session_state.caso_activo:
                st.success("✅ CASO FINALIZADO")
                if st.button("🔄 Nuevo Caso", type="primary", use_container_width=True):
                    st.session_state.mensajes = [{"role": "assistant", "content": "Hola, bienvenido a Soporte Técnico. ¿En qué puedo ayudarte hoy?"}]
                    st.session_state.caso_activo = True
                    st.session_state.simulacion_corriendo = False
                    st.rerun()
            
            else:
                # Botones de Play/Stop
                col_play, col_stop = st.columns(2)
                with col_play:
                    if not st.session_state.simulacion_corriendo:
                        if st.button("▶️ Iniciar", type="primary", use_container_width=True):
                            st.session_state.simulacion_corriendo = True
                            st.rerun()
                    else:
                        st.info("🟢 Corriendo...")
                
                with col_stop:
                    if st.session_state.simulacion_corriendo:
                        if st.button("⏹️ Detener", type="secondary", use_container_width=True):
                            st.session_state.simulacion_corriendo = False
                            st.rerun()
    
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [{"role": "assistant", "content": "Hola, bienvenido a Soporte Técnico. ¿En qué puedo ayudarte hoy?"}]

    for msg in st.session_state.mensajes:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="😡"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg["content"])

    # --- 5. BOTÓN DE ACCIÓN (CORREGIDO) ---
    
    if st.session_state.caso_activo and st.session_state.simulacion_corriendo:
        # Verificamos que haya historial
        if not st.session_state.mensajes:
             st.session_state.mensajes = [{"role": "assistant", "content": "Hola."}]

        ultimo_msg_soporte = st.session_state.mensajes[-1]["content"]

        historial_actual = obtener_historial_como_texto()
        
        # --- BLOQUE DE SEGURIDAD (TRY-EXCEPT) ---
        try:
            time.sleep(3)
            with st.spinner('Nexus escribiendo...'):
                # Turno Cliente
                res_cliente = cadena_cliente.invoke({
                    "perfil": p_perfil,
                    "instruccion_actuacion": instruccion_actuacion,
                    "contexto": p_contexto,
                    "intencion": p_intencion,
                    "mensaje_recibido": ultimo_msg_soporte,
                    "historial": historial_actual
                })
                
                # --- PARCHE DE LIMPIEZA (AQUÍ ESTÁ LA MAGIA) ---
                # Si Gemini manda una lista rara con JSON, sacamos solo el texto
                texto_raw = res_cliente.content
                if isinstance(texto_raw, list) and len(texto_raw) > 0:
                    texto_cliente = texto_raw[0].get("text", str(texto_raw))
                else:
                    texto_cliente = str(texto_raw)
                # -----------------------------------------------
                
                st.session_state.mensajes.append({"role": "user", "content": texto_cliente})
                with st.chat_message("user", avatar="😡"):
                    st.write(texto_cliente)
            
            time.sleep(3) # Pausa para no saturar la API

            historial_con_cliente = obtener_historial_como_texto()

            with st.spinner('Soporte respondiendo...'):
                # Turno Soporte
                texto_politicas = json.dumps(politicas_empresa, ensure_ascii=False)
                
                # Le pasamos el conocimiento (RAG)
                res_soporte = cadena_soporte.invoke({
                    "mensaje_cliente": texto_cliente,
                    "knowledge": texto_politicas,  # <--- AQUÍ INYECTAMOS EL JSON
                    "historial": historial_con_cliente
                })
                # --- LIMPIEZA TAMBIÉN PARA EL SOPORTE ---
                texto_raw_sop = res_soporte.content
                if isinstance(texto_raw_sop, list) and len(texto_raw_sop) > 0:
                    texto_soporte = texto_raw_sop[0].get("text", str(texto_raw_sop))
                else:
                    texto_soporte = str(texto_raw_sop)
                # ----------------------------------------
                
                texto_upper = texto_soporte.upper()
                caso_cerrado = False
                if "[CASO CERRADO]" in texto_upper or "CASO CERRADO" in texto_upper:
                    caso_cerrado = True
                
                mensaje_para_mostrar = texto_soporte.replace("[CASO CERRADO]", "").replace("CASO CERRADO", "")
                st.session_state.mensajes.append({"role": "assistant", "content": mensaje_para_mostrar})
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(texto_soporte)

                if caso_cerrado:
                    st.session_state.caso_activo = False
                    st.session_state.simulacion_corriendo = False
            
            # Recargar para actualizar botones
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ Ocurrió un error: {e}")
            st.session_state.simulacion_corriendo = False
            st.info("Si es un error de Rate Limit con Groq, espera un minuto.")

else:
    st.warning("👈 Ingresa tu API Key en la izquierda para comenzar.")
