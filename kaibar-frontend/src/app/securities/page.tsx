"use client";
import { useState } from "react";
import { Shield, TrendingUp, Landmark, Globe, ChevronRight } from "lucide-react";

const SECURITIES = [
  {
    id: "trust",
    icon: "🤝",
    name: "KAI Trust",
    desc: "Time-locked token trust for beneficiaries",
    apy: "15.2%",
    minStake: "100 KAI",
    color: "#FFD700",
    features: ["Time-lock smart contract","Named beneficiary","Hedera Schedule Service execution"],
  },
  {
    id: "pension",
    icon: "🏦",
    name: "KAIBAR Pension",
    desc: "Long-term retirement savings in KAI/HBAR",
    apy: "12.8%",
    minStake: "500 KAI",
    color: "#A78BFA",
    features: ["Vesting schedule","Monthly auto-deposit","Compound yield"],
  },
  {
    id: "mmf",
    icon: "💵",
    name: "Money Market Fund",
    desc: "Low-risk YBOB/USDC liquidity basket",
    apy: "7.5%",
    minStake: "50 YBOB",
    color: "#22C55E",
    features: ["Instant liquidity","Govt-grade RWA backing","Daily yield"],
  },
  {
    id: "rwa",
    icon: "🏗️",
    name: "RWA Tokenization",
    desc: "Tokenize land, property, or commodity assets",
    apy: "18.0%",
    minStake: "1,000 KAI",
    color: "#F97316",
    features: ["Legal NFT wrapper","On-chain verification","Secondary market trading"],
  },
];

const INSURANCE_POOLS = [
  {
    id: "crop",
    icon: "🌾",
    name: "Community Crop Insurance",
    desc: "Protect against climate/weather crop loss",
    apy: "8.5%",
    minStake: "100 KAI",
    color: "#EAB308",
    features: ["Parametric weather triggers", "Instant payouts", "Community pooled risk"],
  },
  {
    id: "forest",
    icon: "🌲",
    name: "Forest Asset Protection",
    desc: "Cover for tokenized forest hectares",
    apy: "10.2%",
    minStake: "500 KAI",
    color: "#22C55E",
    features: ["Wildfire protection", "Illegal logging cover", "Satellite verified"],
  },
  {
    id: "medical",
    icon: "🏥",
    name: "Medical/Emergency Pool",
    desc: "Community health emergency coverage",
    apy: "5.0%",
    minStake: "50 KAI",
    color: "#EF4444",
    features: ["DAO approved claims", "Fast medical dispersal", "Subsidized premiums"],
  },
];

export default function SecuritiesPage() {
  const [activeTab, setActiveTab] = useState<"Securities" | "Insurance">("Securities");
  const [active, setActive] = useState<string | null>(null);
  const [stakeAmt, setStakeAmt] = useState("");
  const [showClaimForm, setShowClaimForm] = useState(false);

  const currentList = activeTab === "Securities" ? SECURITIES : INSURANCE_POOLS;

  return (
    <main style={{ padding:"16px 16px 90px", display:"flex", flexDirection:"column", gap:16 }}>

      <div style={{ paddingTop:32 }}>
        <h1 style={{ fontSize:24, fontWeight:900, color:"#fff", margin:0 }}>🏛️ Securities & Savings</h1>
        <p style={{ fontSize:11, color:"rgba(255,255,255,0.5)", margin:"4px 0 0" }}>
          Trust · Pension · MMF · Real World Assets · Insurance
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 8, background: "rgba(0,0,0,0.2)", padding: 4, borderRadius: 12 }}>
        {(["Securities", "Insurance"] as const).map(tab => (
          <button
            key={tab}
            onClick={() => { setActiveTab(tab); setActive(null); setShowClaimForm(false); }}
            style={{
              flex: 1, padding: "8px 0", borderRadius: 8, fontSize: 13, fontWeight: 700,
              color: activeTab === tab ? "#121212" : "#fff",
              background: activeTab === tab ? "#FFD700" : "transparent",
              transition: "all 0.2s"
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Regulatory badge */}
      <div style={{
        display:"flex", alignItems:"center", gap:10, padding:"12px 14px", borderRadius:14,
        background:"rgba(34,197,94,0.08)", border:"1px solid rgba(34,197,94,0.25)",
      }}>
        <Shield size={18} color="#22C55E" />
        <div>
          <p style={{ fontSize:11, fontWeight:700, color:"#22C55E", margin:0 }}>
            Regulated · Hedera Schedule Service Enforced
          </p>
          <p style={{ fontSize:10, color:"rgba(255,255,255,0.4)", margin:"2px 0 0" }}>
            Smart contracts audited · KYC optional (testnet)
          </p>
        </div>
      </div>

      {/* Items List */}
      <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
        {currentList.map(s => (
          <div key={s.id}>
            <div className="glass" onClick={() => { setActive(active === s.id ? null : s.id); setShowClaimForm(false); }}
              style={{
                padding:18, borderRadius:20, cursor:"pointer",
                border: active === s.id ? `1px solid ${s.color}60` : "1px solid rgba(255,255,255,0.1)",
                transition:"all 0.2s ease",
                background: active === s.id ? `${s.color}10` : "rgba(255,255,255,0.04)",
              }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
                <div style={{ display:"flex", alignItems:"center", gap:12 }}>
                  <div style={{
                    width:48, height:48, borderRadius:14, fontSize:24,
                    background:`${s.color}20`, border:`1px solid ${s.color}40`,
                    display:"flex", alignItems:"center", justifyContent:"center",
                  }}>{s.icon}</div>
                  <div>
                    <p style={{ fontSize:14, fontWeight:800, color:"#fff", margin:0 }}>{s.name}</p>
                    <p style={{ fontSize:10, color:"rgba(255,255,255,0.45)", margin:"3px 0 0" }}>{s.desc}</p>
                  </div>
                </div>
                <div style={{ textAlign:"right", flexShrink:0, marginLeft:8 }}>
                  <p style={{ fontSize:18, fontWeight:900, color:"#22C55E", margin:0 }}>{s.apy}</p>
                  <p style={{ fontSize:9, color:"rgba(255,255,255,0.35)", margin:0 }}>APY</p>
                </div>
              </div>

              {active === s.id && !showClaimForm && (
                <div style={{ marginTop:14 }}>
                  <div style={{ marginBottom:12 }}>
                    {s.features.map((f,i) => (
                      <div key={i} style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
                        <div style={{ width:5, height:5, borderRadius:"50%", background:s.color, flexShrink:0 }} />
                        <span style={{ fontSize:11, color:"rgba(255,255,255,0.6)" }}>{f}</span>
                      </div>
                    ))}
                  </div>
                  <div style={{ display:"flex", gap:8, alignItems:"center", marginTop: 14 }}>
                    <input value={stakeAmt} onChange={e=>setStakeAmt(e.target.value)} onClick={(e) => e.stopPropagation()}
                      type="number" placeholder={`Min ${s.minStake}`}
                      style={{
                        flex:1, background:"rgba(0,0,0,0.3)", border:"1px solid rgba(255,255,255,0.1)",
                        borderRadius:12, padding:"10px 14px", fontSize:13, color:"#fff", outline:"none",
                        fontFamily:"Inter, sans-serif",
                      }} />
                    <button onClick={(e) => e.stopPropagation()} style={{
                      background:`linear-gradient(135deg,${s.color},${s.color}bb)`,
                      color: s.color === "#FFD700" || s.color === "#EAB308" || s.color === "#22C55E" ? "#1B4332" : "#fff",
                      fontWeight:800, fontSize:13, padding:"10px 20px", borderRadius:12,
                      border:"none", cursor:"pointer", fontFamily:"Inter, sans-serif",
                    }}>
                      Deposit
                    </button>
                  </div>
                  {activeTab === "Insurance" && (
                     <button onClick={(e) => { e.stopPropagation(); setShowClaimForm(true); }} style={{
                        width: "100%", marginTop: 10, padding: 10, borderRadius: 12,
                        background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)",
                        color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer"
                     }}>
                        Submit a Claim
                     </button>
                  )}
                </div>
              )}

              {active === s.id && showClaimForm && (
                <div style={{ marginTop:14 }} onClick={(e) => e.stopPropagation()}>
                    <p style={{ fontSize:13, fontWeight:800, color:"#fff", marginBottom:10 }}>Submit {s.name} Claim</p>
                    <textarea 
                        placeholder="Describe your claim (e.g., date of incident, severity, location)..."
                        style={{
                            width: "100%", background:"rgba(0,0,0,0.3)", border:"1px solid rgba(255,255,255,0.1)",
                            borderRadius:12, padding:"10px 14px", fontSize:13, color:"#fff", outline:"none",
                            fontFamily:"Inter, sans-serif", minHeight: 80, resize: "none", marginBottom: 10
                        }}
                    />
                    <div style={{ display: "flex", gap: 10 }}>
                        <button onClick={(e) => { e.stopPropagation(); setShowClaimForm(false); }} style={{
                            flex: 1, padding: 10, borderRadius: 12, background: "rgba(255,255,255,0.1)",
                            color: "#fff", fontSize: 13, fontWeight: 700, cursor: "pointer", border: "none"
                        }}>
                            Cancel
                        </button>
                        <button style={{
                            flex: 1, padding: 10, borderRadius: 12, background: s.color,
                            color: s.color === "#EAB308" || s.color === "#22C55E" ? "#1B4332" : "#fff",
                            fontSize: 13, fontWeight: 800, cursor: "pointer", border: "none"
                        }}>
                            Submit via DAO
                        </button>
                    </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Portfolio Summary */}
      <div className="glass" style={{ padding:16, borderRadius:18 }}>
        <p style={{ fontSize:12, fontWeight:700, color:"rgba(255,255,255,0.6)", margin:"0 0 10px" }}>
          📊 My Portfolio
        </p>
        <div style={{ display:"flex", gap:10 }}>
          {[
            { l:"Invested", v:"$0.00",   c:"#FFD700" },
            { l:"Est. Yield", v:"$0.00", c:"#22C55E" },
            { l:"Lock/Cover", v:"Active",  c:"#A78BFA" },
          ].map(s => (
            <div key={s.l} style={{ flex:1, background:"rgba(255,255,255,0.04)", borderRadius:10, padding:"8px 6px", textAlign:"center" }}>
              <p style={{ fontSize:9, color:"rgba(255,255,255,0.4)", margin:"0 0 3px", fontWeight:700 }}>{s.l}</p>
              <p style={{ fontSize:14, fontWeight:900, color:s.c, margin:0 }}>{s.v}</p>
            </div>
          ))}
        </div>
      </div>

    </main>
  );
}

