'use client';

import { useState, useEffect, useCallback } from 'react';
import { useKarmaStore } from '@/store/karma';
import { Gate } from '@/components/Gate';
import { Header } from '@/components/Header';
import { ChatFeed } from '@/components/ChatFeed';
import { MessageInput } from '@/components/MessageInput';
import { RoutingHints } from '@/components/RoutingHints';
import { ContextPanel } from '@/components/ContextPanel';
import { CodePanel } from '@/components/CodePanel';
import { CoworkPanel } from '@/components/CoworkPanel';
import { SelfEditBanner } from '@/components/SelfEditBanner';
import { StatusBar } from '@/components/StatusBar';
import { GlobalSearch } from '@/components/GlobalSearch';

export default function Home() {
  const isAuthenticated = useKarmaStore((s) => s.isAuthenticated);
  const token = useKarmaStore((s) => s.token);
  const bootHydration = useKarmaStore((s) => s.bootHydration);
  const bootSessionId = useKarmaStore((s) => s.bootSessionId);
  const hydrateBootFrame = useKarmaStore((s) => s.hydrateBootFrame);
  const fetchSurface = useKarmaStore((s) => s.fetchSurface);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const electronWindow = window as Window & {
      karma?: { isElectron?: boolean };
      __TAURI__?: unknown;
      __TAURI_INTERNALS__?: unknown;
      __karmaPatchedFetch?: boolean;
    };
    if (window.location.protocol !== 'file:') return;
    const isElectron = !!electronWindow.karma?.isElectron;
    const isTauri = !!electronWindow.__TAURI__ || !!electronWindow.__TAURI_INTERNALS__;
    if (!isElectron && !isTauri) return;
    if (electronWindow.__karmaPatchedFetch) return;

    const baseUrl = 'http://127.0.0.1:7891';
    const originalFetch = window.fetch.bind(window);
    const rewriteUrl = (url: string) => (
      url.startsWith('/v1/') || url === '/health' ? `${baseUrl}${url}` : url
    );

    window.fetch = ((input: RequestInfo | URL, init?: RequestInit) => {
      if (typeof input === 'string') {
        return originalFetch(rewriteUrl(input), init);
      }
      if (input instanceof URL) {
        const next = input.pathname.startsWith('/v1/') || input.pathname === '/health'
          ? new URL(`${baseUrl}${input.pathname}${input.search}`)
          : input;
        return originalFetch(next, init);
      }
      if (input instanceof Request) {
        const source = new URL(input.url, window.location.href);
        if (source.pathname.startsWith('/v1/') || source.pathname === '/health') {
          const nextUrl = `${baseUrl}${source.pathname}${source.search}`;
          return originalFetch(new Request(nextUrl, input), init);
        }
      }
      return originalFetch(input, init);
    }) as typeof window.fetch;

    electronWindow.__karmaPatchedFetch = true;
  }, []);

  // Auto-authenticate if token exists from localStorage
  if (token && !isAuthenticated) {
    useKarmaStore.getState().setToken(token);
  }

  // Canonical boot hydration first, then pull merged surface.
  useEffect(() => {
    if (!isAuthenticated) return;
    let cancelled = false;
    (async () => {
      await hydrateBootFrame();
      if (!cancelled) await fetchSurface();
    })();
    return () => { cancelled = true; };
  }, [isAuthenticated, hydrateBootFrame, fetchSurface]);

  // Phase Ascendance 2: cross-surface parity polling. Every 2s poll
  // /v1/session/{id}; append turns written by other surface (Julian.exe <-> hub.arknexus.net).
  useEffect(() => {
    if (!isAuthenticated) return;
    const syncSessionTurns = useKarmaStore.getState().syncSessionTurns;
    const iv = setInterval(() => { syncSessionTurns(); }, 2000);
    return () => clearInterval(iv);
  }, [isAuthenticated]);

  // Ascendance gate contract: expose canonical hydration/session markers on root DOM.
  useEffect(() => {
    if (typeof document === 'undefined') return;
    const root = document.documentElement;
    root.setAttribute('data-hydration-state', bootHydration || 'idle');
    const sid = (bootSessionId || '').trim();
    if (sid) {
      root.setAttribute('data-session-id', sid);
    } else {
      root.removeAttribute('data-session-id');
    }
  }, [bootHydration, bootSessionId]);

  const [showSearch, setShowSearch] = useState(false);

  // Ctrl+K opens global search
  const handleGlobalKey = useCallback((e: KeyboardEvent) => {
    const openPanel = (panel: string) => {
      window.dispatchEvent(new CustomEvent('karma-open-panel', { detail: { panel } }));
    };
    const sendCommand = (cmd: string) => {
      window.dispatchEvent(new CustomEvent('karma-send-message', { detail: cmd }));
    };
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      setShowSearch(true);
      return;
    }
    // Panel shortcuts (closest parity to cc-haha UX)
    if ((e.ctrlKey || e.metaKey) && e.key === ',') {
      e.preventDefault();
      openPanel('settings');
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'm') {
      e.preventDefault();
      openPanel('memory');
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'a') {
      e.preventDefault();
      openPanel('agents');
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'l') {
      e.preventDefault();
      openPanel('learned');
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'g') {
      e.preventDefault();
      openPanel('git');
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'w') {
      e.preventDefault();
      openPanel('wip');
      return;
    }
    // Numeric panel shortcuts (Ctrl+1..6)
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey) {
      if (e.key === '1') { e.preventDefault(); openPanel('learned'); return; }
      if (e.key === '2') { e.preventDefault(); openPanel('agents'); return; }
      if (e.key === '3') { e.preventDefault(); openPanel('git'); return; }
      if (e.key === '4') { e.preventDefault(); openPanel('memory'); return; }
      if (e.key === '5') { e.preventDefault(); openPanel('wip'); return; }
      if (e.key === '6') { e.preventDefault(); openPanel('settings'); return; }
    }

    // Command shortcuts (fire slash commands directly)
    if (e.key === 'F1') {
      e.preventDefault();
      sendCommand('/help');
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'd') {
      e.preventDefault();
      sendCommand('/doctor');
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 's') {
      e.preventDefault();
      sendCommand('/status');
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'p') {
      e.preventDefault();
      sendCommand('/plugins');
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'i') {
      e.preventDefault();
      sendCommand('/inbox');
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'e') {
      e.preventDefault();
      sendCommand('/evolve');
      return;
    }
  }, []);
  useEffect(() => {
    window.addEventListener('keydown', handleGlobalKey);
    return () => window.removeEventListener('keydown', handleGlobalKey);
  }, [handleGlobalKey]);

  if (!isAuthenticated) return <Gate />;

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <SelfEditBanner />
      <div className="flex flex-1 overflow-hidden min-h-0">
        <div className="flex flex-col flex-1">
          <ChatFeed />
          <RoutingHints />
          <MessageInput />
          <StatusBar />
        </div>
        <CoworkPanel />
        <ContextPanel />
      </div>
      <CodePanel />
      {showSearch && <GlobalSearch onClose={() => setShowSearch(false)} />}
    </div>
  );
}
