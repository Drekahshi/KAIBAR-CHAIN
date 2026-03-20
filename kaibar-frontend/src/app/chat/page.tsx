"use client";
import { useState, useCallback, useEffect, useRef } from "react";
import { Bot, Send as SendIcon, Zap, BarChart2, TrendingUp, Shield, Volume2, VolumeX, BrainCircuit } from "lucide-react";
import MicButton from "@/components/ui/MicButton";

const SYSTEM_MSGS = [
  "🌿 Hello! I'm KAI, your HCS-10 AI Advisor powered by Hedera. Ask me about vaults, portfolio analysis, or execute payments. I can also connect to Bonzo Finance data.",
];

const QUICK_PROMPTS = [
  "Ecosystem Status 🌐",
  "Best vault APY right now?",
  "Analyze my portfolio",
  "What is x402 payment?",
  "Show HBAR/YToken price",
  "Top Bonzo vault pick",
];

interface Msg { role: "ai" | "user"; text: string; agent?: string; emoji?: string; }

export default function ChatPage() {
  const [messages, setMessages] = useState<Msg[]>([{ role:"ai", text: SYSTEM_MSGS[0], agent: "Agent KAI", emoji: "🤖" }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior:"smooth" }); }, [messages]);

  const onTranscript = useCallback((text: string) => setInput(text), []);

  // Auto-send after mic stops (fires on final STT result)
  const onFinalTranscript = useCallback((text: string) => {
    setInput(text);
    send(text);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const speak = (text: string) => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const cleanText = text.replace(/\*\*(.*?)\*\*/g, "$1").replace(/### (.*?)/g, "$1").replace(/`(.*?)`/g, "$1");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    const voices = window.speechSynthesis.getVoices();
    const voice = voices.find(v => v.name.includes("Google") && v.lang.startsWith("en")) || voices.find(v => v.lang.startsWith("en")) || voices[0];
    if (voice) utterance.voice = voice;
    window.speechSynthesis.speak(utterance);
  };

  const send = async (text?: string) => {
    const msg = text ?? input.trim();
    if (!msg || loading) return;

    setMessages(p => [...p, { role:"user", text: msg }]);
    setInput("");
    setLoading(true);

    try {
      // First try native Next.js -> Ollama connection
      let res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });

      // Fallback to Python backend if Next.js route fails
      if (!res.ok) {
        console.warn("Next.js Ollama route failed, falling back to Python API on port 8000...");
        res = await fetch("http://localhost:8000/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: msg }),
        });
      }

      if (!res.ok) throw new Error("Both Next.js and Python backend connections failed");

      const data = await res.json();
      const aiText = data.text || "I didn't get a clear response.";
      const newMsg = { 
        role: "ai" as const, 
        text: aiText,
        agent: data.agent || "Agent KAI",
        emoji: data.emoji || "🤖"
      };
      setMessages(p => [...p, newMsg]);

      // Auto-TTS: always speak when voice is on
      if (isVoiceEnabled) speak(aiText);

    } catch (err) {
      console.error(err);
      const errorMsg = "⚠️ **Connection Error.** Please make sure the local Ollama (qwen:0.5b) or Python backend is running.";
      setMessages(p => [...p, { role: "ai", text: errorMsg, agent: "System", emoji: "❌" }]);
      if (isVoiceEnabled) speak("Connection error. Please check the backend.");
    } finally {
      setLoading(false);
    }
  };

  const premiumPrompt = () => {
    send("⚡ Premium AI Analysis: Give me a deep market insight on KAI ecosystem.");
  };

  return (
    <main style={{ display:"flex", flexDirection:"column", height:"100dvh", paddingBottom:70 }}>

      {/* Header */}
      <div style={{ padding:"40px 16px 12px", display:"flex", alignItems:"center", gap:12, flexShrink:0 }}>
        <div className="float" style={{ position:"relative" }}>
          <div className="gold-glow" style={{
            width:48, height:48, borderRadius:"50%",
            background:"linear-gradient(135deg,#FFD700,#F97316)",
            display:"flex", alignItems:"center", justifyContent:"center",
          }}>
            <Bot size={24} color="#1B4332" />
          </div>
          <div style={{
            position:"absolute", bottom:-2, right:-2, width:14, height:14,
            borderRadius:"50%", background:"#22C55E", border:"2px solid #1B4332",
          }} />
        </div>
        <div style={{ flex:1 }}>
          <p style={{ fontSize:17, fontWeight:900, color:"#fff", margin:0 }}>KAI Agent</p>
          <p style={{ fontSize:10, color:"#22C55E", margin:0, fontWeight:700 }}>
            ● HCS-10 Open Conversation · Hedera Testnet
          </p>
        </div>
        <div style={{ display:"flex", gap:6 }}>
          <button onClick={() => setIsVoiceEnabled(!isVoiceEnabled)} style={{
            width:32, height:32, borderRadius:8, background: isVoiceEnabled ? "rgba(255,215,0,0.15)" : "rgba(255,255,255,0.06)",
            border: isVoiceEnabled ? "1px solid rgba(255,215,0,0.4)" : "1px solid rgba(255,255,255,0.1)", 
            display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer",
            transition: "all 0.2s",
          }}>
            {isVoiceEnabled ? <Volume2 size={16} color="#FFD700" /> : <VolumeX size={16} color="rgba(255,255,255,0.4)" />}
          </button>
          {[BarChart2, TrendingUp, Shield].map((Icon,i) => (
            <button key={i} style={{
              width:32, height:32, borderRadius:8, background:"rgba(255,255,255,0.06)",
              border:"1px solid rgba(255,255,255,0.1)", display:"flex", alignItems:"center",
              justifyContent:"center", cursor:"pointer",
            }}>
              <Icon size={14} color="rgba(255,255,255,0.5)" />
            </button>
          ))}
        </div>
      </div>

      {/* Quick prompts */}
      <div style={{ padding:"0 16px 10px", display:"flex", gap:6, overflowX:"auto", flexShrink:0 }}>
        {QUICK_PROMPTS.map(p => (
          <button key={p} onClick={() => send(p)} style={{
            flexShrink:0, background:"rgba(255,215,0,0.1)", border:"1px solid rgba(255,215,0,0.25)",
            borderRadius:999, padding:"6px 12px", fontSize:11, fontWeight:600, color:"#FFD700",
            cursor:"pointer", whiteSpace:"nowrap", fontFamily:"Inter, sans-serif",
          }}>{p}</button>
        ))}
      </div>

      {/* Messages */}
      <div style={{ flex:1, overflowY:"auto", padding:"0 16px", display:"flex", flexDirection:"column", gap:12 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display:"flex", justifyContent: m.role==="user" ? "flex-end" : "flex-start" }}>
            {m.role === "ai" && (
              <div style={{
                width:28, height:28, borderRadius:"50%",
                background:"linear-gradient(135deg,#FFD700,#F97316)",
                display:"flex", alignItems:"center", justifyContent:"center",
                flexShrink:0, marginRight:8, alignSelf:"flex-end",
              }}>
                <span style={{ fontSize: 14 }}>{m.emoji || "🤖"}</span>
              </div>
            )}
            <div style={{
              maxWidth:"78%", padding:"12px 16px", borderRadius:18,
              fontSize:13, lineHeight:1.5,
              ...(m.role === "ai"
                ? {
                    background:"rgba(255,255,255,0.06)",
                    border:"1px solid rgba(255,215,0,0.2)", color:"#fff",
                    borderBottomLeftRadius:4,
                  }
                : {
                    background:"linear-gradient(135deg,#FFD700,#F97316)",
                    color:"#1B4332", fontWeight:600,
                    borderBottomRightRadius:4,
                    boxShadow:"0 4px 16px rgba(255,215,0,0.3)",
                  }),
            }}>
              {m.role === "ai" && (
                <div style={{ fontSize: 10, color: "#FFD700", fontWeight: 700, marginBottom: 4 }}>
                  {m.agent?.toUpperCase() || "AGENT KAI"}
                </div>
              )}
              {m.text.split("\n").map((line, li) => (
                <span key={li}>
                  {line.split("**").map((t, ti) =>
                    ti % 2 === 1
                      ? <strong key={ti}>{t}</strong>
                      : <span key={ti}>{t}</span>
                  )}
                  {li < m.text.split("\n").length - 1 && <br />}
                </span>
              ))}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <div style={{
              width:28, height:28, borderRadius:"50%",
              background:"linear-gradient(135deg,#FFD700,#F97316)",
              display:"flex", alignItems:"center", justifyContent:"center",
            }}>
              <Bot size={14} color="#1B4332" />
            </div>
            <div style={{ display:"flex", gap:4, alignItems:"center", padding:"12px 16px",
              background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,215,0,0.2)",
              borderRadius:18, borderBottomLeftRadius:4,
            }}>
              {[0,1,2].map(d => (
                <div key={d} style={{
                  width:6, height:6, borderRadius:"50%", background:"#FFD700",
                  animation:`pulse-gold ${0.8 + d*0.15}s ease-in-out infinite`,
                }} />
              ))}
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Premium prompt + Agent KAI Mode */}
      <div style={{ padding:"10px 16px 8px", flexShrink:0, display:"flex", gap:8 }}>
        <button onClick={premiumPrompt} style={{
          flex:1, background:"linear-gradient(135deg,#FFD700,#F97316)",
          color:"#1B4332", fontWeight:800, fontSize:12, padding:"10px", borderRadius:14,
          border:"none", cursor:"pointer", fontFamily:"Inter, sans-serif",
          display:"flex", alignItems:"center", justifyContent:"center", gap:8,
          boxShadow:"0 0 20px rgba(255,215,0,0.3)",
        }}>
          <Zap size={14} />✨ Premium AI Analysis
        </button>

        {/* Agent KAI Mode — opens kai_bot interface */}
        <a
          href="/kai-agent/index.html"
          target="_blank"
          rel="noopener noreferrer"
          title="Open Agent KAI Mode (kai_bot interface)"
          style={{
            flexShrink:0,
            background:"linear-gradient(135deg,#7C3AED,#4F46E5)",
            color:"#fff", fontWeight:800, fontSize:11, padding:"10px 14px", borderRadius:14,
            border:"none", cursor:"pointer", fontFamily:"Inter, sans-serif",
            display:"flex", alignItems:"center", justifyContent:"center", gap:6,
            boxShadow:"0 0 20px rgba(124,58,237,0.5)",
            textDecoration:"none",
            whiteSpace:"nowrap",
          }}>
          <BrainCircuit size={14} />
          🤖 Agent KAI
        </a>
      </div>

      {/* Input row */}
      <div style={{ padding:"0 16px 10px", display:"flex", alignItems:"center", gap:8, flexShrink:0 }}>
        <MicButton onTranscript={onTranscript} onFinalTranscript={onFinalTranscript} size="md" />
        <input value={input} onChange={e=>setInput(e.target.value)}
          onKeyDown={e=>e.key==="Enter" && send()}
          placeholder="Ask KAI about vaults, prices, portfolio…"
          style={{
            flex:1, background:"rgba(255,255,255,0.06)",
            border:"1px solid rgba(255,215,0,0.2)",
            borderRadius:14, padding:"12px 16px", fontSize:13, color:"#fff", outline:"none",
            fontFamily:"Inter, sans-serif", transition:"border-color 0.2s",
          }} />
        <button onClick={() => send()}
          style={{
            width:44, height:44, borderRadius:12,
            background:"linear-gradient(135deg,#FFD700,#F97316)",
            display:"flex", alignItems:"center", justifyContent:"center",
            border:"none", cursor:"pointer", flexShrink:0,
            boxShadow:"0 0 16px rgba(255,215,0,0.4)",
          }}>
          <SendIcon size={18} color="#1B4332" strokeWidth={3} />
        </button>
      </div>

    </main>
  );
}
