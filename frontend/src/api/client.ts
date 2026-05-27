export type HealthResponse = {
  status: string;
  message: string;
};

// VITE_API_BASE_URL이 없으면 빈 문자열 → 같은 origin(또는 Vite proxy)으로 요청
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/health`);

  if (!response.ok) {
    throw new Error("Failed to connect to backend");
  }

  return response.json();
}
