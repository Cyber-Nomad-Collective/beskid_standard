// Interop client: Node's built-in WebSocket (undici, RFC 6455) against the Beskid echo server.
const url = "ws://127.0.0.1:18765/interop";
const results = [];
const check = (name, ok) => { results.push([name, ok]); console.log(`${ok ? "PASS" : "FAIL"} ${name}`); };

function open(protocols) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(url, protocols);
    ws.binaryType = "arraybuffer";
    const queue = [];
    const waiters = [];
    ws.onmessage = (e) => { if (waiters.length) waiters.shift()(e.data); else queue.push(e.data); };
    ws.next = () => new Promise((r) => { if (queue.length) r(queue.shift()); else waiters.push(r); });
    ws.closed = new Promise((r) => { ws.onclose = (e) => r(e); });
    ws.onopen = () => resolve(ws);
    ws.onerror = (e) => reject(e);
  });
}

async function openRetry(protocols) {
  const until = Date.now() + 600000;
  for (;;) {
    try { return await open(protocols); } catch (e) {
      if (Date.now() > until) throw e;
      await new Promise((r) => setTimeout(r, 1000));
    }
  }
}

function pattern(n) { const b = new Uint8Array(n); for (let i = 0; i < n; i++) b[i] = (i * 7 + 3) & 255; return b; }
function same(a, b) { a = new Uint8Array(a); if (a.length !== b.length) return false; for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return false; return true; }

const a = await openRetry(["superchat", "chat"]);
check("subprotocol negotiated", a.protocol === "chat");
a.send("zażółć gęślą jaźń");
check("text echo (UTF-8)", (await a.next()) === "zażółć gęślą jaźń");
a.send(pattern(1000));
check("binary echo, 16-bit length", same(await a.next(), pattern(1000)));
a.send(pattern(65536));
check("binary echo, 64-bit length (65536 bytes)", same(await a.next(), pattern(65536)));
a.send("");
check("empty text echo", (await a.next()) === "");
a.close(3001, "done");
const ca = await a.closed;
check("close handshake echoes 3001", ca.code === 3001 && ca.wasClean);

const b = await openRetry([]);
b.send(pattern(70000));
const cb = await b.closed;
check("message over 64 KiB closes with 1009", cb.code === 1009);

const failed = results.filter(([, ok]) => !ok).length;
console.log(`interop: ${results.length - failed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
