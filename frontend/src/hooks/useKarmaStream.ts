'use client';

import { useKarmaStore, isVisibleTool, getPillLabel } from '@/store/karma';

interface StreamOptions {
  apiUrl?: string;
}

export function useKarmaStream(options: StreamOptions = {}) {
  const store = useKarmaStore();
  const apiUrl = options.apiUrl || '/v1/chat';

  async function sendMessage(text: string) {
    const { token, conversationId, pendingFiles, effortLevel, personalPreferences, outputStyle } = useKarmaStore.getState();

    if (!text.trim() && pendingFiles.length === 0) return;

    // Add user message
    const displayText = text || pendingFiles.map((f) => `\ud83d\udcce ${f.name}`).join(', ');
    store.addMessage({
      id: Date.now().toString(36),
      role: 'user',
      content: displayText,
      timestamp: new Date().toISOString(),
    });

    store.setStreaming(true);
    store.setError(null);

    const abortController = new AbortController();
    store.setAbortController(abortController);

    // Add placeholder karma message for streaming into
    const karmaId = Date.now().toString(36) + 'k';
    store.addMessage({
      id: karmaId,
      role: 'karma',
      content: '',
      timestamp: new Date().toISOString(),
    });

    try {
      const res = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: text || 'Describe the attached file.',
          conversation_id: conversationId,
          session_id: conversationId,
          stream: true,
          effort: effortLevel || undefined,
          output_style: outputStyle || undefined,
          user_preferences: personalPreferences || undefined,
          files: pendingFiles.length ? pendingFiles : undefined,
        }),
        signal: abortController.signal,
      });

      store.clearFiles();

      if (res.status === 401) {
        store.setError('Token rejected.');
        store.setStreaming(false);
        return;
      }

      const ct = res.headers.get('content-type') || '';

      // Non-streaming fallback (server returns JSON)
      if (!ct.includes('text/event-stream')) {
        const data = await res.json();
        store.updateLastMessage(
          data.assistant_text || data.response || data.content || data.error || '(no response)'
        );
        store.setStreaming(false);
        store.setStatus({ lastSeen: new Date().toISOString() });
        return;
      }

      // SSE streaming
      const reader = res.body?.getReader();
      if (!reader) {
        store.setError('No response body');
        store.setStreaming(false);
        return;
      }

      const decoder = new TextDecoder();
      let buffer = '';
      const toolMap = new Map<string, string>(); // tool_use_id -> tool_name

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) continue;

          try {
            const evt = JSON.parse(jsonStr);
            handleSSEEvent(evt, toolMap);
          } catch {
            // Skip malformed JSON
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') {
        // User cancelled — OK
      } else {
        store.setError(err instanceof Error ? err.message : 'Stream failed');
      }
    } finally {
      store.setStreaming(false);
      store.setAbortController(null);
      store.setStatus({ lastSeen: new Date().toISOString() });
    }
  }

  function handleSSEEvent(evt: Record<string, unknown>, toolMap: Map<string, string>) {
    const type = evt.type as string;

    if (type === 'queued') {
      store.updateLastMessage(`\u23f3 ${evt.message || 'Queued...'}`);
      return;
    }

    if (type === 'error') {
      store.setError(evt.error as string);
      return;
    }

    if (type === 'assistant') {
      // Full assistant message with content blocks
      const msg = evt.message as Record<string, unknown>;
      const content = msg?.content as Array<Record<string, unknown>>;
      if (!content) return;

      for (const block of content) {
        if (block.type === 'text') {
          store.appendToLastMessage(block.text as string);
        }
        if (block.type === 'tool_use') {
          const toolName = block.name as string;
          const toolId = block.id as string;
          const toolInput = block.input as Record<string, unknown>;
          toolMap.set(toolId, toolName);

          if (isVisibleTool(toolName)) {
            store.addMessage({
              id: toolId,
              role: 'tool-evidence',
              content: '',
              timestamp: new Date().toISOString(),
              toolName,
              toolInput,
              toolOutput: '(running...)',
            });
          }
          store.addToolCall({
            id: toolId,
            name: toolName,
            input: toolInput || {},
            status: 'running',
          });
        }
      }
      return;
    }

    if (type === 'tool_result') {
      const toolId = evt.tool_use_id as string;
      const output = extractToolResultText(evt.content);
      store.updateToolResult(toolId, output);
      return;
    }

    if (type === 'result') {
      // Final result — update cost
      const cost = evt.total_cost_usd as number;
      if (cost) store.addCost(cost);

      // If karma message is still empty (all content was in tool calls), set the result
      const state = useKarmaStore.getState();
      const lastMsg = state.messages[state.messages.length - 1];
      if (lastMsg?.role === 'karma' && !lastMsg.content) {
        store.updateLastMessage(evt.result as string || '');
      }
      return;
    }

    // stream_event (partial messages) — character-level streaming
    if (type === 'stream_event') {
      const innerEvt = evt.event as Record<string, unknown>;
      if (innerEvt?.type === 'content_block_delta') {
        const delta = innerEvt.delta as Record<string, unknown>;
        if (delta?.type === 'text_delta') {
          store.appendToLastMessage(delta.text as string);
        }
      }
    }
  }

  function cancelStream() {
    const { streamAbortController } = useKarmaStore.getState();
    streamAbortController?.abort();
    store.setStreaming(false);

    // Also hit server cancel
    const { token } = useKarmaStore.getState();
    fetch('/v1/cancel', {
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => {});
  }

  return { sendMessage, cancelStream };
}

function extractToolResultText(content: unknown): string {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    return content
      .map((b) => (typeof b === 'string' ? b : b?.type === 'text' ? b.text || '' : ''))
      .filter(Boolean)
      .join('\n');
  }
  return String(content || '');
}
