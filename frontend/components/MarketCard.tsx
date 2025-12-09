import { useEffect, useState } from "react";

interface MarketCardProps {
  name: string;
  price: string | number;
  change?: string | number;
}

export default function MarketCard({ name, price, change }: MarketCardProps) {
  const [animate, setAnimate] = useState(false);

  const isPositive = Number(change) >= 0;

  useEffect(() => {
    // Trigger animation when price or change updates
    setAnimate(true);
    const timeout = setTimeout(() => setAnimate(false), 350); // duration of animation
    return () => clearTimeout(timeout);
  }, [price, change]);

  return (
    <div
      className={`bg-white p-6 rounded-2xl shadow-md flex flex-col gap-2 w-full
                  hover:shadow-lg transition-shadow duration-200
                  ${animate ? "animate-cardPop" : ""}`}
    >
      <h3 className="text-lg font-semibold">{name}</h3>

      <p className={`text-2xl font-bold ${animate ? "animate-numberFlash" : ""}`}>
        ${price}
      </p>

      {change !== undefined && (
        <p
          className={`text-sm font-medium ${animate ? "animate-numberFlash" : ""} ${
            isPositive ? "text-green-600" : "text-red-600"
          }`}
        >
          {isPositive ? "+" : ""}
          {change}%
        </p>
      )}
    </div>
  );
}