import os
import sys
import json
from openai import OpenAI
from cerebro import CerebroKala # Importamos tu memoria RAG

class RouterIA:
    def __init__(self):
        # Conexión a la base de datos de memoria local (Cromadb)
        self.cerebro = CerebroKala()
        
        # Configuración oficial del Kilo AI Gateway (v1.0 - 2026)
        # Según doc: GET https://api.kilo.ai/api/gateway/models
        self.client_kilo = OpenAI(
            base_url="https://api.kilo.ai/api/gateway", 
            api_key="TU_KILO_API_KEY_AQUI" # Reemplaza esto
        )

        # Definición de "Auto Models" y Modelos Populares (basado en tu doc)
        self.modelos = {
            # Virtual Models (Auto-Ruteo por modo)
            "frontier": "kilo-auto/frontier",   # Optimiza cost/perf con modelos de pago
            "balanced": "kilo-auto/balanced",   # Más económico, rutea a Kimi/MiniMax
            "free": "kilo-auto/free",           # Mejor modelo gratuito disponible
            
            # Modelos específicos (IDs directos)
            "claude-opus": "anthropic/claude-opus-4.6",
            "gpt-5": "openai/gpt-5.2",
            "gemini-pro": "google/gemini-3-pro-preview", # 1M context
            "grok-code": "x-ai/grok-code-fast-1",
            
            # Modelos gratuitos (Anonymous access OK)
            "glm": "z-ai/glm-5:free",
            "minimax": "minimax/minimax-m2.5:free"
        }

    def get_herramientas_disponibles(self):
        """Define las funciones que la IA puede ejecutar en tu PC"""
        return [{
            "type": "function",
            "function": {
                "name": "leer_archivo_proyecto",
                "description": "Lee el contenido real de un archivo del proyecto para obtener contexto exacto.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ruta_relativa": {
                            "type": "string",
                            "description": "Ruta del archivo (ej: 'src/main.py')"
                        }
                    },
                    "required": ["ruta_relativa"]
                }
            }
        }]

    def chat_agente_stream(self, mensaje, modo="code", nivel="frontier"):
        """
        Implementa Chat Completions con Streaming y Tool Calling.
        Usa los headers oficiales: x-kilocode-mode
        """
        # 1. Recuperar contexto RAG de CerebroKala
        contexto_rag = self.cerebro.consultar_todo(mensaje)
        
        # 2. Seleccionar el modelo virtual o directo
        modelo_final = self.modelos.get(nivel, self.modelos["free"])

        # 3. Preparar mensajes con System Prompt estructurado
        messages = [
            {
                "role": "system", 
                "content": f"""Eres CerebroKala, un agente de desarrollo experto.
                Usa el siguiente contexto recuperado de los archivos del proyecto para responder:
                ---
                {contexto_rag}
                ---
                Si el contexto no es suficiente, usa la herramienta 'leer_archivo_proyecto'."""
            },
            {"role": "user", "content": mensaje}
        ]

        try:
            print(f"📡 Kilo Gateway ({nivel.upper()} - Modo: {modo}) > {modelo_final}")
            
            # 4. Llamada con Streaming (stream: true en el JSON de la doc)
            response = self.client_kilo.chat.completions.create(
                model=modelo_final,
                messages=messages,
                stream=True, # Habilitar SSE streaming
                tools=self.get_herramientas_disponibles(), # Habilitar Tool Calling
                tool_choice="auto",
                # Headers oficiales de Kilo Code
                extra_headers={
                    "x-kilocode-mode": modo, # plan, general, build, explore, code, ask, debug
                    "HTTP-Referer": "http://localhost:3000" # Para rankings
                },
                temperature=0.3 # Bajo para código preciso
            )
            
            # 5. Manejo del Stream (SSE Events en tiempo real)
            print(f"\n🤖 {modo.upper()}: ", end="", flush=True)
            full_response = ""
            current_tool_call = None

            for chunk in response:
                delta = chunk.choices[0].delta
                
                # A. Recibir texto normal
                if delta.content:
                    print(delta.content, end="", flush=True)
                    full_response += delta.content
                
                # B. Detectar Tool Call (según doc Message types)
                elif delta.tool_calls:
                    # Kilo unifica tool calls, tomamos el primero
                    if not current_tool_call:
                        current_tool_call = delta.tool_calls[0]
                    else:
                        # Acumulamos argumentos si vienen en trozos
                        current_tool_call.function.arguments += delta.tool_calls[0].function.arguments

            print("\n")

            # 6. Procesar Tool Call si existe (Agente Real)
            if current_tool_call:
                print(f"🔧 Ejecutando herramienta: {current_tool_call.function.name}...")
                return self.ejecutar_herramienta(current_tool_call)

            return full_response

        except Exception as e:
            # Manejo de errores basado en la tabla de Error Codes de tu doc
            error_str = str(e)
            if "401" in error_str: return "❌ Error 401: API Key de Kilo inválida o ausente."
            if "402" in error_str: return "❌ Error 402: Saldo insuficiente en Kilo AI. Añade créditos."
            if "429" in error_str: return "❌ Error 429: Rate limited. Demasiadas peticiones (Anonymous > 200/h)."
            return f"❌ Error técnico: {error_str}"

    def ejecutar_herramienta(self, tool_call):
        """Lógica para ejecutar funciones reales en el disco"""
        nombre_funcion = tool_call.function.name
        
        try:
            argumentos = json.loads(tool_call.function.arguments)
            
            if nombre_funcion == "leer_archivo_proyecto":
                ruta = argumentos.get("ruta_relativa")
                print(f"📖 Leyendo archivo físico: {ruta}...")
                
                if os.path.exists(ruta):
                    with open(ruta, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    return f"✅ Contenido de {ruta}:\n---\n{contenido}\n---"
                else:
                    return f"❌ El archivo {ruta} no existe en el proyecto."
            
            return "❌ Herramienta no implementada."
            
        except json.JSONDecodeError:
            return "❌ Error al decodificar argumentos de la herramienta."
        except Exception as e:
            return f"❌ Error ejecutando herramienta: {str(e)}"