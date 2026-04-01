'use client';

import { useKarmaStore } from '@/store/karma';
import { Gate } from '@/components/Gate';
import { Header } from '@/components/Header';
import { ChatFeed } from '@/components/ChatFeed';
import { MessageInput } from '@/components/MessageInput';
import { RoutingHints } from '@/components/RoutingHints';
import { ContextPanel } from '@/components/ContextPanel';

export default function Home() {
  const isAuthenticated = useKarmaStore((s) => s.isAuthenticated);
  const token = useKarmaStore((s) => s.token);

  // Auto-authenticate if token exists from localStorage
  if (token && !isAuthenticated) {
    useKarmaStore.getState().setToken(token);
  }

  if (!isAuthenticated) return <Gate />;

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex flex-1 overflow-hidden min-h-0">
        <div className="flex flex-col flex-1">
          <ChatFeed />
          <RoutingHints />
          <MessageInput />
          <div className="text-center text-karma-muted text-[10px] py-1 tracking-[4px]">
            Evolve. Continue.
          </div>
        </div>
        <ContextPanel />
      </div>
    </div>
  );
}
