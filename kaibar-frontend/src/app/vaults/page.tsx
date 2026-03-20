"use client";
import { useState } from "react";
import { TrendingUp, Shield, Zap, ChevronRight, ArrowUpRight } from "lucide-react";

const BUBBLES = [
  { sym:"KAI",    size:90,  apy:"28.4%", tvl:"$480K",  col:"#FFD700", x:50,  y:35 },
  { sym:"YToken", size:78,  apy:"22.1%", tvl:"$320K",  col:"#F97316", x:20,  y:55 },
  { sym:"HBAR",   size:72,  apy:"18.9%", tvl:"$280K",  col:"#45B7D1", x:75,  y:62 },
  { sym:"YBOB",   size:55,  apy:"12.0%", tvl:"$140K",  col:"#A78BFA", x:35,  y:78 },
  { sym:"GAMI",   size:50,  apy:"19.5%", tvl:"$110K",  col:"#22C55E", x:60,  y:80 },
  { sym:"USDC",   size:44,  apy:"8.0%",  tvl:"$90K",   col:"#3B82F6", x:12,  y:28 },
];

const BONZO_VAULTS = [
  { name:"YToken/KAI Pool",     protocol:"Bonzo · SaucerSwap", apy:"28.4%", tvl:"$480K",  risk:"Low",    badge:"🤖 AI Managed" },
  { name:"HBAR Liquidity",      protocol:"Bonzo · Hedera AMM", apy:"22.1%", tvl:"$320K",  risk:"Low",    badge:"🤖 AI Managed" },
  { name:"YGOLD-H Bond Vault",  protocol:"Bonzo Finance",      apy:"18.9%", tvl:"$280K",  risk:"Medium", badge:"🔒 Verified"   },
  { name:"YBOB Stablecoin Vault",protocol:"Bonzo · RWA",       apy:"12.0%", tvl:"$140K",  risk:"Low",    badge:"🛡️ Protected"  },
  { name:"GAMI Yield",          protocol:"Bonzo · Social Fi",  apy:"19.5%", tvl:"$110K",  risk:"Medium", badge:"🤖 AI Managed" },
];

export default function VaultsPage() {
  const [view, setView] = useState<"bubbles" | "list">("bubbles");
  const [selected, setSelected] = useState<number | null>(null);

  return (
    <main style={{ padding:"16px 16px 90px", display:"flex", flexDirection:"column", gap:16 }}>

      <div style={{ paddingTop:32 }}>
        <h1 style={{ fontSize:24, fontWeight:900, color:"#fff", margin:0 }}>🏦 Hedera Vaults</h1>
        <p style={{ fontSize:11, color:"rgba(255,255,255,0.5)", margin:"4px 0 0" }}>
          AI-managed yield · Powered by Bonzo Finance SDK
        </p>
      </div>

      {/* ── FEATURED BONZO FINANCE SHOWCASE ── */}
      <div style={{
        margin: "8px 0",
        padding: "20px",
        borderRadius: "24px",
        background: "linear-gradient(145deg, rgba(20, 24, 39, 0.9), rgba(15, 18, 30, 0.95))",
        border: "1px solid rgba(255,215,0,0.2)",
        position: "relative",
        overflow: "hidden",
        boxShadow: "0 12px 32px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.1)",
      }}>
        {/* Glow Effects */}
        <div style={{ position:"absolute", top:-40, right:-40, width:120, height:120, background:"rgba(255,215,0,0.15)", filter:"blur(40px)", borderRadius:"50%" }} />
        <div style={{ position:"absolute", bottom:-40, left:-40, width:100, height:100, background:"rgba(34,197,94,0.15)", filter:"blur(40px)", borderRadius:"50%" }} />

        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:16, position:"relative", zIndex:2 }}>
          <div>
            <div style={{ display:"inline-flex", alignItems:"center", gap:6, background:"rgba(249,115,22,0.15)", border:"1px solid rgba(249,115,22,0.3)", padding:"4px 10px", borderRadius:999, marginBottom:10 }}>
              <span style={{ width:6, height:6, background:"#F97316", borderRadius:"50%", animation:"pulse-gold 1.5s infinite" }} />
              <span style={{ fontSize:10, fontWeight:800, color:"#F97316", letterSpacing:0.5 }}>FEATURED INTEGRATION</span>
            </div>
            <h2 style={{ fontSize:20, fontWeight:900, color:"#fff", margin:"0 0 4px" }}>Bonzo HBAR Vault</h2>
            <p style={{ fontSize:12, color:"rgba(255,255,255,0.6)", margin:0, lineHeight:1.4 }}>
              Deposit native <strong style={{color:"#fff"}}>HBAR</strong>. We auto-wrap and supply it seamlessly to Bonzo Finance for instant yield block-by-block.
            </p>
          </div>
          <div style={{ width:48, height:48, background:"linear-gradient(135deg, #FFD700, #F97316)", borderRadius:14, display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0, boxShadow:"0 4px 16px rgba(255,215,0,0.3)" }}>
            <span style={{ fontSize:24 }}>🏦</span>
          </div>
        </div>

        <div style={{ display:"flex", gap:12, marginBottom:16, position:"relative", zIndex:2 }}>
          <div style={{ flex:1, background:"rgba(0,0,0,0.3)", border:"1px solid rgba(255,255,255,0.05)", borderRadius:14, padding:12 }}>
            <p style={{ fontSize:10, color:"rgba(255,255,255,0.4)", margin:"0 0 2px", fontWeight:700 }}>Bonzo APY</p>
            <p style={{ fontSize:18, fontWeight:900, color:"#22C55E", margin:0 }}>18.4%</p>
          </div>
          <div style={{ flex:1, background:"rgba(0,0,0,0.3)", border:"1px solid rgba(255,255,255,0.05)", borderRadius:14, padding:12 }}>
            <p style={{ fontSize:10, color:"rgba(255,255,255,0.4)", margin:"0 0 2px", fontWeight:700 }}>Total Liquidity</p>
            <p style={{ fontSize:18, fontWeight:900, color:"#FFD700", margin:0 }}>$1.2M</p>
          </div>
        </div>

        <div style={{ display:"flex", gap:8, position:"relative", zIndex:2 }}>
          <div style={{ flex:1, position:"relative" }}>
            <input 
              type="number" 
              placeholder="0.0" 
              style={{ width:"100%", background:"rgba(255,255,255,0.05)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:12, padding:"12px 16px", color:"#fff", fontSize:16, fontWeight:700, fontFamily:"Inter, sans-serif", outline:"none" }}
            />
            <span style={{ position:"absolute", right:16, top:13, fontSize:12, fontWeight:800, color:"rgba(255,255,255,0.4)" }}>HBAR</span>
          </div>
          <button style={{ background:"linear-gradient(135deg, #22C55E, #16A34A)", border:"none", borderRadius:12, padding:"0 20px", color:"#fff", fontWeight:800, fontSize:13, cursor:"pointer", boxShadow:"0 4px 12px rgba(34,197,94,0.3)", transition:"transform 0.1s" }} onMouseOver={e => e.currentTarget.style.transform="scale(1.02)"} onMouseOut={e => e.currentTarget.style.transform="scale(1)"}>
            Deposit
          </button>
        </div>
      </div>

      {/* View toggle */}
      <div style={{ display:"flex", background:"rgba(255,255,255,0.05)", borderRadius:12, padding:3 }}>
        {(["bubbles","list"] as const).map(v => (
          <button key={v} onClick={() => setView(v)} style={{
            flex:1, padding:"8px", borderRadius:10, fontWeight:700, fontSize:12, border:"none", cursor:"pointer",
            background: view === v ? "linear-gradient(135deg,#FFD700,#F97316)" : "transparent",
            color: view === v ? "#1B4332" : "rgba(255,255,255,0.5)",
            transition:"all 0.2s ease", textTransform:"capitalize", fontFamily:"Inter, sans-serif",
          }}>
            {v === "bubbles" ? "🫧 Explore All" : "📋 List View"}
          </button>
        ))}
      </div>

      {/* ── BUBBLES VIEW ── */}
      {view === "bubbles" && (
        <div style={{ position:"relative", height:280, overflow:"hidden", borderRadius:20 }}
             className="glass">
          <div style={{ position:"absolute", inset:0, display:"flex", alignItems:"center", justifyContent:"center" }}>
            <p style={{ fontSize:10, color:"rgba(255,255,255,0.2)", fontWeight:600 }}>
              Tap a bubble to view vault
            </p>
          </div>
          {BUBBLES.map((b, i) => (
            <button key={i} onClick={() => setSelected(i === selected ? null : i)}
              style={{
                position:"absolute", borderRadius:"50%",
                width:b.size, height:b.size,
                left:`${b.x}%`, top:`${b.y}%`,
                background:`radial-gradient(circle at 35% 35%, ${b.col}cc, ${b.col}55)`,
                border:`2px solid ${b.col}90`,
                boxShadow: selected === i
                  ? `0 0 30px ${b.col}80, 0 0 60px ${b.col}30`
                  : `0 0 12px ${b.col}40`,
                cursor:"pointer", display:"flex", flexDirection:"column",
                alignItems:"center", justifyContent:"center",
                transition:"all 0.3s ease",
                transform: `translate(-50%,-50%) scale(${selected === i ? 1.15 : 1})`,
                animation:`float ${3 + i * 0.4}s ease-in-out infinite`,
              }}>
              <span style={{ fontSize:b.size > 65 ? 11 : 9, fontWeight:900, color:"#fff" }}>{b.sym}</span>
              <span style={{ fontSize:b.size > 65 ? 10 : 8, fontWeight:700, color:"rgba(255,255,255,0.8)" }}>
                {b.apy}
              </span>
            </button>
          ))}
          {selected !== null && (
            <div style={{
              position:"absolute", bottom:12, left:"50%", transform:"translateX(-50%)",
              background:"rgba(0,0,0,0.8)", backdropFilter:"blur(16px)",
              border:`1px solid ${BUBBLES[selected].col}60`,
              borderRadius:12, padding:"10px 16px",
              display:"flex", alignItems:"center", gap:12, whiteSpace:"nowrap",
              zIndex:10,
            }}>
              <div>
                <p style={{ fontSize:12, fontWeight:800, color:BUBBLES[selected].col, margin:0 }}>
                  {BUBBLES[selected].sym} Pool
                </p>
                <p style={{ fontSize:10, color:"rgba(255,255,255,0.5)", margin:0 }}>
                  APY: {BUBBLES[selected].apy} · TVL: {BUBBLES[selected].tvl}
                </p>
              </div>
              <button className="btn-gold" style={{ padding:"6px 14px", borderRadius:8, fontSize:11 }}>
                Stake →
              </button>
            </div>
          )}
        </div>
      )}

      {/* ── LIST VIEW ── */}
      {view === "list" && (
        <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
          {BONZO_VAULTS.map((v, i) => (
            <div key={i} className="glass glass-hover" style={{ padding:"14px 16px", borderRadius:18, cursor:"pointer" }}>
              <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", marginBottom:8 }}>
                <div>
                  <p style={{ fontSize:13, fontWeight:800, color:"#fff", margin:0 }}>{v.name}</p>
                  <p style={{ fontSize:10, color:"rgba(255,255,255,0.4)", margin:"3px 0 0" }}>{v.protocol}</p>
                </div>
                <span style={{
                  fontSize:10, fontWeight:700, padding:"3px 8px", borderRadius:999,
                  background: v.badge.includes("AI")
                    ? "rgba(167,139,250,0.2)" : "rgba(34,197,94,0.15)",
                  color: v.badge.includes("AI") ? "#A78BFA" : "#22C55E",
                  border: `1px solid ${v.badge.includes("AI") ? "rgba(167,139,250,0.3)" : "rgba(34,197,94,0.3)"}`,
                }}>
                  {v.badge}
                </span>
              </div>
              <div style={{ display:"flex", gap:10, marginBottom:12 }}>
                <div style={{ flex:1, background:"rgba(255,255,255,0.04)", borderRadius:10, padding:"8px 10px" }}>
                  <p style={{ fontSize:9, color:"rgba(255,255,255,0.4)", margin:"0 0 2px", fontWeight:700 }}>APY</p>
                  <p style={{ fontSize:16, fontWeight:900, color:"#22C55E", margin:0 }}>{v.apy}</p>
                </div>
                <div style={{ flex:1, background:"rgba(255,255,255,0.04)", borderRadius:10, padding:"8px 10px" }}>
                  <p style={{ fontSize:9, color:"rgba(255,255,255,0.4)", margin:"0 0 2px", fontWeight:700 }}>TVL</p>
                  <p style={{ fontSize:16, fontWeight:900, color:"#FFD700", margin:0 }}>{v.tvl}</p>
                </div>
                <div style={{ flex:1, background:"rgba(255,255,255,0.04)", borderRadius:10, padding:"8px 10px" }}>
                  <p style={{ fontSize:9, color:"rgba(255,255,255,0.4)", margin:"0 0 2px", fontWeight:700 }}>RISK</p>
                  <p style={{ fontSize:14, fontWeight:900,
                    color: v.risk === "Low" ? "#22C55E" : "#F97316", margin:0 }}>{v.risk}</p>
                </div>
              </div>
              <div style={{ display:"flex", gap:8 }}>
                <button className="btn-gold" style={{ flex:1, padding:"10px", borderRadius:12, fontSize:13 }}>
                  Stake
                </button>
                <button style={{ flex:1, padding:"10px", borderRadius:12, fontSize:13, fontWeight:700,
                  background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.1)",
                  color:"rgba(255,255,255,0.7)", cursor:"pointer", fontFamily:"Inter, sans-serif",
                }}>
                  Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

    </main>
  );
}
