"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ChartData {
  name: string;
  price: number;
}

const sampleData: ChartData[] = [
  { name: "Mon", price: 42000 },
  { name: "Tue", price: 43000 },
  { name: "Wed", price: 44000 },
  { name: "Thu", price: 41500 },
  { name: "Fri", price: 45000 },
];

export default function Chart() {
  return (
    <div className="w-full h-80 bg-white rounded-2xl shadow-md p-5">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={sampleData}>
          <XAxis dataKey="name" stroke="#888" tickLine={false} />
          <YAxis stroke="#888" tickLine={false} />
          <Tooltip />
          <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={3} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}