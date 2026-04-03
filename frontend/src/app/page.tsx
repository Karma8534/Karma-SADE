'use client';

import { useState, useEffect, useCallback } from 'react';
import { useKarmaStore } from '@/store/karma';
import { Gate } from '@/components/Gate';
import { Header } from '@/components/Header';
import { ChatFeed } from '@/components/ChatFeed';
import { MessageInput } from '@/components/MessageInput';
import { RoutingHints } from '@/components/RoutingHints';
import { ContextPanel } from '@/components/ContextPanel';
import { SelfEditBanner } from '@/components/SelfEditBanner';
import { StatusBar } from '@/components/StatusBar';
import { GlobalSearch } from '@/components/GlobalSearch';

export default function Home() {
  const isAuthenticated = useKarmaStore((s) => s.isAuthenticated);
  const token = useKarmaStore((s) => s.token);
  const fetchSurface = useKarmaStore((s) => s.fetchSurface);

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
        <ContextPanel />
      </div>
      {showSearch && <GlobalSearch onClose={() => setShowSearch(false)} />}
    </div>
  );
}
