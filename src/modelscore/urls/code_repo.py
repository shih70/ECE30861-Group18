# This module implements the CodeRepo subclass of UrlItem, representing URLs that point to
# source code repositories (e.g., GitHub). It validates that the URL matches a supported code
# host pattern, extracts the canonical repository identifier (e.g., "org/repo"), and normalizes
# the raw URL into a clean form. The resulting object exposes the category "CODE" and a
# normalized name, allowing code repositories to be consistently recognized and linked to
# models later in the pipeline without duplicating host-specific parsing logic.
