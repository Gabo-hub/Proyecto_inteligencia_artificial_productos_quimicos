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
const petToggle = document.getElementById("petToggle"); // Interruptor de mascota
// < ! -- Referencias para la mascota interactiva -- >
const aiPet = document.getElementById("ai-pet");
const petBubble = document.getElementById("pet-bubble");
const petImg = document.getElementById("pet-img"); 

// < ! -- Referencias para los Modales -- >
const editModal = document.getElementById("editModal");
const deleteModal = document.getElementById("deleteModal");
const editChatInput = document.getElementById("editChatInput");
const saveEditBtn = document.getElementById("saveEdit");
const cancelEditBtn = document.getElementById("cancelEdit");
const confirmDeleteBtn = document.getElementById("confirmDelete");
const cancelDeleteBtn = document.getElementById("cancelDelete");

// Variables de estado
let chatToEdit = null;
let chatToDelete = null;
let chatCounter = 1;
let isProcessing = false; 

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

// < ! -- Banco de frases bonitas de Quimi -- >
const frasesQuimi = [
    "¡Nuestra química es innegable! ✨",
    "Eres el catalizador de mi felicidad. 🧪",
    "¡Reaccionas increíble ante cualquier reto!",
    "Eres un elemento esencial en este laboratorio. 💎",
    "¡Mantén siempre tu energía de activación alta!",
    "Eres más valioso que el Oro (Au). 🌟",
    "Hagamos un enlace fuerte hoy. 💪",
    "¡Tu curiosidad genera reacciones positivas!",
    "Eres la solución perfecta a mis dudas. 💧",
    "¡Brillas más que el Fósforo blanco! 💡"
];

// Estado global de conversaciones
let conversations = [];
let currentConversation = null;

// < ! -- LÓGICA DE FORMATEO DE TEXTO (NEGRITAS Y CURSIVAS) -- >
function formatearMensaje(texto) {
    if (!texto) return "";
    
    // Procesa el texto en orden de complejidad para evitar conflictos de asteriscos
    return texto
        // Triple asterisco: Negrita + Cursiva (***texto***)
        .replace(/\*\*\*([^*]+)\*\*\*/g, "<b><i>$1</i></b>")
        // Doble asterisco: Negrita (**texto**)
        .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
        // Un asterisco: Cursiva (*texto*)
        .replace(/\*([^*]+)\*/g, "<i>$1</i>");
}

// < ! -- LÓGICA DE LA MASCOTA INTERACTIVA 3D (QUIMI) -- >

function actualizarMascota(estado) {
    if (aiPet.classList.contains("pet-hidden")) return;
    aiPet.classList.remove("active", "thinking", "error-state");
    
    switch(estado) {
        case "pensando":
            petBubble.textContent = "Analizando la mezcla...";
            aiPet.classList.add("active", "thinking");
            break;
        case "error":
            petBubble.textContent = "¡Algo salió mal!";
            aiPet.classList.add("active", "error-state");
            setTimeout(() => aiPet.classList.remove("active", "error-state"), 3000);
            break;
        case "exito":
            petBubble.textContent = "¡Tengo la respuesta!";
            aiPet.classList.add("active");
            petImg.style.transition = "transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
            petImg.style.transform = "translateY(-30px) rotateY(0deg) scale(1.1)";
            
            setTimeout(() => {
                petImg.style.transform = "translateY(0) rotateY(20deg)";
                aiPet.classList.remove("active");
                setTimeout(() => { petImg.style.transition = "transform 0.1s ease-out"; }, 500);
            }, 3000);
            break;
    }
}

aiPet.addEventListener("click", () => {
    if (aiPet.classList.contains("thinking") || aiPet.classList.contains("pet-hidden")) return;
    const fraseAleatoria = frasesQuimi[Math.floor(Math.random() * frasesQuimi.length)];
    petBubble.textContent = fraseAleatoria;
    aiPet.classList.add("active");
    petImg.style.transition = "transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
    petImg.style.transform = "translateY(-40px) scale(1.1) rotate(5deg)";
    setTimeout(() => {
        aiPet.classList.remove("active");
        petImg.style.transform = "translateY(0) rotateY(20deg)";
    }, 3000);
});

document.addEventListener("mousemove", (e) => {
    if (!petImg || aiPet.classList.contains("thinking") || aiPet.classList.contains("pet-hidden")) return;
    const rect = petImg.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const rotateX = (centerY - e.clientY) / 25;
    const rotateY = (e.clientX - centerX) / 25;
    petImg.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
});

petToggle.addEventListener("change", () => {
    if (petToggle.checked) {
        aiPet.classList.remove("pet-hidden");
        aiPet.classList.add("pet-appearing");
        petBubble.textContent = "¡Reportándome al laboratorio! 🧪";
        aiPet.classList.add("active");
        setTimeout(() => aiPet.classList.remove("pet-appearing"), 600);
        setTimeout(() => aiPet.classList.remove("active"), 2500);
        localStorage.setItem("quimicai_pet_visible", "true");
    } else {
        aiPet.classList.add("pet-hidden");
        aiPet.classList.remove("active");
        localStorage.setItem("quimicai_pet_visible", "false");
    }
});

// < ! -- LÓGICA DE MODALES -- >

function openModal(modal) {
    modal.style.display = "flex";
}

function closeModal(modal) {
    modal.style.display = "none";
}

window.addEventListener("click", (e) => {
    if (e.target === editModal) closeModal(editModal);
    if (e.target === deleteModal) closeModal(deleteModal);
});

saveEditBtn.addEventListener("click", () => {
    if (chatToEdit && editChatInput.value.trim() !== "") {
        chatToEdit.title = editChatInput.value.trim();
        saveConversations();
        renderConversations();
        closeModal(editModal);
    }
});

cancelEditBtn.addEventListener("click", () => closeModal(editModal));

confirmDeleteBtn.addEventListener("click", () => {
    if (chatToDelete) {
        const items = document.querySelectorAll('.history-item');
        items.forEach(item => {
            if (item.dataset.id == chatToDelete.id) {
                item.classList.add('removing');
            }
        });

        setTimeout(() => {
            conversations = conversations.filter(c => c.id !== chatToDelete.id);
            if (currentConversation && currentConversation.id === chatToDelete.id) {
                currentConversation = conversations[0] || null;
            }
            saveConversations();
            renderConversations();
            renderMessages(currentConversation ? currentConversation.messages : []);
            closeModal(deleteModal);
            chatToDelete = null;
        }, 400);
    }
});

cancelDeleteBtn.addEventListener("click", () => closeModal(deleteModal));

// < ! -- LÓGICA DEL MENÚ DE CONFIGURACIÓN -- >

settingsBtn.addEventListener("click", (e) => {
    e.stopPropagation(); 
    const isVisible = settingsMenu.style.display === "block";
    settingsMenu.style.display = isVisible ? "none" : "block";
});

document.addEventListener("click", () => {
    settingsMenu.style.display = "none";
});

settingsMenu.addEventListener("click", (e) => e.stopPropagation());

themeToggle.addEventListener("change", () => {
    document.body.classList.add("theme-transitioning");
    setTimeout(() => {
        if (!themeToggle.checked) {
            document.body.classList.add("light-mode");
            localStorage.setItem("quimicai_theme", "light");
        } else {
            document.body.classList.remove("light-mode");
            localStorage.setItem("quimicai_theme", "dark");
        }
        setTimeout(() => document.body.classList.remove("theme-transitioning"), 600);
    }, 100);
});

// < ! -- LÓGICA DE MENSAJES Y BIENVENIDA -- >

function obtenerSaludoAleatorio() {
    const receta = recetasBase[Math.floor(Math.random() * recetasBase.length)];
    return `¿Sabías que para un ${receta.n}, ${receta.d}?`;
}

function actualizarPantallaBienvenida() {
    welcomeData.textContent = obtenerSaludoAleatorio();
}

function renderMessages(messages) {
  chatBox.innerHTML = "";
  if (!messages || messages.length === 0) {
    actualizarPantallaBienvenida();
    chatBox.appendChild(welcomeScreen);
    welcomeScreen.style.display = "flex";
  } else {
    welcomeScreen.style.display = "none";
    messages.forEach((msg, index) => {
      const wrapper = document.createElement("div");
      wrapper.classList.add("msg-wrapper", msg.sender);
      
      const bubble = document.createElement("div");
      bubble.classList.add("msg");
      
      // CAMBIO: Aplicamos innerHTML con la función de formateo de asteriscos
      bubble.innerHTML = formatearMensaje(msg.text);

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

window.copyMsg = (txt) => {
  navigator.clipboard.writeText(txt);
};

window.deleteMsg = (idx) => {
  if (isProcessing) return;
  if (currentConversation) {
    currentConversation.messages.splice(idx, 1);
    saveConversations();
    renderMessages(currentConversation.messages);
  }
};

// < ! -- RENDERIZADO DEL HISTORIAL CORREGIDO (CLIC FLUIDO) -- >

function renderConversations(newChatId = null) {
  historyList.innerHTML = "";
  
  historyList.style.pointerEvents = isProcessing ? "none" : "auto";
  historyList.style.opacity = isProcessing ? "0.7" : "1";
  newChatBtn.style.pointerEvents = isProcessing ? "none" : "auto";
  newChatBtn.style.opacity = isProcessing ? "0.7" : "1";

  conversations.forEach(conv => {
    const li = document.createElement("li");
    li.classList.add("history-item");
    li.dataset.id = conv.id; 
    
    if (conv.id === newChatId) li.classList.add("new-item");
    
    if (currentConversation && conv.id === currentConversation.id) {
        li.style.borderColor = "rgba(168, 85, 247, 0.6)";
        li.style.background = "rgba(168, 85, 247, 0.1)";
    }

    li.innerHTML = `
        <div class="history-info">${conv.title}</div>
        <div class="history-actions">
            <button class="item-action-btn edit" title="Editar">
                <i class="fa-solid fa-pen-to-square"></i>
            </button>
            <button class="item-action-btn del" title="Eliminar">
                <i class="fa-solid fa-trash"></i>
            </button>
        </div>
    `;

    // CORRECCIÓN: Evento en el LI completo para máxima sensibilidad
    li.addEventListener("click", (e) => {
      if (isProcessing) return;
      if (e.target.closest('.item-action-btn')) return;

      currentConversation = conv;
      saveConversations();
      renderConversations();
      renderMessages(conv.messages);
    });

    li.querySelector(".edit").addEventListener("click", (e) => {
        e.stopPropagation();
        if (isProcessing) return;
        chatToEdit = conv;
        editChatInput.value = conv.title;
        openModal(editModal);
    });

    li.querySelector(".del").addEventListener("click", (e) => {
        e.stopPropagation();
        if (isProcessing) return;
        chatToDelete = conv;
        openModal(deleteModal);
    });

    historyList.appendChild(li);
  });
}

newChatBtn.addEventListener("click", () => {
  if (isProcessing) return;
  const newId = Date.now();
  const nuevaConv = {
    id: newId,
    title: `Conversación ${chatCounter++}`,
    messages: [] 
  };
  conversations.unshift(nuevaConv); 
  currentConversation = nuevaConv;
  saveConversations();
  renderConversations(newId); 
  renderMessages(currentConversation.messages);
});

// < ! -- ENVÍO DE MENSAJES CON FORMATO Y BLOQUEO -- >
async function sendMessage() {
  const text = messageInput.value.trim();
  if (text === "" || isProcessing) return;

  isProcessing = true;
  renderConversations(); 

  if (!currentConversation) {
    const newId = Date.now();
    const nuevaConv = { id: newId, title: text.substring(0, 15) + "...", messages: [] };
    conversations.unshift(nuevaConv);
    currentConversation = nuevaConv;
    renderConversations(newId);
  }

  const targetConversation = currentConversation;
  if (targetConversation.messages.length === 0) {
    targetConversation.title = text.substring(0, 15) + "...";
    renderConversations();
  }

  const userMsg = { sender: "user", text };
  targetConversation.messages.push(userMsg);
  renderMessages(targetConversation.messages);

  messageInput.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;
  actualizarMascota("pensando");

  if (statusLabel) {
    statusLabel.textContent = "procesando...";
    statusLabel.style.color = "#a855f7"; 
  }

  const typingWrapper = document.createElement("div");
  typingWrapper.classList.add("msg-wrapper", "bot");
  typingWrapper.innerHTML = `<div class="msg typing"><span></span><span></span><span></span></div>`;
  chatBox.appendChild(typingWrapper);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    await new Promise(resolve => setTimeout(resolve, 2000));
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: text })
    });

    if (typingWrapper) typingWrapper.remove();
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    
    const botMsg = { sender: "bot", text: data.answer || "⚠ No se recibió respuesta" };
    targetConversation.messages.push(botMsg);
    saveConversations();

    actualizarMascota("exito");
    renderMessages(targetConversation.messages);
    
  } catch (error) {
    if (typingWrapper) typingWrapper.remove();
    actualizarMascota("error");
    const errorMsg = { sender: "bot", text: "❌ Error de conexión con el servidor" };
    targetConversation.messages.push(errorMsg);
    renderMessages(targetConversation.messages);
  } finally {
    isProcessing = false;
    renderConversations(); 
    if (statusLabel) {
      statusLabel.textContent = "en línea";
      statusLabel.style.color = "#06b6d4"; 
    }
  }
}

sendBtn.addEventListener("click", sendMessage);
messageInput.addEventListener("keypress", e => {
  if (e.key === "Enter") {
    e.preventDefault();
    sendMessage();
  }
});

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

(function init() {
  const savedTheme = localStorage.getItem("quimicai_theme");
  if (savedTheme === "light") {
      document.body.classList.add("light-mode");
      themeToggle.checked = false;
  }
  const petVisible = localStorage.getItem("quimicai_pet_visible");
  if (petVisible === "false") {
      aiPet.classList.add("pet-hidden");
      petToggle.checked = false;
  } else {
      aiPet.classList.remove("pet-hidden");
      petToggle.checked = true;
  }
  const loaded = loadConversations();
  if (!loaded || conversations.length === 0) {
    const defaultConv = { id: Date.now(), title: "Nueva consulta", messages: [] };
    conversations.push(defaultConv);
    currentConversation = defaultConv;
    saveConversations();
  }
  renderConversations();
  if (currentConversation) {
    renderMessages(currentConversation.messages);
  }
})();
