from vector_store import collection
import ast
import operator


# ==========================================
# DOCUMENT STATS TOOL
# ==========================================

def get_document_stats(document_id):
    """
    Return basic statistics about one uploaded document.
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


# ==========================================
# CALCULATOR TOOL
# ==========================================

def calculate(expression):
    """
    Safely calculate a basic mathematical expression.
    """

    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos
    }

    def evaluate(node):

        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        elif isinstance(node, ast.Constant):

            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError(
                "Only numbers are allowed."
            )

        elif isinstance(node, ast.BinOp):

            operator_type = type(node.op)

            if operator_type not in allowed_operators:
                raise ValueError(
                    "Unsupported mathematical operation."
                )

            left = evaluate(node.left)
            right = evaluate(node.right)

            return allowed_operators[operator_type](
                left,
                right
            )

        elif isinstance(node, ast.UnaryOp):

            operator_type = type(node.op)

            if operator_type not in allowed_operators:
                raise ValueError(
                    "Unsupported mathematical operation."
                )

            value = evaluate(node.operand)

            return allowed_operators[operator_type](
                value
            )

        else:
            raise ValueError(
                "Invalid mathematical expression."
            )

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )

        result = evaluate(tree)

        return {
            "expression": expression,
            "result": result
        }

    except Exception as error:

        return {
            "expression": expression,
            "error": str(error)
        }


# ==========================================
# DOCUMENT SUMMARY / CONTENT TOOL
# ==========================================

def summarize_document(document_id):
    """
    Retrieve the content of the currently selected document.

    IMPORTANT:
    This function does NOT call Gemini.

    It only retrieves document content from ChromaDB.
    Gemini will use this content to generate the summary.
    """

    results = collection.get(
        where={"document_id": document_id},
        include=["documents"]
    )

    documents = results.get("documents", [])

    if not documents:
        return {
            "error": "No document content found."
        }

    # Combine all document chunks
    full_text = "\n\n".join(documents)

    # Prevent extremely large tool responses
    max_characters = 12000

    if len(full_text) > max_characters:
        full_text = full_text[:max_characters]

    return {
        "document_content": full_text
    }