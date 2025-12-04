

// --- DOM Elements ---
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatContainer = document.getElementById('chat-container').querySelector('.max-w-4xl');
const welcomeMessage = document.getElementById('welcome-message');
const menuBtn = document.getElementById('menu-btn');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const sendButton = document.getElementById('send-button');
const newChatBtn = document.getElementById('new-chat-btn');
const mobileNewChat = document.getElementById('mobile-new-chat');
const conversationList = document.getElementById('conversation-list');

// --- State Management ---
let conversationHistory = [];
let lastConversation = '';

// --- Event Listeners ---
chatForm.addEventListener('submit', handleSendMessage);
chatInput.addEventListener('input', autoResizeTextarea);
chatInput.addEventListener('keydown', handleKeydown);
menuBtn.addEventListener('click', toggleSidebar);
overlay.addEventListener('click', toggleSidebar);
document.getElementById("close-sidebar-btn").addEventListener("click", toggleSidebar);
newChatBtn.addEventListener('click', startNewConversation);
mobileNewChat.addEventListener('click', startNewConversation);

// --- Functions ---
function toggleSidebar() {
  sidebar.classList.toggle('-translate-x-full');
  overlay.classList.toggle('hidden');
}

function startNewConversation() {
  conversationHistory = [];
  chatContainer.innerHTML = '';
  welcomeMessage.style.display = 'block';
  chatInput.value = '';
  autoResizeTextarea();

  if (!sidebar.classList.contains('-translate-x-full')) {
    toggleSidebar();
  }
}

function addConversationToSidebar(text) {
  const conversationItem = document.createElement('a');
  conversationItem.href = '#';
  conversationItem.className = 'px-3 py-2.5 rounded-lg text-sm font-medium hover:bg-white/5 transition-colors duration-200 truncate';
  conversationItem.textContent = text.substring(0, 50) + (text.length > 50 ? '...' : '');
  conversationList.insertBefore(conversationItem, conversationList.firstChild);

  if (conversationList.children.length > 10) {
    conversationList.removeChild(conversationList.lastChild);
  }
}

async function handleSendMessage(e) {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  if (welcomeMessage && welcomeMessage.style.display !== 'none') {
    welcomeMessage.style.display = 'none';
  }

  // update history & UI
  conversationHistory.push({ role: 'user', content: message });
  appendMessage(message, 'user');

  chatInput.value = '';
  autoResizeTextarea();
  chatInput.style.height = 'auto';

  setLoading(true);
  const typingId = showTypingIndicator();

  try {
    const reply = await sendMessageToBackend(message);

    removeTypingIndicator(typingId);

    conversationHistory.push({ role: 'assistant', content: reply });
    appendMessage(reply, 'bot');

    if (conversationHistory.length === 2) {
      addConversationToSidebar(message);
      lastConversation = message;
    }
  } catch (error) {
    removeTypingIndicator(typingId);
    appendMessage('Sorry, there was an error connecting to the server. Please try again.', 'bot');
    console.error('Error:', error);
  } finally {
    setLoading(false);
  }
}

function showTypingIndicator() {
  const typingId = 'typing-' + Date.now();
  const messageWrapper = document.createElement('div');
  messageWrapper.id = typingId;
  messageWrapper.className = 'w-full';

  const messageDiv = document.createElement('div');
  messageDiv.className = 'max-w-4xl mx-auto p-4 md:p-6 flex items-start gap-5';

  const avatarDiv = document.createElement('div');
  avatarDiv.className = 'w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center font-bold text-white bg-teal-600';
  avatarDiv.innerHTML = `<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" /></svg>`;

  const textDiv = document.createElement('div');
  textDiv.className = 'text-gray-400 pt-0.5 typing-indicator';
  textDiv.textContent = 'Thinking...';

  messageDiv.appendChild(avatarDiv);
  messageDiv.appendChild(textDiv);
  messageWrapper.appendChild(messageDiv);
  chatContainer.appendChild(messageWrapper);

  scrollToBottom();

  return typingId;
}

function removeTypingIndicator(typingId) {
  const indicator = document.getElementById(typingId);
  if (indicator) indicator.remove();
}

function appendMessage(text, sender) {
  const isUser = sender === 'user';
  const messageWrapper = document.createElement('div');
  messageWrapper.className = `w-full`;

  const messageDiv = document.createElement('div');
  messageDiv.className = 'max-w-4xl mx-auto p-4 md:p-6 flex items-start gap-5';

  const avatarDiv = document.createElement('div');
  avatarDiv.className = 'w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center font-bold text-white';

  if (isUser) {
    avatarDiv.classList.add('bg-blue-600');
    avatarDiv.textContent = 'U';
  } else {
    avatarDiv.classList.add('bg-teal-600');
    avatarDiv.innerHTML = `<svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" /></svg>`;
  }

  const textDiv = document.createElement('div');
  textDiv.className = 'text-black pt-0.5 leading-relaxed message-text';
  textDiv.textContent = text;

  messageDiv.appendChild(avatarDiv);
  messageDiv.appendChild(textDiv);
  messageWrapper.appendChild(messageDiv);
  chatContainer.appendChild(messageWrapper);

  scrollToBottom();
}

function scrollToBottom() {
  const container = chatContainer.parentElement;
  container.scrollTop = container.scrollHeight;
}

async function sendMessageToBackend(message) {
  if (CONFIG.MOCK_MODE || !CONFIG.API_URL) {
    await new Promise(r => setTimeout(r, 700));
    return "Mock: I hear you. Try a 15-minute focused lesson. (Prov 3:5)";
  }

  try {
    const res = await fetch(CONFIG.API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: message })
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error('Server error: ' + text);
    }

    const data = await res.json();

    // Backend returns { answer: "..." } on success
    if (data.answer) return data.answer;
    if (data.reply) return data.reply;
    if (data.message) return data.message;
    if (data.error) throw new Error(data.error);

    return JSON.stringify(data);
  } catch (err) {
    console.error('Backend error:', err);
    throw err;
  }
}

function setLoading(state) {
  sendButton.disabled = state;
  chatInput.disabled = state;

  if (state) {
    sendButton.classList.add('opacity-50', 'cursor-not-allowed');
  } else {
    sendButton.classList.remove('opacity-50', 'cursor-not-allowed');
  }
}

function autoResizeTextarea() {
  chatInput.style.height = 'auto';
  const maxHeight = 200;
  const newHeight = Math.min(chatInput.scrollHeight, maxHeight);
  chatInput.style.height = newHeight + 'px';
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  chatInput.focus();
});
