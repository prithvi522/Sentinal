export function createAlertsSocket(onMessage) {
  const socketBase = import.meta.env.VITE_WS_BASE_URL || `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/v1/ws/alerts`;
  const ws = new WebSocket(socketBase);
  let opened = false;
  let cancelled = false;

  ws.onopen = () => {
    opened = true;
    if (cancelled) {
      ws.close();
      return;
    }
    ws.send('subscribe');
  };

  ws.onerror = () => {};

  ws.onclose = () => {
    opened = false;
  };

  ws.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data));
    } catch {
      onMessage({ channel: 'raw', payload: event.data });
    }
  };

  ws.safeClose = () => {
    cancelled = true;
    if (opened && ws.readyState <= WebSocket.OPEN) {
      ws.close();
    }
  };

  return ws;
}
