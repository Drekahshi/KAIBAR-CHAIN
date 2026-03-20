"use client";
import { RefreshCw, Eye, ArrowUpRight, ArrowDownLeft, Shield, Flame, Send, ArrowDownToLine } from "lucide-react";

const tokens = [
  { name: "Hedera HBAR",     symbol: "HBAR",  balance: "0.00", usd: "$0.00",  color: "from-yellow to-gold",       dot: "#FDE047" },
  { name: "KAI Cents",       symbol: "KAI",   balance: "586",  usd: "$58.60", color: "from-gold to-orange",        dot: "#FFD700" },
  { name: "GAMI Social",     symbol: "GAMI",  balance: "293",  usd: "$14.65", color: "from-orange to-orange-dark", dot: "#F97316" },
  { name: "YBOB Stablecoin", symbol: "YBOB",  balance: "0.00", usd: "$0.00",  color: "from-green-light to-green-mid", dot: "#40916C" },
];

const txns = [
  { type: "Received",  label: "Daily Mining Reward",  amount: "+100 KAI",  time: "2h ago", color: "text-green-400" },
  { type: "Sent",      label: "Vault Stake",           amount: "-50 KAI",   time: "5h ago", color: "text-kai-red" },
  { type: "Received",  label: "Referral Bonus",        amount: "+25 GAMI",  time: "1d ago", color: "text-green-400" },
  { type: "Swap",      label: "KAI → HBAR",            amount: "~0.8 HBAR", time: "2d ago", color: "text-yellow" },
];

export default function WalletPage() {
  return (
    <main className="p-4 pt-10 pb-24 flex flex-col gap-5">

      {/* ── PAGE HEADER ── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-white">My Wallet</h1>
          <p className="text-xs text-white/50 mt-0.5">Manage your KAIBAR assets</p>
        </div>
        <button className="glass p-2.5 rounded-xl text-white/60 hover:text-gold transition-colors">
          <Eye size={18} />
        </button>
      </div>

      {/* ── TOTAL BALANCE CARD ── */}
      <div className="glass rounded-2xl p-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-gold/5 via-transparent to-orange/5 pointer-events-none" />
        <div className="flex justify-between items-start mb-1 relative">
          <div>
            <p className="text-xs text-white/50 font-medium mb-2">TOTAL PORTFOLIO</p>
            <p className="text-4xl font-black text-white">$73.25</p>
            <p className="text-xs text-green-400 mt-1 font-medium flex items-center gap-1">
              <ArrowUpRight size={12} /> +2.4% today
            </p>
          </div>
          <button className="text-white/40 hover:text-gold transition-colors p-1">
            <RefreshCw size={16} />
          </button>
        </div>

        <div className="mt-6 pt-4 border-t border-white/10 flex gap-3">
          <button className="flex-1 bg-gold-gradient text-black font-bold py-2.5 rounded-xl text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-opacity shadow-gold">
            <ArrowUpRight size={16} strokeWidth={3} /> Send
          </button>
          <button className="flex-1 glass border border-gold/30 text-gold font-bold py-2.5 rounded-xl text-sm flex items-center justify-center gap-2 hover:bg-gold/10 transition-colors">
            <ArrowDownLeft size={16} strokeWidth={3} /> Receive
          </button>
        </div>
      </div>

      {/* ── TOKEN LIST ── */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between mb-1">
          <p className="text-sm font-bold text-white/80">Assets</p>
          <button className="text-xs text-gold/70 hover:text-gold">+ Associate Token</button>
        </div>
        {tokens.map(t => (
          <div key={t.symbol} className="glass glass-hover rounded-xl p-4 flex items-center gap-4 cursor-pointer transition-all">
            <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${t.color} flex items-center justify-center font-black text-sm text-black flex-shrink-0 shadow-md`}>
              {t.symbol[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm text-white truncate">{t.name}</p>
              <p className="text-xs text-white/50">{t.symbol}</p>
            </div>
            <div className="text-right flex-shrink-0">
              <p className="font-bold text-sm text-white">{t.balance}</p>
              <p className="text-xs text-white/50">{t.usd}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ── DAILY CLAIM ── */}
      <div className="glass rounded-2xl p-5 border border-gold/30 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-gold/5 to-orange/5 pointer-events-none" />
        <div className="relative flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Flame size={16} className="text-orange" />
              <p className="text-sm font-bold text-gold">🎁 Daily Tokens</p>
            </div>
            <p className="text-xs text-white/60 mb-3">Claim 100 KAI + 50 GAMI every 24 hours</p>
            <button className="bg-gold-gradient text-black font-bold px-5 py-2.5 rounded-xl text-sm shadow-gold hover:opacity-90 transition-opacity">
              Claim Tokens →
            </button>
          </div>
          <div className="text-3xl ml-3">🌟</div>
        </div>
      </div>

      {/* ── TRANSACTIONS ── */}
      <div className="flex flex-col gap-2">
        <p className="text-sm font-bold text-white/80 mb-1">Recent Activity</p>
        {txns.map((tx, i) => (
          <div key={i} className="glass rounded-xl px-4 py-3 flex items-center gap-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 
              ${tx.type === "Received" ? "bg-green-400/15 text-green-400" : 
                tx.type === "Sent" ? "bg-kai-red/15 text-kai-red" : "bg-yellow/15 text-yellow"}`}>
              {tx.type === "Received" ? <ArrowDownLeft size={14}/> : 
               tx.type === "Sent"     ? <ArrowUpRight size={14}/> :
               <RefreshCw size={14}/>}
            </div>
            <div className="flex-1">
              <p className="text-xs font-semibold text-white">{tx.label}</p>
              <p className="text-[10px] text-white/40">{tx.time}</p>
            </div>
            <span className={`text-xs font-bold ${tx.color}`}>{tx.amount}</span>
          </div>
        ))}
      </div>

    </main>
  );
}
