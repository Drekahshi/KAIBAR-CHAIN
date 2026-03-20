'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, createConfig, WagmiProvider } from 'wagmi';
import { defineChain } from 'viem';
import { useState } from 'react';

export const hederaTestnet = defineChain({
  id: 296,
  name: 'Hedera Testnet',
  network: 'hedera-testnet',
  nativeCurrency: {
    name: 'HBAR',
    symbol: 'HBAR',
    decimals: 18,
  },
  rpcUrls: {
    default: {
      http: ['https://testnet.hashio.io/api'],
    },
    public: {
      http: ['https://testnet.hashio.io/api'],
    },
  },
  blockExplorers: {
    default: { name: 'Hashscan', url: 'https://hashscan.io/testnet' },
  },
});

export const wagmiConfig = createConfig({
  chains: [hederaTestnet],
  transports: {
    [hederaTestnet.id]: http(),
  },
});

export function ClientProviders({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </WagmiProvider>
  );
}
