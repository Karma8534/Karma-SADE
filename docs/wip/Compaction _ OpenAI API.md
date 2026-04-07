# Compaction _ OpenAI API

*Converted from: Compaction _ OpenAI API.PDF*


Copy Page
Compaction
Manage long-running conversations with server-side and standalone
compaction.
Overview
To support long-running interactions, you can use compaction to reduce context size while
preserving state needed for subsequent turns.
Compaction helps you balance quality, cost, and latency as conversations grow.
Server-side compaction
You can enable server-side compaction in a Responses create request ( POST
/responses or client.responses.create ) by setting context_management with
compact_threshold .
When the rendered token count crosses the configured threshold, the server runs
server-side compaction.
No separate /responses/compact call is required in this mode.
The response stream includes the encrypted compaction item.
ZDR note: server-side compaction is ZDR-friendly when you set store=false on
your Responses create requests.
The returned compaction item carries forward key prior state and reasoning into the next
run using fewer tokens. It is opaque and not intended to be human-interpretable.
For stateless input-array chaining, append output items as usual. If you are using
previous_response_id , pass only the new user message each turn. In both cases, the
compaction item carries context needed for the next window.
Latency tip: After appending output items to the previous input items, you can drop items