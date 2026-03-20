# 🦙 Connecting KAI Bot to Ollama (Local LLM)

Ollama lets you run LLMs like **Llama 3, Mistral, Gemma, or Phi-3** entirely on your own machine — no API key needed.

---

## Step 1 — Install Ollama

Download and install from **[ollama.com/download](https://ollama.com/download)**  
(Available for Windows, macOS, Linux)

After installing, Ollama runs a local server at `http://localhost:11434`

---

## Step 2 — Pull a Model

Open a terminal and run one of these:

```bash
# 🔥 Recommended (fast & smart, ~4GB)
ollama pull llama3.2

# Lighter option (~2GB)
ollama pull phi3

# More powerful (~7GB)
ollama pull mistral

# Google's model
ollama pull gemma2
```

Verify it works:
```bash
ollama run llama3.2
# Type anything, Ctrl+D to exit
```

---

## Step 3 — Configure KAI Bot

Edit your `.env` file in `kai_bot/`:

```env
# Set this to "ollama" to enable local LLM
AI_PROVIDER=ollama

# Choose the model you pulled (e.g. llama3.2, phi3, mistral, gemma2)
OLLAMA_MODEL=llama3.2

# Ollama server URL (default, don't change unless you customized it)
OLLAMA_BASE_URL=http://localhost:11434
```

> [!NOTE]
> You **do not** need any Anthropic/OpenAI/OpenRouter API keys when using Ollama.

---

## Step 4 — Install Python Ollama client

In the `kai_bot/` directory, run:

```bash
pip install ollama
```

Or add it to `requirements.txt`:

```
ollama>=0.3.0
```

---

## Step 5 — Start Everything

Open **two terminals** side by side:

**Terminal 1 — Ollama server:**
```bash
ollama serve
```

**Terminal 2 — KAI Bot API:**
```bash
cd "KAIBAR DAPP/kai_bot"
..\.venv\Scripts\Activate.ps1
python api.py
```

Then open the chatbot at:
```
http://localhost:8000/app/index.html
```

---

## How It Works (Architecture)

```
User Message
     ↓
AgentOrchestrator (agents.py)
  ├── Vault Agent       → answers vault/yield questions
  ├── Tokenomics Agent  → answers price/supply questions
  ├── AMM Agent         → answers liquidity pool questions
  ├── Airdrop Agent     → handles distributions
  ├── Wallet Agent      → registers/lists wallets
  └── Fallback ──────→ Ollama LLM (general chat)
                         ↓
                   llama3.2 running locally
```

The specialized agents answer fast using real data from your modules. If a question doesn't match any agent keyword, it falls back to your local Ollama LLM for a free-form AI answer.

---

## Supported Models Comparison

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| `llama3.2` | 2–4GB | Fast | General purpose (recommended) |
| `phi3` | 2GB | Very Fast | Lightweight, low RAM |
| `mistral` | 4GB | Fast | Coding & analysis |
| `gemma2` | 5GB | Medium | Instruction following |
| `llama3.1:8b` | 5GB | Medium | Best quality |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Connection refused` on port 11434 | Run `ollama serve` in a terminal first |
| `model not found` error | Run `ollama pull <model-name>` |
| Slow responses | Try a smaller model like `phi3` |
| Bot still uses old provider | Check `.env` has `AI_PROVIDER=ollama` |
| `ImportError: ollama` | Run `pip install ollama` |
