def chunk_text(text):
    chunk_size = 500
    overlap = 50
    chunks = []
    start = 0 
    
    while start < len(text):
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)
        start += chunk_size - overlap


    return chunks