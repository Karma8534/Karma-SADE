// library_docs.js — URL map for get_library_docs deep-mode tool
// Pure lookup only. Fetch logic lives in executeToolCall (server.js), reusing fetch_url pattern.

export const LIBRARY_URLS = {
  "redis-py":   "https://redis-py.readthedocs.io/en/stable/commands.html",
  "falkordb":   "https://docs.falkordb.com/cypher/",
  "falkordb-py": "https://github.com/FalkorDB/falkordb-py#readme",
  "fastapi":    "https://fastapi.tiangolo.com/reference/",
};

/**
 * Resolve a library name to its documentation URL.
 * @param {string} library - Library name key from LIBRARY_URLS
 * @returns {string|null} URL string, or null if library is unknown/empty
 */
export function resolveLibraryUrl(library) {
  if (!library) return null;
  return LIBRARY_URLS[library] ?? null;
}
