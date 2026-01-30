# Agente Simulador de Clientes Para Probar Bots

Agente simulador de clientes diseñado para **probar y validar bots de atención al cliente**, generando interacciones humanas realistas a partir de parámetros configurables como perfil, estado de ánimo, contexto e intención.

Este proyecto permite evaluar el comportamiento de bots en escenarios controlados, facilitando pruebas funcionales, validación de flujos y análisis de respuestas.

---

## Descripción del Proyecto

El **Agente Simulador de Clientes** actúa como un cliente humano virtual que interactúa con un agente de soporte automatizado.  
A través del uso de **Modelos de Lenguaje (LLM)** y una **base de conocimiento (RAG)**, el sistema simula conversaciones dinámicas y coherentes, permitiendo:

- Probar bots de atención al cliente
- Simular distintos tipos de usuarios (tranquilo, confundido, molesto)
- Evaluar cierres de casos y cumplimiento de políticas
- Validar respuestas bajo condiciones realistas

El sistema cuenta con una **interfaz gráfica interactiva** desarrollada en Streamlit.

---

## Objetivo

Simular conversaciones humanas realistas para **evaluar el desempeño de bots de soporte técnico**, verificando:
- Cumplimiento de políticas
- Manejo del historial de conversación
- Cierre correcto de casos
- Capacidad de adaptación al comportamiento del cliente

---

## Arquitectura General

- **Frontend:** Streamlit
- **Backend lógico:** LangChain
- **LLM soportados:**
  - Groq (Llama 3)
  - Google Gemini
- **RAG (Retrieval-Augmented Generation):**
  - Base de conocimiento cargada desde archivo JSON
- **Gestión de estado:** `st.session_state`

### Flujo simplificado:
1. Configuración del perfil del cliente
2. Selección del proveedor LLM
3. Inicio de simulación
4. Intercambio cliente ↔ soporte
5. Evaluación de cierre de caso

---

## Tecnologías Utilizadas

- **Python 3**
- **Streamlit**
- **LangChain**
- **Groq API (Llama 3)**
- **Google Generative AI (Gemini)**
- **JSON** (Base de conocimiento tipo RAG)

---

## API Keys

Este proyecto utiliza modelos de lenguaje externos como Groq y Google Gemini.  
Para su ejecución es necesario contar con una API Key válida del proveedor seleccionado.

Por motivos de seguridad, las claves no se incluyen en el repositorio.  

---

## Instalación

**Clonar repositorio**

```bash
git clone https://github.com/mariovicunaa/Semillero-IA-Agente-Simulador de-Clientes-Para-Probar-Bots-Grupo-Nexus.git
cd Semillero-IA-Agente-Simulador de-Clientes-Para-Probar-Bots-Grupo-Nexus
```
**Instalar dependencias** 

```bash
pip install -r requirements.txt
```

---

## Ejecución

```bash
streamlit run src/main.py
```

---

## Uso del sistema

- Selecciona el proveedor LLM (Groq o Google)
- Ingresa tu API Key
- Configura el perfil del cliente:
  - Perfil
  - Ánimo
  - Contexto
  - Objetivo
- Inicia la simulación
- Observa la interacción cliente ↔ soporte
- El sistema detecta automáticamente el cierre del caso

---

## Tests

El proyecto no incluye pruebas unitarias automatizadas debido a la naturaleza interactiva del sistema y al uso de modelos de lenguaje externos (LLM).
La validación del correcto funcionamiento se realizó mediante pruebas funcionales y simulaciones manuales, verificando distintos perfiles de cliente, estados de ánimo y flujos de cierre de casos.

---

## Autores
- Luis Antonio Garces Ordóñez  
  GitHub: [@hduais44](https://github.com/hduais44)

- Mario Samuel Vicuña Aspiazu  
  GitHub: [@mariovicunaa](https://github.com/mariovicunaa)

- Jordan Josue Rodríguez Calderón  
  GitHub: [@jordanr06](https://github.com/jordanr06)

---

## Link del video

https://youtu.be/EcOTv8V5On0

---

## Estructura del Proyecto

```text
Semillero-ia-agente-simulador-Grupo-Nexus/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   └── config/
|       └── RAG_soporte.json
├── docs/
│   └── diagramas/
|       ├── casos_uso.svg
|       └── secuencia_flujo.svg
├── tests/
|   └── test_dummy.py
└── .gitignore
