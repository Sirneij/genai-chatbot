export type Message = {
  id: number;
  text: string;
  sender: "user" | "bot";
  complete?: boolean;
};
