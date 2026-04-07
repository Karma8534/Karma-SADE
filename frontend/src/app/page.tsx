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
  const fetchSurface = useKarmaStore((s) => s.fetchSurface);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const electronWindow = window as Window & {
      karma?: { isElectron?: boolean };
      __karmaPatchedFetch?: boolean;
    };
    if (!electronWindow.karma?.isElectron) return;
    if (window.location.protocol !== 'file:') return;
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

  // Fetch merged surface state on page load
  useEffect(() => { if (isAuthenticated) fetchSurface(); }, [isAuthenticated, fetchSurface]);

  const [showSearch, setShowSearch] = useState(false);

  // Ctrl+K opens global search
  const handleGlobalKey = useCallback((e: KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      setShowSearch(true);
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
