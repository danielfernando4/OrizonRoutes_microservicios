import { useEffect, useRef, useState, type FormEvent } from 'react';
import { MessageCircle, Send, Wifi, WifiOff } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useChatSocket } from '../../hooks/useChatSocket';

interface ChatWindowProps {
  /** ID del viaje: define la sala de chat en el Chat Service. */
  tripId: string;
  /** Nombre a mostrar en el encabezado (el Chat Service no conoce nombres). */
  otherPartyName?: string;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

function ChatSkeleton() {
  return (
    <div className="space-y-3 p-4 animate-pulse">
      <div className="h-10 bg-white/40 rounded-2xl w-2/3" />
      <div className="h-10 bg-white/40 rounded-2xl w-1/2 ml-auto" />
      <div className="h-10 bg-white/40 rounded-2xl w-3/5" />
    </div>
  );
}

export default function ChatWindow({ tripId, otherPartyName }: ChatWindowProps) {
  const { user } = useAuth();
  const { messages, status, historyLoading, historyError, sendMessage } =
    useChatSocket(tripId);
  const [draft, setDraft] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!draft.trim()) return;
    sendMessage(draft);
    setDraft('');
  };

  const isConnected = status === 'open';

  return (
    <div className="glass-panel rounded-2xl flex flex-col h-[32rem] overflow-hidden">
      {/* Encabezado */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/40">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-primary" />
          <span className="font-semibold text-foreground">
            {otherPartyName ? `Chat con ${otherPartyName}` : 'Chat del viaje'}
          </span>
        </div>
        {isConnected ? (
          <span className="flex items-center gap-1 text-xs text-green-600 font-medium">
            <Wifi className="w-3.5 h-3.5" />
            En línea
          </span>
        ) : (
          <span className="flex items-center gap-1 text-xs text-foreground/40 font-medium">
            <WifiOff className="w-3.5 h-3.5" />
            {status === 'connecting' ? 'Conectando...' : 'Reconectando...'}
          </span>
        )}
      </div>

      {/* Mensajes */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
        {historyLoading ? (
          <ChatSkeleton />
        ) : historyError ? (
          <p className="text-sm text-red-500 text-center mt-6">{historyError}</p>
        ) : messages.length === 0 ? (
          <p className="text-sm text-foreground/50 text-center mt-6">
            Aún no hay mensajes. Escribe el primero.
          </p>
        ) : (
          messages.map((msg, idx) => {
            const isOwn = msg.sender_id === user?.id;
            return (
              <div
                key={msg.id ?? idx}
                className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm shadow-sm ${
                    isOwn
                      ? 'bg-primary text-white rounded-br-sm'
                      : 'bg-white/80 text-foreground rounded-bl-sm'
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                  <span
                    className={`block text-[10px] mt-1 ${
                      isOwn ? 'text-white/70' : 'text-foreground/40'
                    }`}
                  >
                    {formatTime(msg.timestamp)}
                  </span>
                </div>
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>

      {/* Entrada de texto */}
      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-2 p-3 border-t border-white/40"
      >
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Escribe un mensaje..."
          maxLength={2000}
          disabled={!isConnected}
          className="flex-1 bg-white/60 border border-white/40 rounded-full px-4 py-2 text-sm text-foreground placeholder:text-foreground/40 focus:outline-none focus:ring-2 focus:ring-primary/40 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!isConnected || !draft.trim()}
          className="bg-primary hover:bg-secondary disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-full p-2.5 transition-colors cursor-pointer flex-shrink-0"
          title="Enviar"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
