let socket = null;
let term = null;
let fitAddon = null;

function safeSend(message) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(message);
  }
}

function waitForTerminalElement(callback) {
  const checkInterval = setInterval(() => {
    const el = document.getElementById('terminal');
    if (el) {
      clearInterval(checkInterval);
      el.innerHTML = '';
      callback(el);
    }
  }, 100);
}

function connect() {
  term = new Terminal({
    fontFamily: 'monospace',
    fontSize: 16,
    theme: {
      background: '#1e1e1e',
      foreground: '#cccccc',
      cursor: '#cccccc',
      black: '#1e1e1e',
      red: '#d16969',
      green: '#b5cea8',
      yellow: '#d7ba7d',
      blue: '#569cd6',
      magenta: '#c586c0',
      cyan: '#9cdcfe',
      white: '#d4d4d4',
      brightBlack: '#666666',
      brightRed: '#f44747',
      brightGreen: '#c8e1a8',
      brightYellow: '#ffcb6b',
      brightBlue: '#82aaff',
      brightMagenta: '#d291e4',
      brightCyan: '#9cdcfe',
      brightWhite: '#ffffff'
    }
  });

  fitAddon = new FitAddon.FitAddon();
  term.loadAddon(fitAddon);

  waitForTerminalElement(el => {
    term.open(el);
    fitAddon.fit();

    const observer = new ResizeObserver(() => {
      fitAddon.fit();
      safeSend(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
    });
    observer.observe(el);
  });

  const protocol = (location.protocol === 'https:') ? 'wss' : 'ws';
  const ws_url = `${protocol}://${location.host}/terminal`;
  console.log("Access to web socket:", ws_url);
  socket = new WebSocket(ws_url);
  socket.binaryType = 'arraybuffer';

  let timeoutHandle = null;

  function resetTimeout() {
    if (timeoutHandle) clearTimeout(timeoutHandle);
    timeoutHandle = setTimeout(() => {
      term.write('\r\n*** Session timeout. Closing connection. ***\r\n');
      socket.close();
    }, 300000); // 300000 = 5 minutes
  }

  socket.onopen = () => {
    safeSend(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
    resetTimeout();
  };

  socket.onclose = () => {
    term.write('\r\n*** Disconnected. Reconnecting in 1s... ***\r\n');
    setTimeout(connect, 1000);
  };

  socket.onerror = () => {
    socket.close();
  };

  socket.onmessage = event => {
    const text = new TextDecoder().decode(event.data);
    term.write(text);
  };

  term.onData(data => {
    resetTimeout();
    safeSend(data)
  });

  term.onResize(({ cols, rows }) => {
    safeSend(JSON.stringify({ type: 'resize', cols, rows }));
  });

  window.addEventListener('resize', () => fitAddon.fit());
}

document.addEventListener('DOMContentLoaded', connect);
