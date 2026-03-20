import { create } from "zustand";

interface KaibarState {
  connected: boolean;
  walletType: "hashpack" | "metamask" | null;
  accountId: string;
  autoMineActive: boolean;
  balances: { hbar: number; kai: number; ytoken: number; gami: number };
  connectWallet: (type: "hashpack" | "metamask", accountId?: string) => void;
  disconnectWallet: () => void;
  toggleAutoMine: () => void;
  incrementKai: (amount: number) => void;
}

export const useKaibarStore = create<KaibarState>((set) => ({
  connected: false,
  walletType: null,
  accountId: "",
  autoMineActive: false,
  balances: { hbar: 0, kai: 0, ytoken: 0, gami: 0 },

  connectWallet: (type, customAccountId) =>
    set({
      connected: true,
      walletType: type,
      accountId: customAccountId
        ? customAccountId
        : type === "hashpack"
          ? "0.0.4872931"
          : "0xaA9953BAB5de2147cC0c919Ab2ff22d809188514",
      balances: { hbar: 245.8, kai: 1250, ytoken: 580, gami: 732 },
    }),

  disconnectWallet: () =>
    set({
      connected: false,
      walletType: null,
      accountId: "",
      autoMineActive: false,
      balances: { hbar: 0, kai: 0, ytoken: 0, gami: 0 },
    }),

  toggleAutoMine: () =>
    set((s) => ({ autoMineActive: !s.autoMineActive })),

  incrementKai: (amount) =>
    set((s) => ({
      balances: { ...s.balances, kai: s.balances.kai + amount },
    })),
}));
