const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost/api';

/**
 * El Chat Service expone su WebSocket en el mismo host que el API Gateway
 * (nginx enruta /ws/chat/ igual que /api/chat/), pero con protocolo ws/wss
 * en vez de http/https y sin el prefijo /api.
 */
function getGatewayOrigin(): string {
  return API_BASE.replace(/\/api\/?$/, '');
}

export function buildChatSocketUrl(tripId: string, token: string): string {
  const origin = getGatewayOrigin();
  const wsOrigin = origin.replace(/^http/, 'ws');
  return `${wsOrigin}/ws/chat/${encodeURIComponent(tripId)}/${encodeURIComponent(token)}`;
}
