# Travel Planner Agent

Un agente inteligente de planificación de viajes construido con **LangGraph**, **FastAPI** y **LLMs**, que utiliza el protocolo **MCP (Model Context Protocol)** para acceder a herramientas de búsqueda y planificación.

## Características

- **Asistente conversacional**: Interactúa en lenguaje natural para planificar tu viaje
- **Búsqueda de vuelos**: Integración con APIs de búsqueda de vuelos
- **Orquestación inteligente**: Usa LangGraph para coordinar múltiples pasos del proceso de planificación
- **Protocolo MCP**: Acceso a herramientas mediante Model Context Protocol
- **API REST**: Endpoint `/chat` para comunicarse con el agente
- **Sesiones persistentes**: Mantiene el contexto de conversación por sesión (en construcción)
- **Logging estructurado**: Registro detallado de operaciones en formato JSON

## Requisitos

- Python 3.11+
- pip o poetry
- Variables de entorno configuradas (ver sección Configuración)

## Configuración

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# LLM Configuration
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
LLM_API_KEY=your_api_key_here

# MCP Server
MCP_URL=http://localhost:8000/mcp

# APIs externas
SERPAPI_KEY=your_serpapi_key
SERPAPI_URL=https://serpapi.com/search
```

## Uso

### Iniciar el servidor
```bash
python main.py
```

El servidor estará disponible en `http://127.0.0.1:8000`

### Acceder a la documentación interactiva
```
http://127.0.0.1:8000/docs
```

**Respuesta:**
```json
{
  "response": "Te he encontrado varios vuelos a Barcelona...",
  "flights": [...],
  ...
}
```

## Estructura del Proyecto

```
travel_planner_agent/
├── main.py                    # Punto de entrada de la aplicación
├── requirements.txt           # Dependencias del proyecto
├── .env                       # Variables de entorno (no incluidas en git)
│
├── agent/                     # Núcleo del agente
│   ├── entrypoint.py         # Punto de entrada del agente
│   ├── graph.py              # Construcción del grafo de ejecución
│   ├── router.py             # Lógica de enrutamiento
│   ├── registry.py           # Registro de handlers y herramientas
│   ├── state.py              # Estado del agente
│   ├── handlers/             # Manejadores específicos
│   │   └── flights.py        # Handler de búsqueda de vuelos
│   ├── nodes/                # Nodos del flujo de trabajo
│   │   ├── planner.py        # Nodo planificador (LLM)
│   │   ├── tools.py          # Nodo ejecutor de herramientas
│   │   ├── response.py       # Nodo generador de respuesta
│   │   └── update.py         # Nodo actualizador de estado
│   └── runtime/              # Runtime del agente
│       ├── checkpointer.py   # Persistencia de estado
│       ├── graph_runtime.py  # Ejecución del grafo
│       └── mcp_manager.py    # Gestor del protocolo MCP
│
├── api/                      # API REST
│   └── routes.py            # Endpoints de la API
│
├── core/                     # Configuración y utilidades
│   ├── config.py            # Variables de entorno
│   ├── llm.py               # Configuración del LLM
│   ├── logging.py           # Setup de logging
│   └── utils.py             # Funciones de utilidad
│
├── models/                  # Modelos de datos Pydantic
│   ├── chat_models.py       # Modelos de chat
│   └── flight_models.py     # Modelos de vuelos
│
├── prompts/                 # Prompts del LLM
│   └── flight_prompts.py    # Prompts específicos para vuelos
│
└── server/                  # Configuración del servidor
    ├── lifespan.py          # Gestión del ciclo de vida
    ├── mcp_server.py        # Servidor MCP
    └── tools/               # Definiciones de herramientas
        └── flights/
            └── search_flights.py  # Herramienta de búsqueda
```

## Arquitectura

### Flujo del Agente

```
Usuario (Mensaje Natural)
         ↓
    FastAPI /chat
         ↓
   travel_agent (entrypoint)
         ↓
  planner_node (LLM decide si necesita herramientas)
         ↓
   Necesita tools?
    ↙         ↘
   Sí          No
   ↓           ↓
tool_node  response_node
   ↓           ↓
   └─→ update_node
         ↓
    Respuesta final
```

### Componentes Principales

1. **GraphState**: Mantiene el estado del viaje y la conversación
2. **Planner Node**: Invoca el LLM con tools dispuestas
3. **Tool Node**: Ejecuta herramientas MCP (búsquedas, cálculos, etc.)
4. **Update Node**: Actualiza el estado con los resultados
5. **Response Node**: Genera la respuesta conversacional final
6. **MCP Manager**: Gestiona la comunicación con el servidor MCP
7. **Checkpointer**: Persiste el estado entre ejecuciones

## Desarrollo

### Agregar una nueva herramienta

1. Implementar en `server/tools/`
2. Registrar en `agent/registry.py`
3. Agregar handler en `agent/handlers/`
4. Actualizar prompts en `prompts/`

### Agregar un nuevo manejador

1. Crear archivo en `agent/handlers/`
2. Implementar la lógica
3. Registrar el handler
4. Actualizar el router si es necesario

## Logging

Los logs se registran en formato JSON estructurado. Ver `core/logging.py` para más detalles.

---

**Última actualización**: Abril 2026
