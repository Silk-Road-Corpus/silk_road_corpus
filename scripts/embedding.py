import numpy as np
from google import genai
from google.genai.types import EmbedContentConfig

def cosine_distance(v1, v2):
    """Computes the cosine distance between two vectors."""
    return 1 - np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

client = genai.Client()
response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=[
        "五蘊",  # Five aggregates, FGDB headword
        "五種",  # Five aggregates, An Shigao variant
        "五陰",  # Five aggregates, Dharmarakṣa variant
        "梵語",  # Sanskrit, expect a large distance from the five aggregates
        "巴利語" # Pali, expect a large distance from the five aggregates
    ],
    config=EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT",  # Optional
        output_dimensionality=3072,  # Optional
        title="Five aggregates",  # Optional
    ),
)

embeddings = [e.values for e in response.embeddings]

# Example: compute distance between the first two embeddings
dist = cosine_distance(embeddings[0], embeddings[1])
print(f"Cosine distance between '五蘊' and '五種': {dist}")

# Example: compute distance between the first third embeddings
dist = cosine_distance(embeddings[0], embeddings[2])
print(f"Cosine distance between '五蘊' and '五陰': {dist}")

# Example: compute distance between the first and fourth embeddings
dist2 = cosine_distance(embeddings[0], embeddings[3])
print(f"Cosine distance between '五蘊' and '梵語': {dist2}")
