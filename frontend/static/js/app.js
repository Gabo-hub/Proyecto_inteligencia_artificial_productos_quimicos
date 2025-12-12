// Referencias a elementos del DOM
const sendBtn = document.getElementById("sendBtn");
const messageInput = document.getElementById("messageInput");
const chatBox = document.getElementById("chatBox");
const historyList = document.getElementById("historyList");
const newChatBtn = document.getElementById("newChatBtn");

let chatCounter = 1;

// Estado global de conversaciones
let conversations = [];
let currentConversation = null;

// Función para renderizar mensajes en el área principal
function renderMessages(messages) {
  chatBox.innerHTML = "";
  messages.forEach(msg => {
    const bubble = document.createElement("div");
    bubble.classList.add("msg", msg.sender);
    bubble.textContent = msg.text;
    chatBox.appendChild(bubble);
  });
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Función para renderizar historial
function renderConversations() {
  historyList.innerHTML = "";
  conversations.forEach(conv => {
    const li = document.createElement("li");
    li.classList.add("history-item");
    li.textContent = conv.title;

    // Seleccionar conversación
    li.addEventListener("click", () => {
      currentConversation = conv;
      renderMessages(conv.messages);
    });

    // Renombrar conversación (doble clic)
    li.addEventListener("dblclick", () => {
      const nuevoTitulo = prompt("Nuevo nombre de la conversación:", conv.title);
      if (nuevoTitulo) {
        conv.title = nuevoTitulo;
        renderConversations();
      }
    });

    // Eliminar conversación (clic derecho)
    li.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      if (confirm("¿Eliminar esta conversación?")) {
        conversations = conversations.filter(c => c.id !== conv.id);
        if (currentConversation && currentConversation.id === conv.id) {
          currentConversation = conversations[0] || null;
          renderMessages(currentConversation ? currentConversation.messages : []);
        }
        renderConversations();
      }
    });

    historyList.appendChild(li);
  });
}

// Crear nueva conversación
newChatBtn.addEventListener("click", () => {
  const nuevaConv = {
    id: Date.now(),
    title: `Conversación ${chatCounter++}`,
    messages: []
  };
  conversations.push(nuevaConv);
  currentConversation = nuevaConv;
  renderConversations();
  renderMessages([]);
});

// Enviar mensaje
async function sendMessage() {
  const text = messageInput.value.trim();
  if (text === "") return;

  if (!currentConversation) {
    // Si no hay conversación activa, crear una nueva
    const nuevaConv = {
      id: Date.now(),
      title: `Conversación ${chatCounter++}`,
      messages: []
    };
    conversations.push(nuevaConv);
    currentConversation = nuevaConv;
    renderConversations();
  }

  // Crear burbuja del usuario
  const userMsg = { sender: "user", text };
  currentConversation.messages.push(userMsg);
  renderMessages(currentConversation.messages);

  messageInput.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;

  // Burbuja temporal del bot
  const botMsg = { sender: "bot", text: "⏳ Procesando..." };
  currentConversation.messages.push(botMsg);
  renderMessages(currentConversation.messages);

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: text })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    botMsg.text = data.answer || "⚠ No se recibió respuesta";
    renderMessages(currentConversation.messages);

    // Guardar conversaciones en localStorage
    saveConversations();

  } catch (error) {
    console.error("Error:", error);
    botMsg.text = "❌ Error de conexión con el servidor";
    renderMessages(currentConversation.messages);
  }
}

// Eventos de envío
sendBtn.addEventListener("click", sendMessage);
messageInput.addEventListener("keypress", e => {
  if (e.key === "Enter") {
    e.preventDefault(); // evita salto de línea
    sendMessage();
  }
});

// Funciones de persistencia con localStorage
function saveConversations() {
  try {
    localStorage.setItem("quimicai_conversations", JSON.stringify(conversations));
    localStorage.setItem("quimicai_current_id", currentConversation ? currentConversation.id : null);
  } catch (e) {
    console.error("Error guardando conversaciones:", e);
  }
}

function loadConversations() {
  try {
    const saved = localStorage.getItem("quimicai_conversations");
    const currentId = localStorage.getItem("quimicai_current_id");

    if (saved) {
      conversations = JSON.parse(saved);
      if (currentId) {
        currentConversation = conversations.find(c => c.id == currentId) || conversations[0];
      } else {
        currentConversation = conversations[0];
      }
      return true;
    }
  } catch (e) {
    console.error("Error cargando conversaciones:", e);
  }
  return false;
}

// Inicializar con una conversación por defecto o cargar desde localStorage
(function init() {
  const loaded = loadConversations();

  if (!loaded || conversations.length === 0) {
    const defaultConv = {
      id: Date.now(),
      title: "Conversación inicial",
      messages: []
    };
    conversations.push(defaultConv);
    currentConversation = defaultConv;
    saveConversations();
  }

  renderConversations();
  if (currentConversation) {
    renderMessages(currentConversation.messages);
  }
})();