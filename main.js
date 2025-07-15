// Simulasi data produk (sama dengan Python code)
const products = {
  laptop: {
    name: "Laptop Gaming ASUS ROG",
    price: 15000000,
    stock: 5,
    description: "Laptop gaming Intel i7, RAM 16GB, VGA GTX 1650",
  },
  smartphone: {
    name: "Samsung Galaxy S24",
    price: 12000000,
    stock: 8,
    description: "Smartphone flagship kamera 108MP, RAM 8GB, Storage 256GB",
  },
  headphone: {
    name: "Sony WH-1000XM5",
    price: 4500000,
    stock: 12,
    description: "Headphone noise cancelling premium battery 30 jam",
  },
  smartwatch: {
    name: "Apple Watch Series 9",
    price: 6000000,
    stock: 3,
    description: "Smartwatch GPS, health monitoring, water resistant",
  },
  tablet: {
    name: "iPad Pro 11 inch",
    price: 13000000,
    stock: 0,
    description: "Tablet professional chip M2, display Liquid Retina",
  },
  mouse: {
    name: "Logitech MX Master 3",
    price: 1200000,
    stock: 15,
    description: "Mouse wireless premium productivity dan gaming",
  },
  keyboard: {
    name: "Mechanical Keyboard RGB",
    price: 800000,
    stock: 7,
    description: "Keyboard mechanical RGB lighting switch blue",
  },
};

const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const typingIndicator = document.getElementById("typingIndicator");

let conversationLog = [];

function addMessage(content, isUser = false) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${isUser ? "user" : "bot"}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = isUser ? "👤" : "🤖";

  const messageContent = document.createElement("div");
  messageContent.className = "message-content";
  messageContent.innerHTML = content;

  if (isUser) {
    messageDiv.appendChild(messageContent);
    messageDiv.appendChild(avatar);
  } else {
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
  }

  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
  typingIndicator.style.display = "flex";
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
  typingIndicator.style.display = "none";
}

function formatPrice(price) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
  }).format(price);
}

function searchProducts(query) {
  const results = [];
  const searchTerm = query.toLowerCase();

  for (const [key, product] of Object.entries(products)) {
    if (
      key.includes(searchTerm) ||
      product.name.toLowerCase().includes(searchTerm) ||
      product.description.toLowerCase().includes(searchTerm)
    ) {
      results.push({ key, ...product });
    }
  }
  return results;
}

function formatProductInfo(products) {
  if (products.length === 0) {
    return "Maaf, produk yang Anda cari tidak tersedia. 😔";
  }

  let html = "Berikut informasi produk yang tersedia:<br><br>";

  products.forEach((product) => {
    const stockStatus =
      product.stock > 0
        ? `<span class="stock-available">✅ Tersedia (${product.stock} unit)</span>`
        : `<span class="stock-unavailable">❌ Stok Habis</span>`;

    html += `
                    <div class="product-card">
                        <div class="product-name">📱 ${product.name}</div>
                        <div class="product-price">💰 ${formatPrice(
                          product.price
                        )}</div>
                        <div class="product-stock">📦 ${stockStatus}</div>
                        <div class="product-description">📝 ${
                          product.description
                        }</div>
                    </div>
                `;
  });

  return html;
}

async function generateResponse(userMessage) {
  try {
    const response = await fetch("http://localhost:5000/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userMessage,
      }),
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error("Error:", error);
    return `Maaf, terjadi kesalahan koneksi. Pastikan backend sudah berjalan di localhost:5000<br><br>
                        Error: ${error.message}<br><br>
                        Silakan coba lagi dalam beberapa saat. 🔄`;
  }
}

async function sendMessage() {
  const message = messageInput.value.trim();
  if (!message) return;

  // Tambahkan pesan user
  addMessage(message, true);
  messageInput.value = "";
  sendButton.disabled = true;

  // Tampilkan indikator mengetik
  showTypingIndicator();

  // Kirim ke backend Python
  try {
    const response = await generateResponse(message);
    hideTypingIndicator();
    addMessage(response);
  } catch (error) {
    hideTypingIndicator();
    addMessage("Maaf, terjadi kesalahan. Silakan coba lagi. 🔄");
  }

  sendButton.disabled = false;
}

function sendQuickMessage(message) {
  messageInput.value = message;
  sendMessage();
}

// Event listeners
sendButton.addEventListener("click", sendMessage);
messageInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});

// Auto-focus input
messageInput.focus();
