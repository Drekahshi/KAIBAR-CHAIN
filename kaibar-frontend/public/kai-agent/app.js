// ═══════════════════════════════════════════════════
//  AGENT KAI — app.js
//  Full multi-agent chat brain with animated routing
// ═══════════════════════════════════════════════════

const API_BASE = 'http://localhost:8000/api';

// ── DOM refs ─────────────────────────────────────
const messagesEl   = document.getElementById('messages');
const userInputEl  = document.getElementById('user-input');
const sendBtnEl    = document.getElementById('send-btn');
const thinkingBar  = document.getElementById('thinking-bar');
const thinkingSteps= document.getElementById('thinking-steps');
const viewLabelEl  = document.getElementById('view-label');
const chatViewEl   = document.getElementById('chat-view');
const dataViewEl   = document.getElementById('data-view');
const dataPanelEl  = document.getElementById('data-panel');

// ── Agent color map ──────────────────────────────
const AGENT_META = {
    'Vault Agent':        { emoji:'🏦', color:'#22C55E', id:'ag-vault'   },
    'Tokenomics Agent':   { emoji:'📊', color:'#FFD700', id:'ag-tokens'  },
    'AMM Agent':          { emoji:'💧', color:'#3B82F6', id:'ag-amm'     },
    'Airdrop Agent':      { emoji:'🎁', color:'#A78BFA', id:'ag-airdrop' },
    'Wallet Agent':       { emoji:'👛', color:'#F97316', id:'ag-wallet'  },
    'Agent KAI':          { emoji:'🤖', color:'#FFD700', id:null         },
};

// ── Thinking steps sequence ──────────────────────
const THINKING_STAGES = [
    { label:'Analyzing intent',         emoji:'🔍' },
    { label:'Waking orchestrator',      emoji:'🌐' },
    { label:'Routing to specialist',    emoji:'⚡' },
    { label:'Agent executing',          emoji:'🤖' },
    { label:'Building response',        emoji:'✍️'  },
];

// ── Textarea auto-resize ─────────────────────────
userInputEl.addEventListener('input', () => {
    userInputEl.style.height = 'auto';
    userInputEl.style.height = userInputEl.scrollHeight + 'px';
    sendBtnEl.disabled = !userInputEl.value.trim();
});

userInputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtnEl.addEventListener('click', () => sendMessage());

document.getElementById('new-chat-btn').addEventListener('click', clearChat);

// ── MAIN SEND ────────────────────────────────────
async function sendMessage(text = null) {
    const msg = text || userInputEl.value.trim();
    if (!msg) return;

    // Clear input
    if (!text) {
        userInputEl.value = '';
        userInputEl.style.height = 'auto';
        sendBtnEl.disabled = true;
    }

    // Clear welcome splash
    const splash = document.getElementById('welcome-splash');
    if (splash) splash.remove();

    appendUserMsg(msg);

    // Show animated thinking bar
    const typingBubble = appendTypingBubble();
    await runThinkingAnimation();

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        hideThinkingBar();
        typingBubble.remove();

        const agentName  = data.agent  || 'Agent KAI';
        const agentEmoji = data.emoji  || '🤖';
        const agentText  = data.text   || data.response || String(data);

        // Flash the correct agent in sidebar
        highlightAgent(agentName, false);

        appendAIMsg(agentText, agentName, agentEmoji);
        if (isVoiceEnabled) {
            speak(agentText);
        }

    } catch (err) {
        console.error(err);
        hideThinkingBar();
        typingBubble.remove();
        const errorMsg = `⚠️ **Backend not reachable.** Make sure you run:\n\`python api.py\`\n\nError: ${err.message}`;
        appendAIMsg(errorMsg, 'Agent KAI', '🤖');
        if (isVoiceEnabled) speak("Backend not reachable. Please check your connection.");
    }
}

// ── VOICE OUTPUT (Speech Synthesis) ──────────────
let isVoiceEnabled = false;
const voiceBtn = document.getElementById('voice-toggle-btn');

function speak(text) {
    if (!window.speechSynthesis) return;
    
    // Stop any current speech
    window.speechSynthesis.cancel();

    // Clean text for better speech (remove markdown)
    const cleanText = text
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/### (.*?)/g, '$1')
        .replace(/`(.*?)`/g, '$1')
        .replace(/✔|✗|⚠️/g, '');

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    // Function to set voice
    const setVoice = () => {
        const voices = window.speechSynthesis.getVoices();
        // Priority: Google English -> Any English -> First available
        const preferredVoice = voices.find(v => v.name.includes('Google') && v.lang.startsWith('en')) 
                            || voices.find(v => v.lang.startsWith('en'))
                            || voices[0];
        if (preferredVoice) utterance.voice = preferredVoice;
        window.speechSynthesis.speak(utterance);
    };

    if (window.speechSynthesis.getVoices().length > 0) {
        setVoice();
    } else {
        window.speechSynthesis.onvoiceschanged = setVoice;
    }
}

voiceBtn.addEventListener('click', () => {
    isVoiceEnabled = !isVoiceEnabled;
    voiceBtn.textContent = isVoiceEnabled ? '🔊' : '🔇';
    voiceBtn.title = isVoiceEnabled ? 'Mute Voice' : 'Unmute Voice';
    if (isVoiceEnabled) {
        speak("Voice output enabled.");
    } else {
        window.speechSynthesis.cancel();
    }
});

// ── THINKING ANIMATION ───────────────────────────
async function runThinkingAnimation() {
    thinkingBar.style.display = 'block';
    thinkingSteps.innerHTML = '';

    const stepEls = THINKING_STAGES.map((stage, i) => {
        const el = document.createElement('div');
        el.className = 'thinking-step pending';

        if (i > 0) {
            const arrow = document.createElement('span');
            arrow.className = 'thinking-arrow';
            arrow.textContent = '→';
            thinkingSteps.appendChild(arrow);
        }

        const dot = document.createElement('span');
        dot.className = 'step-dot';
        el.appendChild(dot);
        el.appendChild(document.createTextNode(' ' + stage.label));
        thinkingSteps.appendChild(el);
        return el;
    });

    // Activate steps sequentially
    for (let i = 0; i < stepEls.length; i++) {
        if (i > 0) stepEls[i - 1].className = 'thinking-step done';
        stepEls[i].className = 'thinking-step active';
        await sleep(420);
    }

    // One more cycle to show all done
    stepEls[stepEls.length - 1].className = 'thinking-step done';
}

function hideThinkingBar() {
    thinkingBar.style.display = 'none';
    thinkingSteps.innerHTML = '';
}

// ── AGENT SIDEBAR HIGHLIGHT ───────────────────────
function highlightAgent(agentName, busy = true) {
    // Reset all
    Object.values(AGENT_META).forEach(m => {
        if (m.id) {
            const el = document.getElementById(m.id);
            if (el) {
                el.classList.remove('active-agent');
                const dot = el.querySelector('.agent-dot');
                if (dot) { dot.classList.remove('busy'); }
            }
        }
    });

    const meta = AGENT_META[agentName];
    if (meta && meta.id) {
        const el = document.getElementById(meta.id);
        if (el) {
            el.classList.add('active-agent');
            const dot = el.querySelector('.agent-dot');
            if (dot && busy) dot.classList.add('busy');
        }
    }

    // Auto-reset after 3 seconds
    setTimeout(() => {
        Object.values(AGENT_META).forEach(m => {
            if (m.id) {
                const el = document.getElementById(m.id);
                if (el) el.classList.remove('active-agent');
            }
        });
    }, 3000);
}

// ── APPEND MESSAGES ──────────────────────────────
function appendUserMsg(text) {
    const div = document.createElement('div');
    div.className = 'msg user';
    div.innerHTML = `
        <div class="msg-avatar">A</div>
        <div class="msg-body">
            <div class="msg-text">${escapeHtml(text)}</div>
        </div>
    `;
    messagesEl.appendChild(div);
    div.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function appendAIMsg(text, agentName, agentEmoji) {
    const div = document.createElement('div');
    div.className = 'msg ai';

    const formatted = formatText(text);

    div.innerHTML = `
        <div class="msg-avatar">${agentEmoji || 'K'}</div>
        <div class="msg-body">
            <div class="msg-badge">${agentEmoji} ${agentName}</div>
            <div class="msg-text">${formatted}</div>
        </div>
    `;
    messagesEl.appendChild(div);
    div.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function appendTypingBubble() {
    const div = document.createElement('div');
    div.className = 'msg ai';
    div.innerHTML = `
        <div class="msg-avatar">⏳</div>
        <div class="msg-body">
            <div class="msg-text" style="padding: 8px 14px;">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;
    messagesEl.appendChild(div);
    div.scrollIntoView({ behavior: 'smooth', block: 'end' });
    return div;
}

// ── TEXT FORMATTER ───────────────────────────────
function formatText(text) {
    return String(text)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/### (.+)/g, '<h3>$1</h3>')
        .replace(/✔/g, '<span style="color:#22C55E">✔</span>')
        .replace(/✗/g, '<span style="color:#EF4444">✗</span>')
        .replace(/⚠️/g, '<span style="color:#F97316">⚠️</span>')
        .replace(/\n/g, '<br>');
}

function escapeHtml(text) {
    return String(text)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;')
        .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── CLEAR CHAT ───────────────────────────────────
function clearChat() {
    messagesEl.innerHTML = `
        <div class="welcome" id="welcome-splash">
            <div class="welcome-orb">🤖</div>
            <h2 class="welcome-title">What can I help with?</h2>
            <p class="welcome-sub">I'll route your request to the right specialist agent automatically.</p>
            <div class="quick-grid">
                <button class="quick-card" onclick="sendMessage('Check vault APYs')">🏦 Vault APYs</button>
                <button class="quick-card" onclick="sendMessage('Show tokenomics summary')">🪙 Tokenomics</button>
                <button class="quick-card" onclick="sendMessage('How are AMM pools performing?')">💧 AMM Pools</button>
                <button class="quick-card" onclick="sendMessage('List all registered wallets')">👛 Wallets</button>
                <button class="quick-card" onclick="sendMessage('Distribute 50 KAI airdrop')">🎁 Airdrop</button>
                <button class="quick-card" onclick="sendMessage('Deposit 500 into KAI Savings Vault')">💰 Deposit</button>
            </div>
        </div>
    `;
}

// ── SIDEBAR NAVIGATION ───────────────────────────
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', async (e) => {
        // If it's a direct href link like the Back button, let it work natively
        if (!item.hasAttribute('data-view')) return;
        
        e.preventDefault();
        const view = item.getAttribute('data-view');

        // If it's the chat view, stay here inside the KAI agent UI
        if (view === 'chat') {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            viewLabelEl.textContent = "Chat";
            chatViewEl.style.display = 'flex';
            dataViewEl.style.display = 'none';
            return;
        }

        // For all other ecosystem views, route back into the main Next.js App
        const ROUTE_MAP = {
            dashboard: '/',
            vaults: '/vaults',
            amm: '/pools',
            tokenomics: '/tokens',
            wallets: '/',
            airdrop: '/airdrop',
            scheduler: '/scheduler'
        };

        if (ROUTE_MAP[view]) {
            window.location.href = ROUTE_MAP[view];
        }
    });
});

// ── DATA VIEWS ───────────────────────────────────
async function loadDataView(view) {
    dataPanelEl.innerHTML = `<p style="color:rgba(255,255,255,0.4); text-align:center; padding-top:40px;">Loading ${view}…</p>`;

    const ENDPOINT_MAP = {
        dashboard: '/dashboard',
        vaults: '/vaults',
        amm: '/amm',
        tokenomics: '/tokenomics',
        wallets: '/wallets',
    };

    const endpoint = ENDPOINT_MAP[view];
    if (!endpoint) {
        dataPanelEl.innerHTML = `<p style="color:rgba(255,255,255,0.4);text-align:center;padding-top:40px;">Use chat to interact with ${view}.</p>`;
        return;
    }

    try {
        const res  = await fetch(API_BASE + endpoint);
        const data = await res.json();
        renderDataView(view, data);
    } catch (err) {
        dataPanelEl.innerHTML = `
            <div class="data-card">
                <h3>⚠️ Cannot connect to backend</h3>
                <p style="color:rgba(255,255,255,0.5);font-size:12px;">Please run: <code>python api.py</code> in the kai_bot directory.</p>
            </div>
        `;
    }
}

function renderDataView(view, data) {
    let html = '';

    if (view === 'dashboard') {
        html = `
            <div class="stat-grid">
                <div class="stat-box"><div class="stat-val">${data.wallets_count}</div><div class="stat-lbl">Wallets</div></div>
                <div class="stat-box"><div class="stat-val">${data.schedules_count}</div><div class="stat-lbl">Scheduled Tx</div></div>
                <div class="stat-box"><div class="stat-val" style="color:#22C55E">${data.status}</div><div class="stat-lbl">Status</div></div>
            </div>
            <div class="data-card">
                <h3>📡 Network Info</h3>
                <p style="font-size:12px;color:rgba(255,255,255,0.6);">Network: <b style="color:#FFD700">${data.network.toUpperCase()}</b></p>
                <p style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:6px;">${data.timestamp}</p>
            </div>
        `;
    } else if (view === 'vaults') {
        const rows = data.map(v => `
            <tr>
                <td>${v.name}</td>
                <td>${v.id}</td>
                <td><span class="badge-apy">${v.apy.toFixed(2)}%</span></td>
                <td>$${Number(v.tvl).toLocaleString()}</td>
                <td>${(v.utilization * 100).toFixed(1)}%</td>
            </tr>
        `).join('');
        html = `
            <div class="data-card">
                <h3>🏦 Vault Overview</h3>
                <table class="data-table">
                    <thead><tr><th>Name</th><th>ID</th><th>APY</th><th>TVL</th><th>Utilization</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    } else if (view === 'amm') {
        const rows = data.map(p => `
            <tr>
                <td>${p.name}</td>
                <td><span class="badge-apy">${p.apy.toFixed(2)}%</span></td>
                <td>$${Number(p.liquidity).toLocaleString()}</td>
                <td>$${Number(p.volume_24h).toLocaleString()}</td>
            </tr>
        `).join('');
        html = `
            <div class="data-card">
                <h3>💧 AMM Pools</h3>
                <table class="data-table">
                    <thead><tr><th>Pool</th><th>APY</th><th>Liquidity</th><th>Vol 24h</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    } else if (view === 'tokenomics') {
        const rows = Object.entries(data).map(([sym, t]) => `
            <tr>
                <td><b>${sym}</b></td>
                <td>${t.name}</td>
                <td>$${t.usd_price}</td>
                <td>${Number(t.total_supply).toLocaleString()}</td>
                <td>${t.category}</td>
            </tr>
        `).join('');
        html = `
            <div class="data-card">
                <h3>🪙 Tokenomics</h3>
                <table class="data-table">
                    <thead><tr><th>Symbol</th><th>Name</th><th>Price</th><th>Supply</th><th>Category</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    } else if (view === 'wallets') {
        if (!data.length) {
            html = `<div class="data-card"><h3>👛 Wallets</h3><p style="color:rgba(255,255,255,0.4);font-size:12px;">No wallets registered. Say "register wallet 0.0.12345" in chat.</p></div>`;
        } else {
            const items = data.map(w => `<div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:12px;font-family:monospace;color:#FFD700">${w}</div>`).join('');
            html = `<div class="data-card"><h3>👛 Registered Wallets (${data.length})</h3>${items}</div>`;
        }
    }

    dataPanelEl.innerHTML = html;
}

// ── VOICE INPUT ──────────────────────────────────
const micBtn = document.getElementById('mic-btn');
let recognition = null;
let isRecording = false;

const SpeechAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechAPI) {
    recognition = new SpeechAPI();
    recognition.continuous = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => { isRecording = true; micBtn.classList.add('recording'); };
    recognition.onend   = () => { isRecording = false; micBtn.classList.remove('recording'); };
    recognition.onerror = () => { isRecording = false; micBtn.classList.remove('recording'); };
    recognition.onresult = (e) => {
        const t = e.results[0][0].transcript;
        userInputEl.value += (userInputEl.value ? ' ' : '') + t;
        userInputEl.dispatchEvent(new Event('input'));
    };
}

micBtn.addEventListener('click', () => {
    if (!recognition) { alert('Speech recognition not supported in this browser.'); return; }
    if (isRecording) { recognition.stop(); } else { try { recognition.start(); } catch(e) {} }
});

// ── HELPER ───────────────────────────────────────
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
