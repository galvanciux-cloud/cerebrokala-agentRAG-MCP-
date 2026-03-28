import os
import sys
import subprocess
from ia_router import RouterIA
from escaner import EscanerProyecto

class CerebroKalaCLI:
    def __init__(self):
        print("🚀 Iniciando CerebroKala v1.0 (Kilo Gateway v1.0 Enabled)")
        self.router = RouterIA()
        self.escaner = EscanerProyecto()
        
        # Configuraciones por defecto (basadas en Kilo Auto Models)
        self.modo_actual = "code"       # plan, general, build, explore, code, ask, debug
        self.nivel_actual = "frontier"  # frontier, balanced, free
        self.ejecutando = True

    def mostrar_panel_control(self):
        os.system('cls' if os.name == 'nt' else 'clear') # Limpiar pantalla pro
        print("\n" + "═"*80)
        print(f" 🧠 CEREBROKALA galvanciux@gmail.com | 🎯 MODO: {self.modo_actual.upper()} | ⚡ NIVEL: {self.nivel_actual.upper()}")
        print("═"*60)
        print(" [Comandos del Sistema]")
        print(" > indexar           : Escanea código del proyecto (RAG)")
        print(" > modo [intent]     : plan, build, code, explore, ask, debug, general")
        print(" > nivel [power]     : frontier, balanced, free")
        print(" > ejecutar [cmd]    : Corre comando y la IA ve el error (Agente)")
        print(" > salir             : Cerrar aplicación")
        print("─" * 60)

    def bucle_principal(self):
        while self.ejecutando:
            self.mostrar_panel_control()
            user_input = input("✨ Tú: ").strip()

            if not user_input:
                continue

            # --- LÓGICA DE COMANDOS ESPECIALES ---
            
            # 1. SALIR
            if user_input.lower() == 'salir':
                self.ejecutando = False
                print("👋 ¡Cerrando CerebroKala. Hasta pronto!")
            
            # 2. INDEXAR PROYECTO (RAG)
            elif user_input.lower() == 'indexar':
                self.escaner.indexar_carpeta()
                input("\nPresiona Enter para continuar...")
            
            # 3. CAMBIAR MODO (x-kilocode-mode Header oficial)
            elif user_input.lower().startswith('modo '):
                # Ejemplo: 'modo debug'
                partes = user_input.split(' ')
                if len(partes) > 1:
                    nuevo_modo = partes[1].lower()
                    modos_validos = ["plan", "build", "code", "explore", "ask", "debug", "general"]
                    if nuevo_modo in modos_validos:
                        self.modo_actual = nuevo_modo
                        print(f"✅ Modo de IA ajustado a: {nuevo_modo}")
                    else:
                        print(f"❌ Modo inválido. Usa: {', '.join(modos_validos)}")
                input("\nPresiona Enter...")

            # 4. CAMBIAR NIVEL (Virtual Models de Kilo)
            elif user_input.lower().startswith('nivel '):
                # Ejemplo: 'nivel free'
                partes = user_input.split(' ')
                if len(partes) > 1:
                    nuevo_nivel = partes[1].lower()
                    niveles_validos = ["frontier", "balanced", "free"]
                    if nuevo_nivel in niveles_validos:
                        self.nivel_actual = nuevo_nivel
                        print(f"✅ Nivel de potencia ajustado a: {nuevo_nivel}")
                    else:
                        print(f"❌ Nivel inválido. Usa: {', '.join(niveles_validos)}")
                input("\nPresiona Enter...")

            # 5. EJECUTAR COMANDO (Agente de Reparación)
            elif user_input.lower().startswith('ejecutar '):
                # Ejemplo: 'ejecutar python src/main.py'
                comando = user_input[9:]
                print(f"🚀 Ejecutando comando del sistema: {comando}...")
                
                # Capturamos stdout y stderr
                resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
                
                if resultado.returncode != 0:
                    print(f"⚠️ Error detectado (Código {resultado.returncode}). Consultando solución...")
                    # Forzamos modo debug para el Gateway
                    prompt_error = f"""He ejecutado el comando '{comando}' y ha fallado.
                    ---
                    ERROR:
                    {resultado.stderr}
                    ---
                    Basándote en mi código, ¿cómo lo arreglo?"""
                    
                    # Llamada a la IA con Streaming
                    self.router.chat_agente_stream(prompt_error, modo="debug", nivel=self.nivel_actual)
                else:
                    print(f"✅ Ejecutado con éxito:\n---\n{resultado.stdout}\n---")
                input("\nPresiona Enter...")

            # --- CONSULTA NORMAL A LA IA (Streaming Enabled) ---
            else:
                # Usamos el método de streaming
                self.router.chat_agente_stream(
                    user_input, 
                    modo=self.modo_actual, 
                    nivel=self.nivel_actual
                )
                input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    app = CerebroKalaCLI()
    app.bucle_principal()