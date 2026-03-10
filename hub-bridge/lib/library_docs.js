// library_docs.js — URL map for get_library_docs deep-mode tool

export const LIBRARY_URLS = {
  ''redis-py'':   ''https://redis-py.readthedocs.io/en/stable/commands.html'',
  ''falkordb'':   ''https://docs.falkordb.com/cypher/'',
  ''falkordb-py'': ''https://github.com/FalkorDB/falkordb-py#readme'',
  ''fastapi'':    ''https://fastapi.tiangolo.com/reference/'',
};

export function resolveLibraryUrl(library) {
  if (\!library) return null;
  return LIBRARY_URLS[library] ?? null;
}
