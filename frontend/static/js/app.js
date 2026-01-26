// Referencias a elementos del DOM
const sendBtn = document.getElementById("sendBtn");
const messageInput = document.getElementById("messageInput");
const chatBox = document.getElementById("chatBox");
const historyList = document.getElementById("historyList");
const newChatBtn = document.getElementById("newChatBtn");
const statusLabel = document.getElementById("statusLabel");
const settingsBtn = document.getElementById("settingsBtn");
// < ! -- Nuevas referencias para la bienvenida -- >
const welcomeScreen = document.getElementById("welcomeScreen");
const welcomeData = document.getElementById("welcomeData");
// < ! -- Nuevas referencias para el menú y tema -- >
const settingsMenu = document.getElementById("settingsMenu");
const themeToggle = document.getElementById("themeToggle");

let chatCounter = 1;

// < ! -- Banco de datos reales extraídos del backend -- >
const recetasBase = [
    { n: "Limpiador Multiusos", d: "puedes usar 50% Vinagre y 50% Agua. ¡Evita usarlo en mármol!" },
    { n: "Pasta para Horno", d: "el Bicarbonato con un poco de agua elimina la grasa quemada toda la noche." },
    { n: "Limpiavidrios", d: "mezcla Alcohol Isopropílico, Vinagre y Agua para un acabado sin rayas." },
    { n: "Desatascador Ecológico", d: "el Bicarbonato seguido de Vinagre crea una reacción efervescente que limpia tuberías." },
    { n: "Lustramuebles", d: "el Aceite de Oliva con Limón es ideal, pero prepáralo al momento porque el limón se oxida." },
    { n: "Talco para Pies", d: "la Fécula de Maíz y el Bicarbonato son la base perfecta para absorber humedad." },
    { n: "Solución de Ácido Clorhídrico", d: "para una mezcla 0.1M de laboratorio, se usan 8.3 mL de ácido en 1L de agua." },
    { n: "Desinfectante Natural", d: "el Agua Oxigenada y el Vinagre desinfectan genial, pero aplícalos por separado." }
];

// Estado global de conversaciones
let conversations = [];
let currentConversation = null;

// < ! -- LÓGICA DEL MENÚ DE CONFIGURACIÓN -- >

// Abrir/Cerrar menú al dar clic a la tuerca
settingsBtn.addEventListener("click", (e) => {
    e.stopPropagation(); // Evita que el evento cierre el menú inmediatamente
    const isVisible = settingsMenu.style.display === "block";
    settingsMenu.style.display = isVisible ? "none" : "block";
});

// Cerrar menú si se hace clic fuera del área del menú
document.addEventListener("click", () => {
    settingsMenu.style.display = "none";
});

// Evitar que el menú se cierre al hacer clic dentro de él
settingsMenu.addEventListener("click", (e) => e.stopPropagation());

// < ! -- LÓGICA DE CAMBIO DE TEMA (MODO CLARO/OSCURO) -- >
themeToggle.addEventListener("change", () => {
    if (!themeToggle.checked) {
        document.body.classList.add("light-mode");
        localStorage.setItem("quimicai_theme", "light");
    } else {
        document.body.classList.remove("light-mode");
        localStorage.setItem("quimicai_theme", "dark");
    }
});

// < ! -- Función para obtener un saludo aleatorio con dato químico -- >
function obtenerSaludoAleatorio() {
    const receta = recetasBase[Math.floor(Math.random() * recetasBase.length)];
    return `¿Sabías que para un ${receta.n}, ${receta.d}?`;
}

// < ! -- Función para actualizar el texto de la pantalla central -- >
function actualizarPantallaBienvenida() {
    welcomeData.textContent = obtenerSaludoAleatorio();
}

// Función para renderizar mensajes en el área principal
function renderMessages(messages) {
  // Limpiamos todo, pero mantenemos la referencia de la welcomeScreen
  chatBox.innerHTML = "";
  
  if (!messages || messages.length === 0) {
    // Si no hay mensajes, se muestra la pantalla de bienvenida central
    actualizarPantallaBienvenida();
    chatBox.appendChild(welcomeScreen);
    welcomeScreen.style.display = "flex";
  } else {
    // Si hay mensajes, se oculta la pantalla de bienvenida
    welcomeScreen.style.display = "none";
    
    messages.forEach((msg, index) => {
      const wrapper = document.createElement("div");
      wrapper.classList.add("msg-wrapper", msg.sender);

      const bubble = document.createElement("div");
      bubble.classList.add("msg");
      bubble.textContent = msg.text;

      const actions = document.createElement("div");
      actions.classList.add("msg-actions");
      actions.innerHTML = `
        <button class="action-btn" onclick="copyMsg('${msg.text.replace(/'/g, "\\'")}')">Copiar</button>
        <button class="action-btn" onclick="deleteMsg(${index})">Eliminar</button>
      `;

      wrapper.appendChild(bubble);
      wrapper.appendChild(actions);
      chatBox.appendChild(wrapper);
    });
  }
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Funciones globales para acciones de mensajes
window.copyMsg = (txt) => {
  navigator.clipboard.writeText(txt);
};

window.deleteMsg = (idx) => {
  if (currentConversation) {
    currentConversation.messages.splice(idx, 1);
    saveConversations();
    renderMessages(currentConversation.messages);
  }
};

// Función para renderizar historial
function renderConversations() {
  historyList.innerHTML = "";
  conversations.forEach(conv => {
    const li = document.createElement("li");
    li.classList.add("history-item");
    li.textContent = conv.title;

    li.addEventListener("click", () => {
      currentConversation = conv;
      saveConversations();
      renderMessages(conv.messages);
    });

    li.addEventListener("dblclick", () => {
      const nuevoTitulo = prompt("Nuevo nombre de la conversación:", conv.title);
      if (nuevoTitulo) {
        conv.title = nuevoTitulo;
        saveConversations();
        renderConversations();
      }
    });

    li.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      if (confirm("¿Eliminar esta conversación?")) {
        conversations = conversations.filter(c => c.id !== conv.id);
        if (currentConversation && currentConversation.id === conv.id) {
          currentConversation = conversations[0] || null;
        }
        saveConversations();
        renderConversations();
        renderMessages(currentConversation ? currentConversation.messages : []);
      }
    });

    historyList.appendChild(li);
  });
}

// < ! -- Crear nueva conversación vacía para mostrar bienvenida -- >
newChatBtn.addEventListener("click", () => {
  const nuevaConv = {
    id: Date.now(),
    title: `Conversación ${chatCounter++}`,
    messages: [] // VACÍO para que active la welcome screen
  };
  conversations.push(nuevaConv);
  currentConversation = nuevaConv;
  saveConversations();
  renderConversations();
  renderMessages(currentConversation.messages);
});

// Enviar mensaje
async function sendMessage() {
  const text = messageInput.value.trim();
  if (text === "") return;

  if (!currentConversation) {
    const nuevaConv = {
      id: Date.now(),
      title: text.substring(0, 15) + "...",
      messages: []
    };
    conversations.push(nuevaConv);
    currentConversation = nuevaConv;
    renderConversations();
  }

  if (currentConversation.messages.length === 0) {
    currentConversation.title = text.substring(0, 15) + "...";
    renderConversations();
  }

  const userMsg = { sender: "user", text };
  currentConversation.messages.push(userMsg);
  renderMessages(currentConversation.messages);

  messageInput.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;

  if (statusLabel) {
    statusLabel.textContent = "procesando...";
    statusLabel.style.color = "#a855f7"; 
  }

  const typingWrapper = document.createElement("div");
  typingWrapper.classList.add("msg-wrapper", "bot");
  typingWrapper.innerHTML = `
    <div class="msg typing">
      <span></span><span></span><span></span>
    </div>
  `;
  chatBox.appendChild(typingWrapper);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    await new Promise(resolve => setTimeout(resolve, 3000));

    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: text })
    });

    typingWrapper.remove();

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    const botMsg = { sender: "bot", text: data.answer || "⚠ No se recibió respuesta" };
    currentConversation.messages.push(botMsg);
    
    renderMessages(currentConversation.messages);
    saveConversations();

  } catch (error) {
    if(typingWrapper) typingWrapper.remove();
    console.error("Error:", error);
    const errorMsg = { sender: "bot", text: "❌ Error de conexión con el servidor" };
    currentConversation.messages.push(errorMsg);
    renderMessages(currentConversation.messages);
  } finally {
    if (statusLabel) {
      statusLabel.textContent = "en línea";
      statusLabel.style.color = "#06b6d4"; 
    }
  }
}

// Eventos de envío
sendBtn.addEventListener("click", sendMessage);
messageInput.addEventListener("keypress", e => {
  if (e.key === "Enter") {
    e.preventDefault();
    sendMessage();
  }
});

// Funciones de persistencia
function saveConversations() {
  try {
    localStorage.setItem("quimicai_conversations", JSON.stringify(conversations));
    localStorage.setItem("quimicai_current_id", currentConversation ? currentConversation.id : null);
  } catch (e) {
    console.error("Error guardando:", e);
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
    console.error("Error cargando:", e);
  }
  return false;
}

// < ! -- Inicializar aplicación -- >
(function init() {
  // < ! -- Cargar tema guardado -- >
  const savedTheme = localStorage.getItem("quimicai_theme");
  if (savedTheme === "light") {
      document.body.classList.add("light-mode");
      themeToggle.checked = false;
  }

  const loaded = loadConversations();

  if (!loaded || conversations.length === 0) {
    const defaultConv = {
      id: Date.now(),
      title: "Nueva consulta",
      messages: [] // VACÍO para mostrar bienvenida al cargar por primera vez
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
