import type { Metadata } from 'next';
import './globals.css';
import BottomNav from '@/components/shared/BottomNav';
import { ClientProviders } from '@/components/providers/ClientProviders';

export const metadata: Metadata = {
  title: 'KAIBAR — DeFi Ecosystem',
  description: 'Premium Rastafari-inspired Web3 DeFi platform on Hedera',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-[100dvh] gradient-bg text-white flex justify-center">
        <ClientProviders>
          <div className="w-full max-w-[600px] min-h-[100dvh] relative flex flex-col overflow-x-hidden">
            <main className="flex-1 pb-24">
              {children}
            </main>
            <BottomNav />
          </div>
        </ClientProviders>
      </body>
    </html>
  );
}
