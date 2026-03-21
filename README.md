hedera certificate https://drive.google.com/file/d/1TzfY1nPsi-C24rHZ0NHBgQw70ENBLcNi/view?usp=drive_link
 # KAIBAR-CHAIN
 # 🌍 KAI (KAIBAR Ecosystem)

**Empowering Financial Growth in Kenya via Hedera Hashgraph & AI**  
*Built for the official Hedera Hackathon (17 Feb - 23 Mar 2026)*

---

## 💡 What is KAI?

KAI is a decentralized financial ecosystem designed to help people in Kenya **save, invest, transact, and grow wealth** using blockchain and AI. By bridging the gap between traditional mobile money (M-Pesa) and global digital assets, KAI brings together:

- **Decentralized Finance (DeFi)**
- **Real-world assets** (like bonds and gold)
- **AI-powered automation**
- **Everyday payments** (including M-Pesa Integration)

All in one simple, unified platform.

---

## ❗ The Problem

In Kenya today:
- Many people and small businesses don’t have access to proper financial services.  
- Savings lose value due to inflation.  
- Systems like M-Pesa, banks, and crypto are not connected.  

This makes it hard for individuals to grow their money or access global opportunities.

## ✅ The Solution

KAI creates a unified system where users can:
- **Save and invest** through digital vaults.  
- **Access global assets** like BTC and HBAR.  
- **Make payments** using QR codes or M-Pesa.  
- **Use AI agents** to automate complex financial actions.  

---

## ⚙️ How It Works

### 1. Connect
Users connect a wallet (MetaMask or HashPack) to access the Hedera network.

### 2. Automate
An AI agent helps manage tasks like:
- Mining rewards  
- Moving funds  
- Executing transactions  

### 3. Invest
Users choose from curated vaults such as:
- **YToken**: Diversified crypto ETF.
- **YGOLD**: Gold-backed assets.
- **YBOB**: Stablecoin backed by USDC and bonds.

### 4. Transact
Seamless transitions between digital and physical currency:
- Pay using QR codes.
- Deposit/Withdraw via M-Pesa.
- Send funds instantly to other wallets.

---

## 🤖 AI in KAI

KAI uses a lightweight AI agent architecture that can run locally or via API (Gemini/Ollama).

This means:
- **No expensive setup**: Easy access for everyone.
- **Natural Interaction**: Users can interact using simple commands like:
  > *“Deposit 500 YT into my vault”*

---

## 🎯 Vision & Why It Matters

**Vision:** A financial system where anyone can save, invest, and build wealth — simply and securely.

**KAI is built to:**
- Increase **financial inclusion**.
- Protect users from **inflation**.
- Enable access to **modern financial tools**.
- Bring **Web3 to everyday users** in a simple way.

---

## 🛠 Project Architecture

The project is structured as a monorepo containing the following components:

- **`kaibar-frontend/`**: Next.js 15+ Web application.
- **`backend/`**: Python FastAPI service for AI strategies and Hedera interactions.
- **`kai_bot/`**: Python CLI tool for ecosystem operations and multi-agent orchestration.
- **`contracts/`**: Solidity smart contracts for Vaults, AMM, and Tokens on Hedera.

---

## 🚀 Local Setup Guide

### Prerequisites
- **Node.js** (v18+)
- **Python** (v3.10+)
- **Hedera Testnet Account** (Private Key & Account ID)

### 1. Frontend Setup
```bash
cd kaibar-frontend
npm install
npm run dev
```
*Access at: http://localhost:3000*

### 2. Backend API Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
*Docs at: http://localhost:8000/docs*

### 3. KAI Bot (CLI) Setup
```bash
cd kai_bot
python kai_bot.py
```
*Run `help` inside the bot to see available commands.*

---

## 🏆 Hackathon Submission

This project is a submission for the **Hedera Hackathon (Feb-Mar 2026)**.

- **Status:** Open Source (MIT License)
- **Network:** Hedera Testnet
- **Submission Date:** March 2026



---
*Built with ❤️ for the Hedera ecosystem.*
