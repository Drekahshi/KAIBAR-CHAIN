"use client";
import { useState } from "react";
import { QrCode, Phone, Zap, Send as SendIcon, Copy, Check } from "lucide-react";
import RealisticQR from "@/components/ui/RealisticQR";

type Tab = "qr" | "mpesa" | "x402" | "send";

const TABS: { id: Tab; label: string; emoji: string }[] = [
  { id:"qr",    label:"QR Pay",   emoji:"📱" },
  { id:"mpesa", label:"M-Pesa",   emoji:"💚" },
  { id:"x402",  label:"x402",     emoji:"⚡" },
  { id:"send",  label:"Send",     emoji:"↗️" },
];

export default function PayPage() {
  const [tab, setTab] = useState<Tab>("qr");
  const [amount, setAmount] = useState("");
  const [phone, setPhone] = useState("");
  const [toAddr, setToAddr] = useState("");
  const [copied, setCopied] = useState(false);
  const [x402Step, setX402Step] = useState(0);

  const myAddress = "0.0.4872931";

  const copy = () => {
    navigator.clipboard.writeText(myAddress).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const simulateX402 = async () => {
    for (let i = 1; i <= 3; i++) {
      await new Promise(r => setTimeout(r, 800));
      setX402Step(i);
    }
  };

  return (
    <main style={{ padding:"16px 16px 90px", display:"flex", flexDirection:"column", gap:16 }}>

      <div style={{ paddingTop:32 }}>
        <h1 style={{ fontSize:24, fontWeight:900, color:"#fff", margin:0 }}>💳 Payments</h1>
        <p style={{ fontSize:11, color:"rgba(255,255,255,0.5)", margin:"4px 0 0" }}>
          QR · M-Pesa · x402 Agent · Direct Send
        </p>
      </div>

      {/* Tab bar */}
      <div style={{ display:"flex", gap:6 }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            flex:1, padding:"10px 4px", borderRadius:12, border:"none", cursor:"pointer",
            background: tab === t.id ? "linear-gradient(135deg,#FFD700,#F97316)" : "rgba(255,255,255,0.06)",
            color: tab === t.id ? "#1B4332" : "rgba(255,255,255,0.5)",
            fontWeight:700, fontSize:11, fontFamily:"Inter, sans-serif",
            display:"flex", flexDirection:"column", alignItems:"center", gap:2,
          }}>
            <span>{t.emoji}</span>
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      {/* ── QR CODE ── */}
      {tab === "qr" && (
        <div className="glass" style={{ padding:24, borderRadius:24, display:"flex", flexDirection:"column", alignItems:"center", gap:16 }}>
          <p style={{ fontSize:13, fontWeight:700, color:"rgba(255,255,255,0.6)", margin:0 }}>
            Your KAIBAR QR Code
          </p>
          <div style={{
            background:"#fff", padding:12, borderRadius:16,
            border:"2px solid rgba(255,215,0,0.3)",
            boxShadow:"0 0 40px rgba(255,215,0,0.15)",
          }}>
            <RealisticQR value={myAddress} size={180} label="" />
          </div>
          <div style={{ textAlign:"center" }}>
            <p style={{ fontSize:11, color:"rgba(255,255,255,0.4)", margin:"0 0 4px" }}>Account ID</p>
            <p style={{ fontFamily:"monospace", fontSize:14, fontWeight:700, color:"#FFD700", margin:0 }}>
              {myAddress}
            </p>
          </div>
          <button onClick={copy}
            style={{
              display:"flex", alignItems:"center", gap:8, padding:"10px 20px",
              borderRadius:12, border:"1px solid rgba(255,215,0,0.3)",
              background:"rgba(255,215,0,0.08)", color:"#FFD700",
              fontWeight:700, fontSize:13, cursor:"pointer", fontFamily:"Inter, sans-serif",
            }}>
            {copied ? <Check size={16} color="#22C55E" /> : <Copy size={16} />}
            {copied ? "Copied!" : "Copy Address"}
          </button>
          <div style={{ display:"flex", gap:8, width:"100%" }}>
            <input value={amount} onChange={e=>setAmount(e.target.value)}
              type="number" placeholder="Request amount (KAI)"
              style={{ flex:1, background:"rgba(0,0,0,0.3)", border:"1px solid rgba(255,255,255,0.1)",
                borderRadius:12, padding:"10px 14px", fontSize:13, color:"#fff", outline:"none",
                fontFamily:"Inter, sans-serif",
              }} />
            <button className="btn-gold" style={{ padding:"10px 16px", borderRadius:12, fontSize:13 }}>
              Share QR
            </button>
          </div>
        </div>
      )}

      {/* ── M-PESA ── */}
      {tab === "mpesa" && (
        <div className="glass" style={{ padding:20, borderRadius:22, border:"1px solid rgba(34,197,94,0.3)" }}>
          <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:14 }}>
            <div style={{
              width:44, height:44, borderRadius:12, fontSize:24,
              background:"rgba(34,197,94,0.15)", display:"flex", alignItems:"center", justifyContent:"center",
            }}>💚</div>
            <div>
              <p style={{ fontSize:14, fontWeight:800, color:"#22C55E", margin:0 }}>M-Pesa Integration</p>
              <p style={{ fontSize:10, color:"rgba(255,255,255,0.4)", margin:"2px 0 0" }}>
                KES ↔ KAI · Powered by Hedera HBAR Bridge
              </p>
            </div>
          </div>

          <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
            <input value={phone} onChange={e=>setPhone(e.target.value)}
              type="tel" placeholder="M-Pesa number (e.g. 0712345678)"
              style={{ background:"rgba(0,0,0,0.3)", border:"1px solid rgba(34,197,94,0.3)",
                borderRadius:12, padding:"12px 16px", fontSize:13, color:"#fff", outline:"none",
                fontFamily:"Inter, sans-serif",
              }} />
            <input value={amount} onChange={e=>setAmount(e.target.value)}
              type="number" placeholder="Amount (KES)"
              style={{ background:"rgba(0,0,0,0.3)", border:"1px solid rgba(34,197,94,0.3)",
                borderRadius:12, padding:"12px 16px", fontSize:13, color:"#fff", outline:"none",
                fontFamily:"Inter, sans-serif",
              }} />
            {amount && (
              <div style={{ background:"rgba(34,197,94,0.08)", borderRadius:12, padding:"10px 14px",
                border:"1px solid rgba(34,197,94,0.2)",
              }}>
                <p style={{ fontSize:11, color:"rgba(255,255,255,0.5)", margin:"0 0 4px" }}>You receive approximately:</p>
                <p style={{ fontSize:18, fontWeight:900, color:"#22C55E", margin:0 }}>
                  {(parseFloat(amount || "0") / 130).toFixed(2)} KAI
                </p>
                <p style={{ fontSize:10, color:"rgba(255,255,255,0.3)", margin:"3px 0 0" }}>
                  Rate: 130 KES = 1 KAI · 0.5% fee
                </p>
              </div>
            )}
            <button style={{
              background:"linear-gradient(135deg,#22C55E,#16A34A)",
              color:"#fff", fontWeight:700, fontSize:13, padding:"12px", borderRadius:12,
              border:"none", cursor:"pointer", fontFamily:"Inter, sans-serif",
            }}>
              💚 Pay with M-Pesa
            </button>
          </div>
        </div>
      )}

      {/* ── x402 AGENT ── */}
      {tab === "x402" && (
        <div className="glass" style={{ padding:20, borderRadius:22, border:"1px solid rgba(167,139,250,0.3)" }}>
          <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:14 }}>
            <div style={{ width:44, height:44, borderRadius:12, fontSize:24,
              background:"rgba(167,139,250,0.15)", display:"flex", alignItems:"center", justifyContent:"center",
            }}>⚡</div>
            <div>
              <p style={{ fontSize:14, fontWeight:800, color:"#A78BFA", margin:0 }}>x402 Agentic Wallet</p>
              <p style={{ fontSize:10, color:"rgba(255,255,255,0.4)", margin:"2px 0 0" }}>
                HTTP 402 micropayment · AI-executed on Hedera
              </p>
            </div>
          </div>

          {/* Steps */}
          <div style={{ display:"flex", flexDirection:"column", gap:8, marginBottom:14 }}>
            {[
              { step:1, label:"Initiate x402 Request",    done: x402Step >= 1 },
              { step:2, label:"AI Agent Signs Transaction",done: x402Step >= 2 },
              { step:3, label:"Payment Confirmed on-chain",done: x402Step >= 3 },
            ].map(s => (
              <div key={s.step} style={{
                display:"flex", alignItems:"center", gap:10, padding:"8px 12px", borderRadius:10,
                background: s.done ? "rgba(34,197,94,0.08)" : "rgba(255,255,255,0.04)",
                border:`1px solid ${s.done ? "rgba(34,197,94,0.3)" : "rgba(255,255,255,0.08)"}`,
              }}>
                <div style={{
                  width:22, height:22, borderRadius:"50%", flexShrink:0,
                  background: s.done ? "#22C55E" : "rgba(255,255,255,0.1)",
                  display:"flex", alignItems:"center", justifyContent:"center",
                  fontSize:11, fontWeight:900, color: s.done ? "#fff" : "rgba(255,255,255,0.3)",
                }}>
                  {s.done ? "✓" : s.step}
                </div>
                <span style={{ fontSize:12, color: s.done ? "#22C55E" : "rgba(255,255,255,0.5)", fontWeight:600 }}>
                  {s.label}
                </span>
              </div>
            ))}
          </div>

          <input value={amount} onChange={e=>setAmount(e.target.value)}
            type="number" placeholder="Micropayment amount (KAI)"
            style={{ width:"100%", background:"rgba(0,0,0,0.3)", border:"1px solid rgba(167,139,250,0.3)",
              borderRadius:12, padding:"12px 16px", fontSize:13, color:"#fff", outline:"none",
              fontFamily:"Inter, sans-serif", marginBottom:10, boxSizing:"border-box",
            }} />
          <button onClick={simulateX402}
            disabled={x402Step > 0}
            style={{
              width:"100%", background: x402Step === 3
                ? "linear-gradient(135deg,#22C55E,#16A34A)"
                : "linear-gradient(135deg,#A78BFA,#7C3AED)",
              color:"#fff", fontWeight:700, fontSize:13, padding:"12px", borderRadius:12,
              border:"none", cursor: x402Step > 0 ? "not-allowed" : "pointer",
              fontFamily:"Inter, sans-serif",
            }}>
            {x402Step === 3 ? "✅ Payment Complete" : x402Step > 0 ? "⏳ Processing…" : "⚡ Execute x402 Payment"}
          </button>
        </div>
      )}

      {/* ── SEND ── */}
      {tab === "send" && (
        <div className="glass" style={{ padding:20, borderRadius:22 }}>
          <p style={{ fontSize:14, fontWeight:800, color:"#FFD700", margin:"0 0 14px" }}>↗️ Send KAIBAR Assets</p>
          <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
            <input value={toAddr} onChange={e=>setToAddr(e.target.value)}
              placeholder="To: @username, 0.0.xxxxx, or 0xhex"
              style={{ background:"rgba(0,0,0,0.3)", border:"1px solid rgba(255,255,255,0.1)",
                borderRadius:12, padding:"12px 16px", fontSize:13, color:"#fff", outline:"none",
                fontFamily:"Inter, sans-serif",
              }} />
            <input value={amount} onChange={e=>setAmount(e.target.value)}
              type="number" placeholder="Amount"
              style={{ background:"rgba(0,0,0,0.3)", border:"1px solid rgba(255,255,255,0.1)",
                borderRadius:12, padding:"12px 16px", fontSize:13, color:"#fff", outline:"none",
                fontFamily:"Inter, sans-serif",
              }} />
            {["KAI","YToken","HBAR","GAMI"].map(t => (
              <div key={t} style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
              </div>
            ))}
            <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
              {["KAI","YToken","HBAR","GAMI"].map(t => (
                <button key={t} style={{
                  padding:"6px 14px", borderRadius:999, fontSize:12, fontWeight:700, cursor:"pointer",
                  background:"rgba(255,215,0,0.1)", border:"1px solid rgba(255,215,0,0.3)",
                  color:"#FFD700", fontFamily:"Inter, sans-serif",
                }}>{t}</button>
              ))}
            </div>
            <button className="btn-gold" style={{ padding:"12px", borderRadius:12, fontSize:13 }}>
              <SendIcon size={14} style={{display:"inline",marginRight:6}} />
              Send Tokens
            </button>
          </div>
        </div>
      )}

    </main>
  );
}
