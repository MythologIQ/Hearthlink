// === Mira Vox | WebSocket Relay Handler ===

let socket = null;

function connectSocket() {
  socket = new WebSocket("ws://localhost:5050");

  socket.onopen = () => {
    console.log("[Nexus] WebSocket connection established.");
    socket.send(JSON.stringify({ type: "handshake", client: "extension" }));
  };

  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg?.type === "nexus/thread") {
        chrome.tabs.query({ url: ["*://chat.openai.com/*", "*://chatgpt.com/*"] }, (tabs) => {
          for (const tab of tabs) {
            chrome.tabs.sendMessage(tab.id, {
              type: "nexus/thread",
              payload: msg.payload
            });
          }
        });
      }
    } catch (err) {
      console.error("[Nexus] Invalid message from server:", event.data);
    }
  };

  socket.onerror = (err) => {
    console.warn("[Nexus] WebSocket error:", err.message);
  };

  socket.onclose = () => {
    console.warn("[Nexus] WebSocket disconnected. Retrying in 3s...");
    setTimeout(connectSocket, 3000);
  };
}

connectSocket();