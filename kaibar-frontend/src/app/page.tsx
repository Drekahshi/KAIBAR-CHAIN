"use client";
import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useKaibarStore } from "@/store/useKaibarStore";
import WalletConnectModal from "@/components/ui/WalletConnectModal";
import { Copy, Share2, ExternalLink, Zap, TrendingUp, Shield, ChevronRight, Circle } from "lucide-react";

const TICKER = [
  { s: "HBAR",   p: "$0.0891", c: "+3.2%"  },
  { s: "YToken", p: "$0.0234", c: "+8.7%"  },
  { s: "KAI",    p: "$0.1020", c: "+12.4%" },
  { s: "GAMI",   p: "$0.0501", c: "+5.1%"  },
  { s: "YBOB",   p: "$1.0012", c: "+0.1%"  },
];

const quickActions = [
  { name: "Mine",       href: "/mine",       emoji: "⛏️",  color: "#F97316" },
  { name: "Vaults",     href: "/vaults",     emoji: "🏦",  color: "#FFD700" },
  { name: "Pay",        href: "/pay",        emoji: "📱",  color: "#22C55E" },
  { name: "Securities", href: "/securities", emoji: "🏛️",  color: "#A78BFA" },
];

export default function Home() {
  const { connected, accountId, walletType, balances,
          autoMineActive, toggleAutoMine, incrementKai } = useKaibarStore();
  const [showModal, setShowModal] = useState(false);
  const [tickerOffset, setTickerOffset] = useState(0);

  // Auto-mine engine
  useEffect(() => {
    if (!autoMineActive) return;
    const id = setInterval(() => incrementKai(0.003), 1000);
    return () => clearInterval(id);
  }, [autoMineActive, incrementKai]);

  // Ticker animation
  useEffect(() => {
    const id = setInterval(() => setTickerOffset(o => (o - 1) % 400), 30);
    return () => clearInterval(id);
  }, []);

  return (
    <main style={{ display:"flex", flexDirection:"column", minHeight:"100vh" }}>

      {/* ── TICKER STRIP ── */}
      <div style={{
        background:"rgba(0,0,0,0.3)", borderBottom:"1px solid rgba(255,215,0,0.15)",
        padding:"6px 0", overflow:"hidden", flexShrink:0,
      }}>
        <div style={{
          display:"inline-flex", gap:32, paddingLeft:16,
          transform:`translateX(${tickerOffset}px)`, whiteSpace:"nowrap"
        }}>
          {[...TICKER,...TICKER,...TICKER].map((t,i) => (
            <span key={i} style={{ fontSize:11, fontWeight:600 }}>
              <span style={{ color:"rgba(255,255,255,0.6)" }}>{t.s} </span>
              <span style={{ color:"#fff" }}>{t.p} </span>
              <span style={{ color:"#22C55E" }}>{t.c}</span>
            </span>
          ))}
        </div>
      </div>

      {/* ── HEADER ── */}
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between",
                    padding:"16px 20px 8px" }}>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <div className="float" style={{
            width:40, height:40, borderRadius:"50%",
            background:"linear-gradient(135deg,#FFD700,#F97316)",
            display:"flex", alignItems:"center", justifyContent:"center",
            boxShadow:"0 0 16px rgba(255,215,0,0.5)",
          }}>
            <span style={{ color:"#1B4332", fontWeight:900, fontSize:18 }}>K</span>
          </div>
          <div>
            <span className="shimmer-text" style={{ fontSize:20, fontWeight:900, letterSpacing:2 }}>KAIBAR</span>
            <p style={{ fontSize:9, color:"rgba(255,255,255,0.4)", margin:0, letterSpacing:1 }}>
              HCS-10 · HEDERA SCHEDULE SERVICE
            </p>
          </div>
        </div>

        {/* Wallet button */}
        <button onClick={() => setShowModal(true)}
          style={{
            background: connected ? "linear-gradient(135deg,#22C55E,#16A34A)" : "linear-gradient(135deg,#FFD700,#F97316)",
            color: "#1B4332", fontWeight:700, fontSize:11, padding:"8px 14px",
            borderRadius:999, border:"none", cursor:"pointer",
            boxShadow: connected ? "0 0 12px rgba(34,197,94,0.4)" : "0 0 12px rgba(255,215,0,0.4)",
          }}>
          {connected ? `✓ ${accountId.substring(0,12)}…` : "🔗 Connect"}
        </button>
      </div>

      {/* ── HCS-10 BADGE ── */}
      <div style={{
        margin:"0 16px 12px", padding:"10px 14px", borderRadius:12,
        background:"rgba(167,139,250,0.08)", border:"1px solid rgba(167,139,250,0.25)",
        display:"flex", alignItems:"center", gap:10,
      }}>
        <div style={{ fontSize:20 }}>🌐</div>
        <div style={{ flex:1 }}>
          <p style={{ fontSize:11, fontWeight:700, color:"#A78BFA", margin:0 }}>
            HCS-10 Open Conversation AI · Hedera Schedule Service
          </p>
          <p style={{ fontSize:10, color:"rgba(255,255,255,0.45)", margin:"2px 0 0" }}>
            Agentic wallet · x402 micropayments · AI-driven execution
          </p>
        </div>
        <div style={{ display:"flex", gap:4 }}>
          {[...Array(3)].map((_,i) => (
            <div key={i} style={{
              width:6, height:6, borderRadius:"50%", background:"#A78BFA",
              animation:`pulse-gold ${1 + i*0.3}s ease-in-out infinite`,
            }} />
          ))}
        </div>
      </div>

      {/* ── PROFILE CARD ── */}
      <div className="glass" style={{ margin:"0 16px 14px", padding:20, position:"relative", overflow:"hidden" }}>
        <div style={{
          position:"absolute", top:-20, right:-20, width:80, height:80,
          borderRadius:"50%", background:"rgba(255,215,0,0.08)", filter:"blur(20px)"
        }} />

        <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", marginBottom:16 }}>
          <div style={{ display:"flex", alignItems:"center", gap:14 }}>
            <div style={{
              width:52, height:52, borderRadius:"50%",
              background:"linear-gradient(135deg,#FFD700,#F97316)",
              padding:2,
            }}>
              <div style={{
                width:"100%", height:"100%", borderRadius:"50%",
                background:"#1B4332", display:"flex", alignItems:"center", justifyContent:"center",
                fontSize:22, fontWeight:900, color:"#FFD700",
              }}>A</div>
            </div>
            <div>
              <p style={{ fontSize:11, color:"rgba(255,255,255,0.4)", margin:"0 0 2px" }}>Good morning,</p>
              <h2 style={{ fontSize:17, fontWeight:900, margin:"0 0 2px", color:"#fff" }}>AUSTIN NAMUYE</h2>
              <p style={{ fontSize:10, color:"rgba(255,255,255,0.35)", margin:0 }}>
                @drekahshi · 🇰🇪 Kenya
              </p>
            </div>
          </div>
          <div style={{
            background:"rgba(255,215,0,0.1)", border:"1px solid rgba(255,215,0,0.3)",
            borderRadius:999, padding:"5px 10px", fontSize:11, color:"#FFD700", fontWeight:600,
          }}>👥 1 Referral</div>
        </div>

        {/* Balance pills */}
        <div style={{ display:"flex", gap:8, marginBottom:14 }}>
          {[
            { l:"HBAR",   v: balances.hbar.toFixed(2), col:"#FDE047" },
            { l:"YToken", v: balances.ytoken.toFixed(0), col:"#FFD700" },
            { l:"KAI",    v: balances.kai.toFixed(2), col:"#F97316" },
            { l:"GAMI",   v: balances.gami.toFixed(0), col:"#22C55E" },
          ].map(b => (
            <div key={b.l} style={{
              flex:1, background:"rgba(255,255,255,0.05)", borderRadius:12,
              padding:"8px 6px", border:"1px solid rgba(255,255,255,0.08)", textAlign:"center",
            }}>
              <p style={{ fontSize:9, color:"rgba(255,255,255,0.4)", margin:"0 0 2px", fontWeight:700 }}>{b.l}</p>
              <p style={{ fontSize:14, fontWeight:900, color:b.col, margin:0 }}>{b.v}</p>
            </div>
          ))}
        </div>

        {/* Wallet action strip */}
        <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
          {["Copy Link","Share","Profile"].map(a => (
            <button key={a} style={{
              background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.1)",
              borderRadius:8, padding:"6px 12px", fontSize:11, color:"rgba(255,255,255,0.8)",
              cursor:"pointer", fontWeight:600,
            }}>{a}</button>
          ))}
          <div style={{ marginLeft:"auto", display:"flex", alignItems:"center", gap:6,
            background:"rgba(249,115,22,0.15)", border:"1px solid rgba(249,115,22,0.3)",
            borderRadius:8, padding:"6px 12px", fontSize:11, color:"#F97316", fontWeight:700,
          }}>
            <span style={{ width:6, height:6, borderRadius:"50%", background:"#F97316", display:"inline-block", animation:"pulse-gold 1.5s infinite" }} />
            Active
          </div>
        </div>
      </div>

      {/* ── AUTO-MINE AGENT ── */}
      <div className="glass" style={{
        margin:"0 16px 14px", padding:16,
        background: autoMineActive
          ? "linear-gradient(135deg,rgba(249,115,22,0.12),rgba(255,215,0,0.08))"
          : "rgba(255,255,255,0.05)",
        border: autoMineActive ? "1px solid rgba(249,115,22,0.4)" : "1px solid rgba(255,215,0,0.15)",
      }}>
        <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <div style={{ fontSize:28 }}>⛏️</div>
            <div>
              <p style={{ fontSize:13, fontWeight:800, color:"#FFD700", margin:0 }}>
                Auto-Drop Mining Agent
              </p>
              <p style={{ fontSize:10, color:"rgba(255,255,255,0.5)", margin:"2px 0 0" }}>
                {autoMineActive
                  ? `🤖 Bot mining… +${(balances.kai % 1).toFixed(3)} KAI mined`
                  : "Enable bot to auto-mine KAI daily tokens"}
              </p>
            </div>
          </div>

          {/* Toggle */}
          <button onClick={connected ? toggleAutoMine : () => setShowModal(true)}
            style={{
              width:52, height:28, borderRadius:14,
              background: autoMineActive ? "linear-gradient(135deg,#22C55E,#16A34A)" : "rgba(255,255,255,0.1)",
              border: autoMineActive ? "none" : "1px solid rgba(255,255,255,0.2)",
              cursor:"pointer", position:"relative", transition:"all 0.3s ease",
              boxShadow: autoMineActive ? "0 0 16px rgba(34,197,94,0.5)" : "none",
              padding: 0, display:"flex", alignItems:"center",
            }}>
            <div style={{
              width:22, height:22, borderRadius:"50%", background:"#fff",
              position:"absolute", transition:"left 0.3s ease",
              left: autoMineActive ? 27 : 3, boxShadow:"0 2px 8px rgba(0,0,0,0.3)",
            }} />
          </button>
        </div>

        {autoMineActive && (
          <div style={{
            marginTop:10, display:"flex", gap:8, alignItems:"center",
            background:"rgba(34,197,94,0.08)", borderRadius:8, padding:"6px 10px",
          }}>
            <div style={{ width:6, height:6, borderRadius:"50%", background:"#22C55E", animation:"pulse-gold 1s infinite" }} />
            <p style={{ fontSize:10, color:"#22C55E", fontWeight:700, margin:0 }}>
              Mining active · +0.003 KAI/sec · Agent running on Hedera Testnet
            </p>
          </div>
        )}
      </div>

      {/* ── QUICK ACTIONS ── */}
      <div style={{ padding:"0 16px 14px" }}>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
          {quickActions.map(({ name, href, emoji, color }) => (
            <Link key={name} href={href} style={{ textDecoration:"none" }}>
              <div className="glass glass-hover" style={{ padding:"20px 16px", borderRadius:20,
                display:"flex", flexDirection:"column", alignItems:"center", gap:10, cursor:"pointer" }}>
                <div style={{
                  width:48, height:48, borderRadius:"50%",
                  background:`${color}20`, border:`2px solid ${color}50`,
                  display:"flex", alignItems:"center", justifyContent:"center", fontSize:22,
                  boxShadow:`0 0 16px ${color}30`,
                }}>{emoji}</div>
                <span style={{ fontSize:13, fontWeight:700, color:"rgba(255,255,255,0.9)" }}>{name}</span>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ── CFA COMMUNITY DASHBOARD ── */}
      <div style={{ padding:"0 16px 14px" }}>
        <Link href="/cfa" style={{ textDecoration:"none" }}>
          <div className="glass glass-hover" style={{
            padding:"20px", borderRadius:20, display:"flex", alignItems:"center", gap:16, cursor:"pointer",
            background:"linear-gradient(135deg, rgba(34,197,94,0.1), rgba(34,197,94,0.05))",
            border:"1px solid rgba(34,197,94,0.2)"
          }}>
            <div style={{
              width:52, height:52, borderRadius:"50%", background:"#22C55E20", border:"2px solid #22C55E50",
              display:"flex", alignItems:"center", justifyContent:"center", fontSize:26,
              boxShadow:"0 0 16px #22C55E30", flexShrink:0
            }}>🌲</div>
            <div style={{ flex:1 }}>
              <h3 style={{ fontSize:16, fontWeight:800, color:"#22C55E", margin:"0 0 4px" }}>CFA Dashboard</h3>
              <p style={{ fontSize:11, color:"rgba(255,255,255,0.6)", margin:0 }}>Community Treasury • Governance • Assets</p>
            </div>
            <ChevronRight color="#22C55E" opacity={0.5} />
          </div>
        </Link>
      </div>

      {/* ── SME DASHBOARD ── */}
      <div style={{ padding:"0 16px 14px" }}>
        <Link href="/sme" style={{ textDecoration:"none" }}>
          <div className="glass glass-hover" style={{
            padding:"20px", borderRadius:20, display:"flex", alignItems:"center", gap:16, cursor:"pointer",
            background:"linear-gradient(135deg, rgba(59,130,246,0.1), rgba(59,130,246,0.05))",
            border:"1px solid rgba(59,130,246,0.2)"
          }}>
            <div style={{
              width:52, height:52, borderRadius:"50%", background:"#3B82F620", border:"2px solid #3B82F650",
              display:"flex", alignItems:"center", justifyContent:"center", fontSize:26,
              boxShadow:"0 0 16px #3B82F630", flexShrink:0
            }}>🏪</div>
            <div style={{ flex:1 }}>
              <h3 style={{ fontSize:16, fontWeight:800, color:"#3B82F6", margin:"0 0 4px" }}>SME Dashboard</h3>
              <p style={{ fontSize:11, color:"rgba(255,255,255,0.6)", margin:0 }}>Digitize Cash • Inventory • Loans • AI Agents</p>
            </div>
            <ChevronRight color="#3B82F6" opacity={0.5} />
          </div>
        </Link>
      </div>

      {/* ── ECOSYSTEM STATS ── */}
      <div style={{ padding:"0 16px 16px" }}>
        <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:10 }}>
          <TrendingUp size={15} color="#FFD700" />
          <span style={{ fontSize:13, fontWeight:700, color:"#FFD700" }}>Ecosystem Stats</span>
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:8 }}>
          {[
            { l:"Total TVL", v:"$2.4M", c:"#FFD700" },
            { l:"Miners",    v:"12.4K", c:"#22C55E" },
            { l:"Avg APY",   v:"27.5%", c:"#F97316" },
          ].map(s => (
            <div key={s.l} className="glass" style={{ padding:12, textAlign:"center", borderRadius:14 }}>
              <p style={{ fontSize:16, fontWeight:900, color:s.c, margin:0 }}>{s.v}</p>
              <p style={{ fontSize:9, color:"rgba(255,255,255,0.4)", margin:"3px 0 0", fontWeight:600 }}>{s.l}</p>
            </div>
          ))}
        </div>
      </div>

      {showModal && <WalletConnectModal onClose={() => setShowModal(false)} />}
    </main>
  );
}
