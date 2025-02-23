export const BASE_API_URL = process.env.NEXT_PUBLIC_BASE_API_URL as string;
export const BASE_WS_URL = BASE_API_URL?.replace("http", "ws");
