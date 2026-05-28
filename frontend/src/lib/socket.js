export function createAlertsSocket(onMessage) {
  const configuredBase = import.meta.env.VITE_WS_BASE_URL;
  const fallbackBase = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/v1/ws/alerts`;
  const socketBase = configuredBase
    ? (() => {
        if (configuredBase.startsWith('ws://') || configuredBase.startsWith('wss://')) {
          return configuredBase;
        }

        const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const path = configuredBase.startsWith('/') ? configuredBase : `/${configuredBase}`;
        return `${scheme}://${window.location.host}${path}`;
      })()
    : fallbackBase;
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
