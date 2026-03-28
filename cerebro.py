import chromadb
from chromadb.utils import embedding_functions

class CerebroKala:
    def __init__(self):
        # Iniciamos base de datos local
        self.cliente = chromadb.PersistentClient(path="./memoria_kala")
        
        # Usamos Sentence Transformers para "entender" el código
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Obtenemos o creamos la colección
        self.coleccion = self.cliente.get_or_create_collection(
            name="codigo_proyecto", 
            embedding_function=self.emb_fn
        )

    def guardar_fragmento(self, ids, documentos, metadatos):
        """Guarda código en la base de datos vectorial"""
        try:
            # EL ERROR ESTABA AQUÍ: Se debe usar 'metadatas' en lugar de 'metadatos'
            self.coleccion.add(
                ids=ids,
                documents=documentos,
                metadatas=metadatos  # <--- CORREGIDO
            )
            print(f"✅ {len(documentos)} fragmentos guardados correctamente.")
        except Exception as e:
            print(f"❌ Error al guardar en ChromaDB: {e}")

    def consultar_todo(self, query_text):
        """Busca el código más relevante para una pregunta"""
        try:
            resultados = self.coleccion.query(
                query_texts=[query_text],
                n_results=5
            )
            
            if resultados['documents'] and len(resultados['documents'][0]) > 0:
                contexto = "\n---\n".join(resultados['documents'][0])
                return contexto
            return ""
        except Exception as e:
            print(f"⚠️ Error en consulta RAG: {e}")
            return ""