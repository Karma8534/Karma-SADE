// Open a URL in the user's default browser.
// In Tauri, `window.open` is often blocked or opens inside the webview, so use the shell plugin when available.

export async function openExternal(url: string): Promise<void> {
  if (typeof window === 'undefined') return;
  let opened = false;

  // Tauri v2
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w: any = window as any;
    const tauri = w.__TAURI__;
    if (tauri?.shell?.open) {
      await tauri.shell.open(url);
      opened = true;
      return;
    }
    // Tauri v2 fallback when plugin API is only exposed through invoke.
    if (tauri?.core?.invoke) {
      await tauri.core.invoke('plugin:shell|open', { path: url });
      opened = true;
      return;
    }
    if (w.__TAURI_INTERNALS__?.invoke) {
      await w.__TAURI_INTERNALS__.invoke('plugin:shell|open', { path: url });
      opened = true;
      return;
    }
  } catch {}

  try {
    const win = window.open(url, '_blank', 'noopener,noreferrer');
    opened = Boolean(win);
  } catch {}

  if (!opened) {
    try {
      const a = document.createElement('a');
      a.href = url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.style.display = 'none';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      opened = true;
    } catch {}
  }

  if (!opened) {
    try {
      // Last-resort fallback: navigate the current webview instead of failing silently.
      window.location.href = url;
      opened = true;
    } catch {}
  }

  if (!opened) {
    throw new Error('failed to open external URL');
  }
}
