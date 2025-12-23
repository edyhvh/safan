'use client';

import { useState } from 'react';
import { SiEthereum, SiBitcoin, SiSolana, SiGithubsponsors } from 'react-icons/si';
import { BsCreditCard } from 'react-icons/bs';
import { IoCopyOutline, IoCheckmark } from 'react-icons/io5';
import { DONATION_CONFIG } from '@/lib/config';

interface CopyableWalletProps {
  icon: React.ReactNode;
  name: string;
  address: string;
}

function CopyableWallet({ icon, name, address }: CopyableWalletProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center justify-center gap-3 text-lg group">
      {icon}
      <span className="font-medium">{name}</span>
      <button
        onClick={handleCopy}
        className="flex items-center gap-2 text-gray/70 hover:text-black transition-colors cursor-pointer"
        title={`Copy ${name} address`}
      >
        <span className="font-mono text-sm">{address}</span>
        {copied ? (
          <IoCheckmark className="w-4 h-4 text-green-600" />
        ) : (
          <IoCopyOutline className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
        )}
      </button>
    </div>
  );
}

export default function DonatePage() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="space-y-6 font-ui-latin text-gray">
          {/* Ethereum */}
          <CopyableWallet
            icon={<SiEthereum className="w-6 h-6" />}
            name="Ethereum"
            address={DONATION_CONFIG.wallets.ethereum}
          />

          {/* Bitcoin */}
          <CopyableWallet
            icon={<SiBitcoin className="w-6 h-6" />}
            name="Bitcoin"
            address={DONATION_CONFIG.wallets.bitcoin}
          />

          {/* Solana */}
          <CopyableWallet
            icon={<SiSolana className="w-6 h-6" />}
            name="Solana"
            address={DONATION_CONFIG.wallets.solana}
          />

          {/* GitHub Sponsor */}
          <div className="flex items-center justify-center gap-3 text-lg">
            <div className="flex items-center gap-1">
              <SiGithubsponsors className="w-6 h-6" />
              <BsCreditCard className="w-5 h-5" />
            </div>
            <span className="font-medium">Github Sponsor</span>
            <a
              href={DONATION_CONFIG.githubSponsor}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray/70 hover:text-black underline underline-offset-2 transition-colors"
            >
              @edyhvh
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
