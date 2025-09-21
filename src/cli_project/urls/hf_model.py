# This module implements the HuggingFaceModel subclass of UrlItem, representing URLs that
# point to models hosted on huggingface.co. It validates that the URL matches a Hugging Face
# model pattern, extracts the canonical model identifier (e.g., "org/model"), and normalizes
# the raw URL to a clean, consistent form (stripping paths like "/tree/main"). The resulting
# object exposes the category "MODEL" and a normalized name, ensuring that all downstream
# components (adapters, metrics, executor) can rely on uniform, validated model references
# without duplicating Hugging Face–specific parsing logic.
