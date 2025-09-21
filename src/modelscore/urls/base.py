# This module defines the abstract URL representation and common utilities for URL handling
# across the project. It introduces UrlItem—a normalized, typed wrapper around a raw input
# URL—with required fields (category, name, url) and shared behaviors (normalize, validate,
# and stable key generation). A small factory/classifier maps raw strings to concrete subclasses
# (HuggingFaceModel, HuggingFaceDataset, CodeRepo) without embedding CLI concerns, ensuring
# that downstream components (adapters, metrics, executor) consume consistent, validated
# objects. Centralizing URL logic here improves modularity, reduces drift in normalization rules,
# and enables focused unit testing of URL parsing and linking behaviors.
