"use client";
import { useState, useRef } from "react";
import Link from "next/link";
import { ArrowLeft, Upload, Receipt, Package, Banknote, Bot, CheckCircle2, History } from "lucide-react";
import { useKaibarStore } from "@/store/useKaibarStore";

export default function SMEDashboard() {
  const { connected, accountId } = useKaibarStore();
  
  // Digitize Cash State
  const [cashAmount, setCashAmount] = useState("");
  const [description, setDescription] = useState("");
  const [receiptImage, setReceiptImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Agents State
  const [aiRestock, setAiRestock] = useState(false);
  const [x402Payments, setX402Payments] = useState(false);
  
  // Mock Ledger Data
  const mockLedger = [
    { id: 1, type: "Digitized Cash", amount: "+500 YToken", date: "2026-03-17 08:30", status: "Completed" },
    { id: 2, type: "Inventory Restock", amount: "-150 YToken", date: "2026-03-16 14:20", status: "Agent Executed" },
    { id: 3, type: "Flash Loan Repayment", amount: "-2000 HBAR", date: "2026-03-15 09:15", status: "Completed" },
  ];

  // Mock Inventory Data
  const mockInventory = [
    { item: "Maize Flour (Bales)", stock: 12, status: "Low", replenish: true },
    { item: "Cooking Oil (Litres)", stock: 45, status: "Optimal", replenish: false },
    { item: "Sugar (Sacks)", stock: 5, status: "Critical", replenish: true },
  ];

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Create a fake local URL for preview
      const url = URL.createObjectURL(file);
      setReceiptImage(url);
    }
  };

  const handleDigitize = () => {
    if (!cashAmount || !description) return alert("Please fill details");
    alert(`Digitizing ${cashAmount} from cash record: ${description}`);
    setCashAmount("");
    setDescription("");
    setReceiptImage(null);
  };

  return (
    <main style={{ paddingBottom: 80 }}>
      {/* ── HEADER ── */}
      <div style={{ padding: "20px 16px", display: "flex", alignItems: "center", gap: 16 }}>
        <Link href="/" style={{
          width: 40, height: 40, borderRadius: "50%", background: "rgba(255,255,255,0.05)",
          display: "flex", alignItems: "center", justifyContent: "center", textDecoration: "none"
        }}>
          <ArrowLeft color="#fff" size={20} />
        </Link>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 900, margin: 0, color: "#3B82F6" }}>SME Hub</h1>
          <p style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", margin: 0 }}>Business Operations & AI Agents</p>
        </div>
      </div>

      {/* ── WALLET STATUS ── */}
      <div style={{ margin: "0 16px 20px" }}>
        {connected ? (
          <div className="glass" style={{ padding: 12, borderRadius: 12, display: "flex", justifyContent: "space-between", alignItems: "center", border: "1px solid rgba(34,197,94,0.3)" }}>
            <span style={{ fontSize: 12, color: "rgba(255,255,255,0.6)" }}>Connected Wallet</span>
            <span style={{ fontSize: 13, fontWeight: 700, color: "#22C55E" }}>{accountId.substring(0, 10)}...</span>
          </div>
        ) : (
          <div className="glass" style={{ padding: 12, borderRadius: 12, textAlign: "center", border: "1px solid rgba(249,115,22,0.3)" }}>
            <span style={{ fontSize: 13, color: "#F97316" }}>⚠️ Wallet not connected. Please connect on Home.</span>
          </div>
        )}
      </div>

      <div style={{ padding: "0 16px", display: "flex", flexDirection: "column", gap: 20 }}>
        
        {/* ── DIGITIZE CASH & INVOICES ── */}
        <section className="glass" style={{ padding: 20, borderRadius: 24, border: "1px solid rgba(59,130,246,0.3)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            <div style={{ padding: 8, borderRadius: 12, background: "rgba(59,130,246,0.1)" }}>
              <Receipt color="#3B82F6" size={20} />
            </div>
            <h2 style={{ fontSize: 16, fontWeight: 800, margin: 0 }}>Digitize Cash</h2>
          </div>
          <p style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginBottom: 16 }}>Record cash transactions and upload receipts to mint digital equivalents (YToken/HBAR).</p>
          
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <input 
              type="text" placeholder="Amount (e.g. 5000 KES)" 
              value={cashAmount} onChange={(e) => setCashAmount(e.target.value)}
              style={{ width: "100%", padding: 14, borderRadius: 12, border: "1px solid rgba(255,255,255,0.1)", background: "rgba(0,0,0,0.2)", color: "#fff", fontSize: 14, boxSizing: "border-box" }}
            />
            <input 
              type="text" placeholder="Description / Customer Name" 
              value={description} onChange={(e) => setDescription(e.target.value)}
              style={{ width: "100%", padding: 14, borderRadius: 12, border: "1px solid rgba(255,255,255,0.1)", background: "rgba(0,0,0,0.2)", color: "#fff", fontSize: 14, boxSizing: "border-box" }}
            />
            
            {/* Image Upload Area */}
            <div 
              onClick={() => fileInputRef.current?.click()}
              style={{ 
                border: "2px dashed rgba(59,130,246,0.4)", borderRadius: 12, padding: 20, 
                display: "flex", flexDirection: "column", alignItems: "center", cursor: "pointer",
                background: receiptImage ? "rgba(59,130,246,0.05)" : "transparent"
              }}>
              <input type="file" accept="image/*" ref={fileInputRef} onChange={handleImageUpload} style={{ display: "none" }} />
              {receiptImage ? (
                <>
                  <CheckCircle2 color="#22C55E" style={{ marginBottom: 8 }} />
                  <span style={{ fontSize: 12, color: "#22C55E", fontWeight: 600 }}>Image Attached</span>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={receiptImage} alt="Receipt" style={{ marginTop: 10, maxHeight: 60, borderRadius: 8, border: "1px solid rgba(255,255,255,0.2)" }} />
                </>
              ) : (
                <>
                  <Upload color="#3B82F6" style={{ marginBottom: 8 }} />
                  <span style={{ fontSize: 13, color: "#3B82F6", fontWeight: 600 }}>Upload Receipt Image</span>
                  <span style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", marginTop: 4 }}>Tap to open camera/gallery</span>
                </>
              )}
            </div>

            <button onClick={handleDigitize} style={{
              width: "100%", padding: 16, borderRadius: 12, border: "none",
              background: "linear-gradient(135deg, #3B82F6, #2563EB)", color: "#fff", fontWeight: 800, fontSize: 14,
              cursor: "pointer", marginTop: 4, boxShadow: "0 0 16px rgba(59,130,246,0.4)"
            }}>Secure & Digitize Entry</button>
          </div>
        </section>

        {/* ── WALLET LEDGER ── */}
        <section className="glass" style={{ padding: 20, borderRadius: 24, border: "1px solid rgba(167,139,250,0.3)" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ padding: 8, borderRadius: 12, background: "rgba(167,139,250,0.1)" }}>
                <History color="#A78BFA" size={20} />
              </div>
              <h2 style={{ fontSize: 16, fontWeight: 800, margin: 0 }}>Wallet Ledger</h2>
            </div>
            <span style={{ fontSize: 11, color: "rgba(255,255,255,0.4)" }}>Recent</span>
          </div>
          
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {mockLedger.map((tx) => (
              <div key={tx.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingBottom: 12, borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <div>
                  <p style={{ fontSize: 13, fontWeight: 600, margin: "0 0 4px" }}>{tx.type}</p>
                  <p style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", margin: 0 }}>{tx.date} • {tx.status}</p>
                </div>
                <span style={{ fontSize: 14, fontWeight: 800, color: tx.amount.startsWith("+") ? "#22C55E" : "#fff" }}>
                  {tx.amount}
                </span>
              </div>
            ))}
            
            <button style={{
              width: "100%", padding: "12px", borderRadius: "12px", border: "1px solid rgba(167,139,250,0.3)",
              background: "transparent", color: "#A78BFA", fontSize: "12px", fontWeight: 700, cursor: "pointer",
              marginTop: "4px"
            }}>View Full Ledger</button>
          </div>
        </section>

        {/* ── INVENTORY MANAGEMENT ── */}
        <section className="glass" style={{ padding: 20, borderRadius: 24, border: "1px solid rgba(249,115,22,0.3)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            <div style={{ padding: 8, borderRadius: 12, background: "rgba(249,115,22,0.1)" }}>
              <Package color="#F97316" size={20} />
            </div>
            <h2 style={{ fontSize: 16, fontWeight: 800, margin: 0 }}>Inventory Hub</h2>
          </div>
          
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {mockInventory.map((item, i) => (
              <div key={i} style={{ background: "rgba(0,0,0,0.2)", padding: 12, borderRadius: 12, display: "flex", justifyContent: "space-between", alignItems: "center", border: "1px solid rgba(255,255,255,0.05)" }}>
                <div>
                  <p style={{ fontSize: 13, fontWeight: 600, margin: "0 0 4px" }}>{item.item}</p>
                  <span style={{ 
                    fontSize: 9, padding: "2px 6px", borderRadius: 4, 
                    background: item.status === "Critical" ? "rgba(239,68,68,0.2)" : item.status === "Low" ? "rgba(249,115,22,0.2)" : "rgba(34,197,94,0.2)",
                    color: item.status === "Critical" ? "#EF4444" : item.status === "Low" ? "#F97316" : "#22C55E",
                    fontWeight: 700
                  }}>{item.status} Stock: {item.stock}</span>
                </div>
                {item.replenish && (
                  <button style={{ background: "rgba(249,115,22,0.1)", border: "1px solid rgba(249,115,22,0.3)", color: "#F97316", padding: "6px 12px", borderRadius: 8, fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
                    Restock
                  </button>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* ── AUTONOMOUS AGENTS (x402) ── */}
        <section className="glass" style={{ padding: 20, borderRadius: 24, border: "1px solid rgba(255,215,0,0.3)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            <div style={{ padding: 8, borderRadius: 12, background: "rgba(255,215,0,0.1)" }}>
              <Bot color="#FFD700" size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 800, margin: 0, color: "#FFD700" }}>Autonomous Agents</h2>
              <p style={{ fontSize: 10, color: "rgba(255,255,255,0.5)", margin: 0 }}>x402 Execution</p>
            </div>
          </div>
          
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(255,255,255,0.03)", padding: 14, borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
              <div>
                <p style={{ fontSize: 13, fontWeight: 600, margin: "0 0 4px" }}>AI Auto-Restock</p>
                <p style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", margin: 0 }}>Agent negotiates & buys when critical</p>
              </div>
              <button onClick={() => setAiRestock(!aiRestock)} style={{
                width: 44, height: 24, borderRadius: 12, position: "relative", cursor: "pointer", border: "none",
                background: aiRestock ? "linear-gradient(135deg, #FFD700, #F97316)" : "rgba(255,255,255,0.1)",
                transition: "background 0.3s", boxShadow: aiRestock ? "0 0 12px rgba(255,215,0,0.4)" : "none"
              }}>
                <div style={{
                  width: 18, height: 18, borderRadius: "50%", background: aiRestock ? "#000" : "#fff",
                  position: "absolute", top: 3, left: aiRestock ? 23 : 3, transition: "left 0.3s"
                }}/>
              </button>
            </div>
            
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(255,255,255,0.03)", padding: 14, borderRadius: 12, border: "1px solid rgba(255,255,255,0.05)" }}>
              <div>
                <p style={{ fontSize: 13, fontWeight: 600, margin: "0 0 4px" }}>x402 Micropayments</p>
                <p style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", margin: 0 }}>Pay API/Supplier fees autonomously</p>
              </div>
              <button onClick={() => setX402Payments(!x402Payments)} style={{
                width: 44, height: 24, borderRadius: 12, position: "relative", cursor: "pointer", border: "none",
                background: x402Payments ? "linear-gradient(135deg, #FFD700, #F97316)" : "rgba(255,255,255,0.1)",
                transition: "background 0.3s", boxShadow: x402Payments ? "0 0 12px rgba(255,215,0,0.4)" : "none"
              }}>
                <div style={{
                  width: 18, height: 18, borderRadius: "50%", background: x402Payments ? "#000" : "#fff",
                  position: "absolute", top: 3, left: x402Payments ? 23 : 3, transition: "left 0.3s"
                }}/>
              </button>
            </div>
          </div>
        </section>

        {/* ── LOANS & FLASH LOANS ── */}
        <section className="glass" style={{ padding: 20, borderRadius: 24, border: "1px solid rgba(220,38,38,0.3)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            <div style={{ padding: 8, borderRadius: 12, background: "rgba(220,38,38,0.1)" }}>
              <Banknote color="#EF4444" size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 800, margin: 0 }}>Flash Loans & Credit</h2>
              <p style={{ fontSize: 10, color: "rgba(255,255,255,0.5)", margin: 0 }}>Collateralize inventory for instant funds</p>
            </div>
          </div>
          
          <div style={{ background: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 12, border: "1px dashed rgba(239,68,68,0.3)", textAlign: "center" }}>
            <p style={{ fontSize: 12, color: "rgba(255,255,255,0.7)", margin: "0 0 12px" }}>Available Credit limit based on your Ledger</p>
            <h3 style={{ fontSize: 24, fontWeight: 900, color: "#fff", margin: "0 0 16px" }}>5,000 HBAR</h3>
            <div style={{ display: "flex", gap: 10 }}>
              <button style={{ flex: 1, padding: 12, borderRadius: 8, background: "rgba(239,68,68,0.2)", color: "#EF4444", border: "1px solid rgba(239,68,68,0.4)", fontWeight: 700, cursor: "pointer" }}>Request Loan</button>
              <button style={{ flex: 1, padding: 12, borderRadius: 8, background: "rgba(255,215,0,0.1)", color: "#FFD700", border: "1px solid rgba(255,215,0,0.4)", fontWeight: 700, cursor: "pointer" }}>Flash Loan</button>
            </div>
          </div>
        </section>

      </div>
    </main>
  );
}
