"use client";
import { useState } from "react";
import {
  Users, Leaf, Vote, Receipt, QrCode, Sprout, Landmark,
  TreePalm, Bug, TrendingUp, Briefcase, Store, ShoppingBag, MapPin, X,
} from "lucide-react";
import RealisticQR from "@/components/ui/RealisticQR";

/* ─── Community Group Data ──────────────────────────── */
interface CommunityGroup {
  name: string;
  icon: React.ReactNode;
  desc: string;
  members: number;
  color: string;
  accountId: string;
}

const GREEN_GROUPS: CommunityGroup[] = [
  { name: "Tree Seedling Nurseries", icon: <Sprout size={20}/>,      desc: "Seedling propagation & nursery sales",          members: 48,  color: "#22C55E", accountId: "0.0.5210010" },
  { name: "Ecotourism Ventures",     icon: <TreePalm size={20}/>,    desc: "Forest & wildlife eco-lodges & tours",          members: 23,  color: "#10B981", accountId: "0.0.5210020" },
  { name: "Beekeeping Cooperatives", icon: <Bug size={20}/>,         desc: "Honey, beeswax & pollination services",         members: 65,  color: "#F59E0B", accountId: "0.0.5210030" },
  { name: "Agroforestry Groups",     icon: <Leaf size={20}/>,        desc: "Intercropping timber, fruit & food crops",       members: 112, color: "#34D399", accountId: "0.0.5210040" },
  { name: "Impact Investors",        icon: <TrendingUp size={20}/>,  desc: "Community ESG & carbon-credit funding",          members: 17,  color: "#818CF8", accountId: "0.0.5210050" },
];

const SME_GROUPS: CommunityGroup[] = [
  { name: "SME Sole Proprietors",    icon: <Briefcase size={20}/>,   desc: "Registered SME micro-businesses",               members: 89,  color: "#FFD700", accountId: "0.0.5220010" },
  { name: "Mama Bonga Kiosks",       icon: <Store size={20}/>,       desc: "Roadside kiosk & mama bonga vendors",           members: 204, color: "#F97316", accountId: "0.0.5220020" },
  { name: "Market Traders",          icon: <ShoppingBag size={20}/>, desc: "Open-air market stall merchants",                members: 157, color: "#EAB308", accountId: "0.0.5220030" },
  { name: "Roadside Sellers",        icon: <MapPin size={20}/>,      desc: "Mobile & pavement vendors",                      members: 310, color: "#FB923C", accountId: "0.0.5220040" },
];

/* ─── GroupCard ──────────────────────────────────────── */
function GroupCard({ g, onViewQR }: { g: CommunityGroup; onViewQR: () => void }) {
  return (
    <div
      className="glass"
      style={{
        padding: 16, borderRadius: 16,
        display: "flex", flexDirection: "column", gap: 10,
        border: `1px solid ${g.color}22`,
        transition: "transform 0.2s, box-shadow 0.2s",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            padding: 10, borderRadius: 12,
            background: `${g.color}20`,
            color: g.color, display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            {g.icon}
          </div>
          <div>
            <p style={{ fontSize: 14, fontWeight: 800, color: "#fff", margin: 0 }}>{g.name}</p>
            <p style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", margin: "2px 0 0" }}>{g.desc}</p>
          </div>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Users size={14} color="rgba(255,255,255,0.4)" />
          <span style={{ fontSize: 12, fontWeight: 700, color: "rgba(255,255,255,0.6)" }}>
            {g.members} members
          </span>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          <button
            onClick={onViewQR}
            style={{
              padding: "6px 12px", borderRadius: 10, fontSize: 11, fontWeight: 700,
              background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)",
              color: "#fff", cursor: "pointer", display: "flex", alignItems: "center", gap: 4,
              fontFamily: "Inter, sans-serif",
            }}
          >
            <QrCode size={12}/> Pay
          </button>
          <button
            style={{
              padding: "6px 12px", borderRadius: 10, fontSize: 11, fontWeight: 700,
              background: `${g.color}18`, border: `1px solid ${g.color}40`,
              color: g.color, cursor: "pointer", fontFamily: "Inter, sans-serif",
            }}
          >
            Join Group
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── QR Modal ──────────────────────────────────────── */
function QRModal({ group, onClose }: { group: CommunityGroup; onClose: () => void }) {
  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed", inset: 0, zIndex: 999,
        background: "rgba(0,0,0,0.7)", backdropFilter: "blur(8px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: 20, animation: "fadeIn 0.2s ease",
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: "linear-gradient(170deg, #1a2e1a 0%, #0d1f0d 100%)",
          borderRadius: 24, padding: 28, maxWidth: 340, width: "100%",
          border: "1px solid rgba(255,215,0,0.15)",
          display: "flex", flexDirection: "column", alignItems: "center", gap: 16,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ padding: 8, borderRadius: 10, background: `${group.color}20`, color: group.color, display: "flex" }}>
              {group.icon}
            </div>
            <p style={{ fontSize: 14, fontWeight: 800, color: "#fff", margin: 0 }}>{group.name}</p>
          </div>
          <button onClick={onClose} style={{
            background: "rgba(255,255,255,0.1)", border: "none", borderRadius: 8,
            padding: 6, cursor: "pointer", color: "#fff", display: "flex",
          }}>
            <X size={16}/>
          </button>
        </div>

        <div style={{
          background: "#fff", padding: 12, borderRadius: 16,
          boxShadow: `0 0 30px ${group.color}30`,
        }}>
          <RealisticQR value={group.accountId} size={180} />
        </div>

        <div style={{ textAlign: "center" }}>
          <p style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", margin: "0 0 4px" }}>Group Account ID</p>
          <p style={{ fontFamily: "monospace", fontSize: 14, fontWeight: 700, color: "#FFD700", margin: 0 }}>
            {group.accountId}
          </p>
        </div>

        <p style={{ fontSize: 10, color: "rgba(255,255,255,0.35)", margin: 0, textAlign: "center" }}>
          Scan to pay dues or contribute to {group.name}
        </p>
      </div>
    </div>
  );
}

/* ─── Main Page ─────────────────────────────────────── */
export default function CFADashboard() {
  const [activeTab, setActiveTab] = useState("Treasury");
  const [qrGroup, setQrGroup] = useState<CommunityGroup | null>(null);

  const tabs = ["Treasury", "Governance", "Assets & Marketplace", "Community Groups"];

  return (
    <main style={{ padding: "16px 16px 90px", display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ paddingTop: 32 }}>
        <h1 style={{ fontSize: 24, fontWeight: 900, color: "#fff", margin: 0 }}>🌲 CFA Dashboard</h1>
        <p style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", margin: "4px 0 0" }}>
          Community Forest Association · Governance & Treasury
        </p>
      </div>

      <div style={{ display: "flex", gap: 10 }}>
        <div style={{ flex: 1, background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.3)", borderRadius: 16, padding: 16 }}>
          <p style={{ fontSize: 11, color: "rgba(255,255,255,0.6)", marginBottom: 4 }}>Treasury Balance</p>
          <p style={{ fontSize: 20, fontWeight: 900, color: "#22C55E" }}>14,500 KAI</p>
        </div>
        <div style={{ flex: 1, background: "rgba(255,215,0,0.1)", border: "1px solid rgba(255,215,0,0.3)", borderRadius: 16, padding: 16 }}>
          <p style={{ fontSize: 11, color: "rgba(255,255,255,0.6)", marginBottom: 4 }}>Members</p>
          <p style={{ fontSize: 20, fontWeight: 900, color: "#FFD700" }}>342 Active</p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 8, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "none" }}>
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: "8px 16px", borderRadius: 12, fontSize: 12, fontWeight: 700, whiteSpace: "nowrap",
              color: activeTab === tab ? "#121212" : "#fff",
              background: activeTab === tab ? "#FFD700" : "rgba(255,255,255,0.05)",
              border: activeTab === tab ? "none" : "1px solid rgba(255,255,255,0.1)",
              fontFamily: "Inter, sans-serif", cursor: "pointer",
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* ─── Treasury ─── */}
      {activeTab === "Treasury" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div className="glass" style={{ padding: 16, borderRadius: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{ padding: 10, borderRadius: 12, background: "rgba(34,197,94,0.2)" }}><Landmark size={20} color="#22C55E" /></div>
                <div>
                  <p style={{ fontSize: 14, fontWeight: 800, color: "#fff" }}>Monthly Contribution</p>
                  <p style={{ fontSize: 11, color: "rgba(255,255,255,0.5)" }}>50 KAI / month</p>
                </div>
              </div>
              <button className="btn-gold" style={{ padding: "8px 16px", borderRadius: 12, fontSize: 13, fontWeight: 800 }}>Pay Dues</button>
            </div>
          </div>

          <div className="glass" style={{ padding: 16, borderRadius: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 800, color: "#fff", marginBottom: 12 }}>Produce Sales Receipts</h3>
            {[1, 2].map((i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 0", borderBottom: i === 1 ? "1px solid rgba(255,255,255,0.05)" : "none" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ padding: 8, borderRadius: 10, background: "rgba(255,255,255,0.05)" }}><Receipt size={16} color="#FFD700" /></div>
                  <div>
                    <p style={{ fontSize: 13, fontWeight: 700, color: "#fff" }}>Timber Sale #{1024 + i}</p>
                    <p style={{ fontSize: 10, color: "rgba(255,255,255,0.4)" }}>Buyer: 0.0.8492{i} • Today</p>
                  </div>
                </div>
                <p style={{ fontSize: 13, fontWeight: 800, color: "#22C55E" }}>+500 KAI</p>
              </div>
            ))}
          </div>

          <button style={{
            display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
            padding: 14, borderRadius: 16, background: "rgba(255,255,255,0.05)", border: "1px dashed rgba(255,255,255,0.2)",
            color: "#fff", fontWeight: 700, fontSize: 14, cursor: "pointer", fontFamily: "Inter, sans-serif",
          }}>
            <QrCode size={18} /> Generate Buyer QR Code
          </button>
        </div>
      )}

      {/* ─── Governance ─── */}
      {activeTab === "Governance" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div className="glass" style={{ padding: 16, borderRadius: 16 }}>
            <span style={{ fontSize: 10, padding: "4px 8px", borderRadius: 8, background: "rgba(34,197,94,0.2)", color: "#22C55E", fontWeight: 700, marginBottom: 8, display: "inline-block" }}>Active Proposal</span>
            <p style={{ fontSize: 15, fontWeight: 800, color: "#fff", marginBottom: 6 }}>Purchase 50 new beehives for NTFP</p>
            <p style={{ fontSize: 12, color: "rgba(255,255,255,0.6)", marginBottom: 16 }}>Requesting 2,500 KAI from treasury to expand community honey production.</p>
            <div style={{ display: "flex", gap: 10 }}>
              <button style={{ flex: 1, padding: 10, borderRadius: 12, background: "rgba(34,197,94,0.2)", color: "#22C55E", fontWeight: 800, border: "1px solid rgba(34,197,94,0.3)" }}>Yes (68%)</button>
              <button style={{ flex: 1, padding: 10, borderRadius: 12, background: "rgba(239,68,68,0.1)", color: "#EF4444", fontWeight: 800, border: "1px solid rgba(239,68,68,0.2)" }}>No (32%)</button>
            </div>
          </div>
          <button className="glass" style={{ width: "100%", padding: 16, borderRadius: 16, color: "#FFD700", fontWeight: 800, fontSize: 14, display: "flex", justifyContent: "center", alignItems: "center", gap: 8, cursor: "pointer" }}>
            <Vote size={18} /> Create New Proposal
          </button>
        </div>
      )}

      {/* ─── Assets & Marketplace ─── */}
      {activeTab === "Assets & Marketplace" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div className="glass" style={{ padding: 16, borderRadius: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 800, color: "#fff", marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}><Leaf size={18} color="#22C55E"/> Tokenized Carbon Credits</h3>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
              <div>
                <p style={{ fontSize: 13, fontWeight: 700, color: "#fff" }}>Block A - 50 Hectares</p>
                <p style={{ fontSize: 11, color: "rgba(255,255,255,0.5)" }}>Generating 120 Carbon Credits / yr</p>
              </div>
              <span style={{ fontSize: 12, padding: "4px 8px", borderRadius: 8, background: "rgba(255,215,0,0.1)", color: "#FFD700", fontWeight: 700 }}>NFT Minted</span>
            </div>
            <button style={{ width: "100%", padding: 10, borderRadius: 10, background: "rgba(34,197,94,0.15)", color: "#22C55E", fontWeight: 700, fontSize: 13, border: "none", cursor: "pointer" }}>Sell Credits on Open Market</button>
          </div>

          <div className="glass" style={{ padding: 16, borderRadius: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 800, color: "#fff", marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}><Sprout size={18} color="#F97316"/> NTFP Marketplace</h3>
            <div style={{ display: "flex", gap: 10, overflowX: "auto", paddingBottom: 10, scrollbarWidth: "none" }}>
              {[{n: "Raw Honey", p: "12 KAI/kg"}, {n: "Baobab Powder", p: "8 KAI/kg"}, {n: "Shea Butter", p: "15 KAI/kg"}].map(item => (
                <div key={item.n} style={{ minWidth: 120, padding: 12, borderRadius: 12, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)" }}>
                  <p style={{ fontSize: 12, fontWeight: 700, color: "#fff", marginBottom: 4 }}>{item.n}</p>
                  <p style={{ fontSize: 12, fontWeight: 800, color: "#FFD700" }}>{item.p}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ─── Community Groups ─── */}
      {activeTab === "Community Groups" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

          {/* Green Economy */}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
              <Leaf size={16} color="#22C55E"/>
              <h3 style={{ fontSize: 13, fontWeight: 800, color: "#22C55E", margin: 0, textTransform: "uppercase", letterSpacing: 1 }}>
                Green Economy
              </h3>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {GREEN_GROUPS.map(g => (
                <GroupCard key={g.name} g={g} onViewQR={() => setQrGroup(g)} />
              ))}
            </div>
          </div>

          {/* Divider */}
          <div style={{ height: 1, background: "linear-gradient(90deg, transparent, rgba(255,215,0,0.3), transparent)" }}/>

          {/* SME & Informal Traders */}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
              <Store size={16} color="#F97316"/>
              <h3 style={{ fontSize: 13, fontWeight: 800, color: "#F97316", margin: 0, textTransform: "uppercase", letterSpacing: 1 }}>
                SME & Informal Traders
              </h3>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {SME_GROUPS.map(g => (
                <GroupCard key={g.name} g={g} onViewQR={() => setQrGroup(g)} />
              ))}
            </div>
          </div>

          {/* Summary bar */}
          <div className="glass" style={{
            padding: 14, borderRadius: 14, display: "flex", justifyContent: "space-around",
            border: "1px solid rgba(255,215,0,0.15)",
          }}>
            <div style={{ textAlign: "center" }}>
              <p style={{ fontSize: 18, fontWeight: 900, color: "#FFD700", margin: 0 }}>9</p>
              <p style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", margin: 0 }}>Groups</p>
            </div>
            <div style={{ width: 1, background: "rgba(255,255,255,0.1)" }}/>
            <div style={{ textAlign: "center" }}>
              <p style={{ fontSize: 18, fontWeight: 900, color: "#22C55E", margin: 0 }}>
                {[...GREEN_GROUPS, ...SME_GROUPS].reduce((s, g) => s + g.members, 0).toLocaleString()}
              </p>
              <p style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", margin: 0 }}>Total Members</p>
            </div>
            <div style={{ width: 1, background: "rgba(255,255,255,0.1)" }}/>
            <div style={{ textAlign: "center" }}>
              <p style={{ fontSize: 18, fontWeight: 900, color: "#A78BFA", margin: 0 }}>KES 2.1M</p>
              <p style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", margin: 0 }}>Monthly Volume</p>
            </div>
          </div>
        </div>
      )}

      {/* QR Modal */}
      {qrGroup && <QRModal group={qrGroup} onClose={() => setQrGroup(null)} />}
    </main>
  );
}
