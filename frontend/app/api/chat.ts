export async function sendPrompt(query: string): Promise<string> {
  const res = await fetch("/api/agent", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    throw new Error("Failed to fetch agent response");
  }

  const data = await res.json();
  return data.result;
}