import os
from cerebro import CerebroKala

class EscanerProyecto:
    def __init__(self):
        self.cerebro = CerebroKala()
        # Extensiones de archivos que queremos que la IA aprenda
        self.extensiones_validas = ['.py', '.js', '.txt', '.html', '.css', '.json', '.md']

    def indexar_carpeta(self, ruta_raiz="."):
        print(f"🔍 Analizando archivos en: {os.path.abspath(ruta_raiz)}")
        
        documentos = []
        metadatos = []
        ids = []
        contador = 0

        for raiz, dirs, archivos in os.walk(ruta_raiz):
            # Ignorar carpetas pesadas o irrelevantes
            if 'venv' in raiz or '__pycache__' in raiz or '.git' in raiz or 'memoria_kala' in raiz:
                continue

            for archivo in archivos:
                if any(archivo.endswith(ext) for ext in self.extensiones_validas):
                    ruta_completa = os.path.join(raiz, archivo)
                    try:
                        with open(ruta_completa, 'r', encoding='utf-8') as f:
                            contenido = f.read()
                            
                            if contenido.strip():
                                documentos.append(contenido)
                                metadatos.append({"archivo": archivo, "ruta": ruta_completa})
                                ids.append(f"id_{contador}_{archivo}")
                                contador += 1
                                print(f"✅ Leído: {archivo}")
                    except Exception as e:
                        print(f"❌ Error leyendo {archivo}: {e}")

        if documentos:
            print(f"🧠 Guardando {len(documentos)} fragmentos en la memoria...")
            # Llamamos al método correcto del CerebroKala
            self.cerebro.guardar_fragmento(ids, documentos, metadatos)
            print("✨ ¡Indexación completada con éxito!")
        else:
            print("⚠️ No se encontraron archivos válidos para indexar.")