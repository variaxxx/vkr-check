class Config:
    # connection params
    IP = "163.5.212.83"
    PORT = "29465"
    
    # model params
    TEMPERATURE = 0.1
    MODEL_NAME = "google/gemma-3-4b-it"
    EMBEDDINGS_MODEL = "intfloat/multilingual-e5-small"
    
    # rag
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150
    K_RETRIEVALS = 5
        

