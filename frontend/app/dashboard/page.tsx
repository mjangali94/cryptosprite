"use client";

import { useEffect, useState } from "react";
import MarketCard from "../../components/MarketCard";
import Chart from "../../components/Chart";

export default function DashboardPage() {
  const [data, setData] = useState({
    BTC: { price: null as number | null, change: null as number | null },
    ETH: { price: null as number | null, change: null as number | null },
    SOL: { price: null as number | null, change: null as number | null },
  });

  // Fetch today's price
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

  // Fetch percentage change
  const fetchChange = async (symbol: string) => {
    try {
      const res = await fetch(
        `http://localhost:8000/api/crypto_price/percentage_change/${symbol}/USD/`
      );
      const json = await res.json();
      return json.percentage_change ?? null;
    } catch (err) {
      console.error("Change fetch error:", symbol, err);
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

      const [btcChange, ethChange, solChange] = await Promise.all([
        fetchChange("BTC"),
        fetchChange("ETH"),
        fetchChange("SOL"),
      ]);

      setData({
        BTC: { price: btcPrice, change: btcChange },
        ETH: { price: ethPrice, change: ethChange },
        SOL: { price: solPrice, change: solChange },
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
          change={data.BTC.change !== null ? data.BTC.change.toFixed(2) : "Loading..."}
        />

        <MarketCard
          name="Ethereum"
          price={data.ETH.price ? data.ETH.price.toLocaleString() : "Loading..."}
          change={data.ETH.change !== null ? data.ETH.change.toFixed(2) : "Loading..."}
        />

        <MarketCard
          name="Solana"
          price={data.SOL.price ? data.SOL.price.toLocaleString() : "Loading..."}
          change={data.SOL.change !== null ? data.SOL.change.toFixed(2) : "Loading..."}
        />
      </div>

      {/* Chart */}
     {/* <div>
        <h2 className="text-2xl font-semibold mb-3">BTC Price Chart</h2>
        <Chart />
      </div>
      */}
    </div>
  );
}