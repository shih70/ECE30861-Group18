# This module implements the HuggingFaceDataset subclass of UrlItem, representing URLs that
# point to datasets hosted on huggingface.co. It validates that the URL matches a dataset
# pattern (typically containing "/datasets/"), extracts the canonical dataset identifier
# (e.g., "org/dataset"), and normalizes the raw URL into a clean form. The resulting object
# exposes the category "DATASET" and a normalized name, allowing datasets to be consistently
# recognized and attached to models later in the pipeline without duplicating parsing logic.
