import chromadb
from mcp.server.mcpserver import MCPServer


mcp = MCPServer("DocuMind MCP Server")


client = chromadb.PersistentClient(
    path="../data/chroma_db"
)

collection = client.get_or_create_collection(
    name="documents"
)


@mcp.tool()
def document_statistics(document_id: str) -> dict:
    """
    Get statistics for an uploaded document.

    Returns the total number of chunks and
    total number of characters stored for the document.
    """

    results = collection.get(
        where={"document_id": document_id},
        include=["documents"]
    )

    documents = results.get("documents", [])

    total_chunks = len(documents)

    total_characters = sum(
        len(document)
        for document in documents
    )

    return {
        "document_id": document_id,
        "total_chunks": total_chunks,
        "total_characters": total_characters
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")