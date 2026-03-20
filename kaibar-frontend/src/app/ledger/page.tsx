"use client";
import { Package, FileText, CheckCircle, Clock, PlusCircle, TrendingUp, Users, Coins } from "lucide-react";
import { useState } from "react";

const invoices = [
  { id: "INV-001", asset: "Solar Panel Kit 500W",  amount: "400 KAI",   status: "paid",    time: "2h ago" },
  { id: "INV-002", asset: "Agricultural Seeds Box",amount: "125 KAI",   status: "pending", time: "5h ago" },
  { id: "INV-003", asset: "Software License Pack", amount: "800 KAI",   status: "paid",    time: "1d ago" },
  { id: "INV-004", asset: "Consulting Service",    amount: "200 GAMI",  status: "pending", time: "2d ago" },
];

export default function LedgerPage() {
  const [assetName, setAssetName] = useState("");
  const [value, setValue] = useState("");
  const [qty, setQty] = useState("");

  return (
    <main className="p-4 pt-10 pb-24 flex flex-col gap-6">

      {/* ── HEADER ── */}
      <div>
        <h1 className="text-2xl font-black text-white">SME Ledger</h1>
        <p className="text-xs text-white/50 mt-0.5">Tokenize assets · Digitize payments · On-chain receipts</p>
      </div>

      {/* ── STATS STRIP ── */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { icon: <Package size={14}/>,   label: "Assets Issued", val: "24",    color: "text-gold" },
          { icon: <TrendingUp size={14}/>, label: "Revenue",       val: "1,450", color: "text-green-400" },
          { icon: <Users size={14}/>,      label: "Customers",     val: "11",    color: "text-orange" },
        ].map(s => (
          <div key={s.label} className="glass rounded-xl p-3 text-center">
            <div className={`flex justify-center mb-1 ${s.color}`}>{s.icon}</div>
            <p className={`text-xl font-black ${s.color}`}>{s.val}</p>
            <p className="text-[9px] text-white/50 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* ── TOKENIZE FORM ── */}
      <div className="glass rounded-2xl p-5 border border-gold/20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-gold/5 to-orange/5 pointer-events-none" />
        <div className="relative">
          <h2 className="text-base font-bold text-gold mb-1 flex items-center gap-2">
            <Coins size={16} className="text-gold" /> Mint New Asset Token
          </h2>
          <p className="text-xs text-white/50 mb-4">Create a blockchain-backed digital receipt for any real-world product or service.</p>

          <div className="flex flex-col gap-3">
            <input
              value={assetName}
              onChange={e => setAssetName(e.target.value)}
              type="text"
              placeholder="Asset name (e.g. Organic Coffee Beans – 5kg)"
              className="w-full bg-black/30 border border-white/10 focus:border-gold/50 rounded-xl px-4 py-3 text-sm outline-none transition-colors placeholder-white/30"
            />
            <div className="flex gap-3">
              <input
                value={value}
                onChange={e => setValue(e.target.value)}
                type="number"
                placeholder="Value (KAI)"
                className="w-1/2 bg-black/30 border border-white/10 focus:border-gold/50 rounded-xl px-4 py-3 text-sm outline-none transition-colors placeholder-white/30"
              />
              <input
                value={qty}
                onChange={e => setQty(e.target.value)}
                type="number"
                placeholder="Qty"
                className="w-1/2 bg-black/30 border border-white/10 focus:border-gold/50 rounded-xl px-4 py-3 text-sm outline-none transition-colors placeholder-white/30"
              />
            </div>
            <button
              className={`w-full font-bold rounded-xl py-3.5 text-sm flex items-center justify-center gap-2 transition-all
                ${assetName && value
                  ? "bg-gold-gradient text-black shadow-gold hover:opacity-90 hover:-translate-y-0.5"
                  : "bg-white/10 text-white/40 cursor-not-allowed"}`}>
              <PlusCircle size={16} strokeWidth={2.5} />
              Generate SME Token on Hedera
            </button>
          </div>
        </div>
      </div>

      {/* ── INVOICES / RECEIPTS ── */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-bold text-white/80 flex items-center gap-2">
            <FileText size={14} className="text-gold" /> Digital Payments
          </p>
          <button className="text-xs text-gold/70 hover:text-gold transition-colors">View All</button>
        </div>

        <div className="flex flex-col gap-2">
          {invoices.map(inv => (
            <div key={inv.id} className="glass glass-hover rounded-xl p-4 flex items-center gap-3 transition-all cursor-pointer">
              <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0
                ${inv.status === "paid"
                  ? "bg-green-400/15 text-green-400"
                  : "bg-orange/15 text-orange"}`}>
                {inv.status === "paid" ? <CheckCircle size={15}/> : <Clock size={15}/>}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-white truncate">{inv.asset}</p>
                <p className="text-[10px] text-white/40">{inv.id} · {inv.time}</p>
              </div>
              <div className="flex-shrink-0 text-right">
                <p className="text-xs font-bold text-white">{inv.amount}</p>
                <p className={`text-[10px] font-medium capitalize ${inv.status === "paid" ? "text-green-400" : "text-orange"}`}>
                  {inv.status}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

    </main>
  );
}
