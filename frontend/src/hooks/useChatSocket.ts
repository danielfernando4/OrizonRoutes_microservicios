import { useCallback, useEffect, useRef, useState } from 'react';
import api from '../api/axiosConfig';
import { buildChatSocketUrl } from '../api/wsConfig';
import { useAuth } from '../context/AuthContext';

export interface ChatMessage {
  id?: string;
  trip_id: string;
  sender_id: string;
  content: string;
  timestamp: string;
}

export type ChatConnectionStatus = 'connecting' | 'open' | 'closed' | 'error';

const RECONNECT_DELAY_MS = 3000;

/**
 * Maneja la conexión WebSocket con el Chat Service para un trip_id dado:
 * - Carga el historial vía REST (GET /chat/history/{trip_id}) al montar.
 * - Abre el WebSocket y reconecta automáticamente si se cae la conexión.
 * - Expone el estado de conexión para que la UI muestre feedback (Wifi on/off).
 */
export function useChatSocket(tripId: string) {
  const { token } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState<ChatConnectionStatus>('connecting');
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState('');

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const shouldReconnect = useRef(true);

  useEffect(() => {
    let active = true;
    setHistoryLoading(true);
    setHistoryError('');

    api
      .get(`/api/chat/history/${tripId}`)
      .then((response) => {
        if (active) setMessages(response.data.items ?? []);
      })
      .catch((err) => {
        if (active) {
          setHistoryError(
            err.response?.data?.detail || 'No se pudo cargar el historial del chat'
          );
        }
      })
      .finally(() => {
        if (active) setHistoryLoading(false);
      });

    return () => {
      active = false;
    };
  }, [tripId]);

  useEffect(() => {
    if (!token) return;
    shouldReconnect.current = true;

    const connect = () => {
      setStatus('connecting');
      const ws = new WebSocket(buildChatSocketUrl(tripId, token));
      socketRef.current = ws;

      ws.onopen = () => setStatus('open');

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.error) return; // mensaje inválido rechazado por el servidor
          setMessages((prev) => [...prev, data as ChatMessage]);
        } catch {
          // ignorar frames que no sean JSON válido
        }
      };

      ws.onclose = () => {
        setStatus('closed');
        if (shouldReconnect.current) {
          reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY_MS);
        }
      };

      ws.onerror = () => setStatus('error');
    };

    connect();

    return () => {
      shouldReconnect.current = false;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      socketRef.current?.close();
    };
  }, [tripId, token]);

  const sendMessage = useCallback((content: string) => {
    const trimmed = content.trim();
    if (!trimmed || socketRef.current?.readyState !== WebSocket.OPEN) return;
    socketRef.current.send(JSON.stringify({ content: trimmed }));
  }, []);

  return { messages, status, historyLoading, historyError, sendMessage };
}
