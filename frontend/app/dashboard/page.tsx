"use client";

import { useEffect, useState } from "react";
import MarketCard from "../../components/MarketCard";

export default function DashboardPage() {
  const [data, setData] = useState({
    BTC: { price: null as number | null },
    ETH: { price: null as number | null },
    SOL: { price: null as number | null },
  });

  const fetchPrice = async (symbol: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/crypto_price/${symbol}/USD`);
      const json = await res.json();
      return json.price ?? null;
    } catch (err) {
      console.error("Price fetch error:", symbol, err);
      return null;
    }
  };

  useEffect(() => {
    async function loadData() {
      const [btcPrice, ethPrice, solPrice] = await Promise.all([
        fetchPrice("BTC"),
        fetchPrice("ETH"),
        fetchPrice("SOL"),
      ]);

      setData({
        BTC: { price: btcPrice },
        ETH: { price: ethPrice },
        SOL: { price: solPrice },
      });
    }

    loadData();
  }, []);

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-3xl font-bold">Market Overview</h1>

      {/* Market Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MarketCard
          name="Bitcoin"
          price={data.BTC.price ? data.BTC.price.toLocaleString() : "Loading..."}
        />
        <MarketCard
          name="Ethereum"
          price={data.ETH.price ? data.ETH.price.toLocaleString() : "Loading..."}
        />
        <MarketCard
          name="Solana"
          price={data.SOL.price ? data.SOL.price.toLocaleString() : "Loading..."}
        />
      </div>
    </div>
  );
}