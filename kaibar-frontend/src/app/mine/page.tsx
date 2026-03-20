"use client";
import { useState, useEffect } from "react";
import { useKaibarStore } from "@/store/useKaibarStore";
import WalletConnectModal from "@/components/ui/WalletConnectModal";
import { Pickaxe, Zap, Gift, CheckCircle, Clock, Users, UserPlus } from "lucide-react";

const WHITELIST = [
  { name: "Alpha Miners",  spots: "247 / 500",  badge: "🔥 Hot",    status: "open",   reward: "500 KAI" },
  { name: "YToken Launch", spots: "89 / 200",   badge: "✨ Early",  status: "open",   reward: "1,000 YToken" },
  { name: "Bonzo Airdrop", spots: "500 / 500",  badge: "⏰ Closed", status: "closed", reward: "200 GAMI" },
];

export default function MinePage() {
  const { connected, balances, autoMineActive, toggleAutoMine, incrementKai } = useKaibarStore();
  const [showModal, setShowModal] = useState(false);
  const [claimed, setClaimed] = useState(false);
  const [minted, setMinted] = useState<string | null>(null);
  const [mintName, setMintName] = useState("");
  const [mintSym, setMintSym] = useState("");
  const [mintSupply, setMintSupply] = useState("");
  const [countdown, setCountdown] = useState(86400);

  // Countdown
  useEffect(() => {
    const id = setInterval(() => setCountdown(c => Math.max(0, c - 1)), 1000);
    return () => clearInterval(id);
  }, []);

  const fmtTime = (s: number) => {
    const h = Math.floor(s / 3600).toString().padStart(2, "0");
    const m = Math.floor((s % 3600) / 60).toString().padStart(2, "0");
    const sec = (s % 60).toString().padStart(2, "0");
    return `${h}:${m}:${sec}`;
  };

  const claim = () => {
    if (!connected) { setShowModal(true); return; }
    incrementKai(100);
    setClaimed(true);
  };

  const mint = () => {
    if (!mintName || !mintSym || !mintSupply) return;
    setMinted(`0.0.${Math.floor(Math.random() * 9000000 + 1000000)}`);
  };

  return (
    <main style={{ padding:"16px 16px 90px", display:"flex", flexDirection:"column", gap:16 }}>

      {/* Header */}
      <div style={{ paddingTop:32 }}>
        <h1 style={{ fontSize:24, fontWeight:900, color:"#fff", margin:0 }}>⛏️ Mining Hub</h1>
        <p style={{ fontSize:12, color:"rgba(255,255,255,0.5)", margin:"4px 0 0" }}>
          Auto-mine · Mint tokens · Whitelist spots
        </p>
      </div>

      {/* ── DAILY CLAIM CARD ── */}
      <div className="glass" style={{
        padding:20, borderRadius:20, border:"1px solid rgba(255,215,0,0.35)",
        background:"linear-gradient(135deg,rgba(255,215,0,0.08),rgba(249,115,22,0.05))",
        position:"relative", overflow:"hidden",
      }}>
        <p style={{ fontSize:11, fontWeight:700, color:"#FFD700", margin:"0 0 4px", letterSpacing:1 }}>DAILY CLAIM</p>
        <div style={{ display:"flex", alignItems:"flex-end", gap:10, marginBottom:12 }}>
          <span style={{ fontSize:36, fontWeight:900, color:"#fff" }}>100</span>
          <span style={{ fontSize:18, fontWeight:700, color:"#FFD700", paddingBottom:4 }}>KAI</span>
          <span style={{ fontSize:12, color:"rgba(255,255,255,0.4)", paddingBottom:4 }}>+ 50 YToken</span>
        </div>
        {!claimed ? (
          <button onClick={claim} className="btn-gold"
            style={{ padding:"12px 24px", borderRadius:12, fontSize:14, width:"100%" }}>
            🎁 Claim Daily Tokens
          </button>
        ) : (
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <CheckCircle size={20} color="#22C55E" />
            <div>
              <p style={{ fontSize:13, fontWeight:700, color:"#22C55E", margin:0 }}>Claimed! Next in:</p>
              <p style={{ fontSize:18, fontWeight:900, color:"#fff", fontFamily:"monospace", margin:"2px 0 0" }}>
                {fmtTime(countdown)}
              </p>
            </div>
            <div style={{ marginLeft:"auto", padding:"6px 12px", borderRadius:10, background:"rgba(34,197,94,0.1)",
              border:"1px solid rgba(34,197,94,0.3)", fontSize:11, color:"#22C55E", fontWeight:700,
            }}>🔢 Streak: 3</div>
          </div>
        )}
      </div>

      {/* ── AUTO-MINE BOT ── */}
      <div className="glass" style={{
        padding:18, borderRadius:20,
        background: autoMineActive ? "rgba(249,115,22,0.08)" : "rgba(255,255,255,0.04)",
        border: autoMineActive ? "1px solid rgba(249,115,22,0.4)" : "1px solid rgba(255,215,0,0.15)",
      }}>
        <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:12 }}>
          <div>
            <p style={{ fontSize:13, fontWeight:800, color:"#FFD700", margin:0 }}>🤖 Auto-Drop Agent</p>
            <p style={{ fontSize:10, color:"rgba(255,255,255,0.4)", margin:"3px 0 0" }}>
              AI bot mines KAI for you 24/7 on Hedera Testnet
            </p>
          </div>
          <button onClick={connected ? toggleAutoMine : () => setShowModal(true)}
            style={{
              width:56, height:30, borderRadius:14,
              background: autoMineActive ? "linear-gradient(135deg,#22C55E,#16A34A)" : "rgba(255,255,255,0.1)",
              border: autoMineActive ? "none" : "1px solid rgba(255,255,255,0.2)",
              cursor:"pointer", position:"relative", transition:"all 0.3s ease",
              boxShadow: autoMineActive ? "0 0 16px rgba(34,197,94,0.5)" : "none",
            }}>
            <div style={{
              width:24, height:24, borderRadius:"50%", background:"#fff",
              position:"absolute", transition:"left 0.3s ease", top:3,
              left: autoMineActive ? 29 : 3, boxShadow:"0 2px 6px rgba(0,0,0,0.3)",
            }} />
          </button>
        </div>

        {/* Mining stats */}
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:8 }}>
          {[
            { l:"Mining Rate", v:"0.003 KAI/s", c:"#F97316" },
            { l:"Total Mined",  v:`${balances.kai.toFixed(1)} KAI`, c:"#FFD700" },
            { l:"Status",       v: autoMineActive ? "🟢 Active" : "⚫ Idle", c:"#22C55E" },
          ].map(s => (
            <div key={s.l} style={{
              background:"rgba(255,255,255,0.04)", borderRadius:10,
              padding:"8px 10px", border:"1px solid rgba(255,255,255,0.06)",
            }}>
              <p style={{ fontSize:9, color:"rgba(255,255,255,0.4)", margin:"0 0 3px", fontWeight:700 }}>{s.l}</p>
              <p style={{ fontSize:12, fontWeight:800, color:s.c, margin:0 }}>{s.v}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── MINT TOKENS ── */}
      <div className="glass" style={{ padding:20, borderRadius:20, border:"1px solid rgba(167,139,250,0.3)" }}>
        <p style={{ fontSize:14, fontWeight:800, color:"#A78BFA", margin:"0 0 4px" }}>🏭 Mint New Token</p>
        <p style={{ fontSize:11, color:"rgba(255,255,255,0.5)", margin:"0 0 14px" }}>
          Deploy your own HTS token on Hedera
        </p>

        {!minted ? (
          <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
            <input value={mintName} onChange={e=>setMintName(e.target.value)}
              placeholder="Token name (e.g. FarmCoin)"
              style={{ background:"rgba(0,0,0,0.3)", border:"1px solid rgba(255,255,255,0.1)",
                borderRadius:12, padding:"12px 16px", fontSize:13, color:"#fff", outline:"none",
                fontFamily:"Inter, sans-serif",
              }} />
            <div style={{ display:"flex", gap:10 }}>
              <input value={mintSym} onChange={e=>setMintSym(e.target.value)}
                placeholder="Symbol (e.g. FRM)"
                style={{ flex:1, background:"rgba(0,0,0,0.3)", border:"1px solid rgba(255,255,255,0.1)",
                  borderRadius:12, padding:"12px 16px", fontSize:13, color:"#fff", outline:"none",
                  fontFamily:"Inter, sans-serif",
                }} />
              <input value={mintSupply} onChange={e=>setMintSupply(e.target.value)}
                type="number" placeholder="Supply"
                style={{ flex:1, background:"rgba(0,0,0,0.3)", border:"1px solid rgba(255,255,255,0.1)",
                  borderRadius:12, padding:"12px 16px", fontSize:13, color:"#fff", outline:"none",
                  fontFamily:"Inter, sans-serif",
                }} />
            </div>
            <button onClick={mint}
              style={{
                background: mintName && mintSym && mintSupply
                  ? "linear-gradient(135deg,#A78BFA,#7C3AED)"
                  : "rgba(255,255,255,0.1)",
                color: mintName && mintSym && mintSupply ? "#fff" : "rgba(255,255,255,0.3)",
                fontWeight:700, fontSize:14, padding:"12px", borderRadius:12,
                border:"none", cursor: mintName ? "pointer" : "not-allowed", fontFamily:"Inter, sans-serif",
              }}>
              🚀 Mint on Hedera Testnet
            </button>
          </div>
        ) : (
          <div style={{ textAlign:"center", padding:"12px 0" }}>
            <div style={{ fontSize:36, marginBottom:8 }}>🎉</div>
            <p style={{ fontSize:13, fontWeight:700, color:"#22C55E", margin:0 }}>Token Minted!</p>
            <p style={{ fontSize:11, color:"rgba(255,255,255,0.5)", margin:"6px 0 0" }}>Token ID:</p>
            <p style={{ fontFamily:"monospace", fontSize:14, fontWeight:700, color:"#FFD700", margin:"4px 0 12px" }}>
              {minted}
            </p>
            <button onClick={()=>{setMinted(null);setMintName("");setMintSym("");setMintSupply("")}}
              style={{ fontSize:12, color:"rgba(255,255,255,0.5)", background:"transparent",
                border:"1px solid rgba(255,255,255,0.1)", borderRadius:8, padding:"6px 14px", cursor:"pointer",
              }}>Mint another</button>
          </div>
        )}
      </div>

      {/* ── WHITELIST ── */}
      <div>
        <p style={{ fontSize:13, fontWeight:700, color:"rgba(255,255,255,0.7)", margin:"0 0 10px",
          display:"flex", alignItems:"center", gap:6 }}>
          <UserPlus size={15} color="#FFD700" /> Active Whitelists
        </p>
        <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
          {WHITELIST.map((w, i) => (
            <div key={i} className="glass glass-hover" style={{ padding:"14px 16px", borderRadius:16,
              display:"flex", alignItems:"center", gap:12 }}>
              <div style={{
                width:40, height:40, borderRadius:10, background:"rgba(255,215,0,0.1)",
                display:"flex", alignItems:"center", justifyContent:"center", fontSize:18,
              }}>🎫</div>
              <div style={{ flex:1 }}>
                <p style={{ fontSize:13, fontWeight:700, color:"#fff", margin:0 }}>{w.name}</p>
                <div style={{ display:"flex", gap:8, marginTop:3 }}>
                  <span style={{ fontSize:10, color:"rgba(255,255,255,0.4)" }}>
                    <Users size={10} style={{display:"inline",marginRight:3}} />{w.spots}
                  </span>
                  <span style={{ fontSize:10, color:"#22C55E" }}>🎁 {w.reward}</span>
                </div>
              </div>
              <div style={{ display:"flex", flexDirection:"column", alignItems:"flex-end", gap:4 }}>
                <span style={{ fontSize:10, fontWeight:700, color: w.status === "open" ? "#22C55E" : "#E63946" }}>
                  {w.badge}
                </span>
                <button
                  disabled={w.status === "closed"}
                  style={{
                    fontSize:11, fontWeight:700, padding:"5px 12px", borderRadius:8,
                    background: w.status === "open" ? "linear-gradient(135deg,#FFD700,#F97316)" : "rgba(255,255,255,0.05)",
                    color: w.status === "open" ? "#1B4332" : "rgba(255,255,255,0.3)",
                    border:"none", cursor: w.status === "open" ? "pointer" : "not-allowed",
                  }}>
                  {w.status === "open" ? "Join" : "Closed"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {showModal && <WalletConnectModal onClose={() => setShowModal(false)} />}
    </main>
  );
}
