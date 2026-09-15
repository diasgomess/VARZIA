export type MatchEvent = {
  type: "goal" | "timer" | "event";
  team?: "home" | "away";
  seconds?: number;
  player?: string;
  action?: string;
  x?: number;
  y?: number;
};

const players = [
  "João",
  "Lucas",
  "Pedro",
  "Rafael",
  "Carlos",
  "Felipe",
  "André",
  "Bruno",
  "Diego",
  "Vitor",
  "Thiago",
];

export function connectMatchSocket(onEvent: (event: MatchEvent) => void) {
  const wsUrl = process.env.NEXT_PUBLIC_MATCH_WS_URL;

  if (wsUrl) {
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (message) => {
      try {
        const event = JSON.parse(message.data) as MatchEvent;
        onEvent(event);
      } catch {
        // ignore malformed payloads
      }
    };

    return () => ws.close();
  }

  const interval = setInterval(() => {
    onEvent({ type: "timer", seconds: 1 });

    if (Math.random() > 0.6) {
      onEvent({
        type: "event",
        player: players[Math.floor(Math.random() * players.length)],
        action: "Passe",
        x: Math.round(Math.random() * 100),
        y: Math.round(Math.random() * 100),
      });
    }

    if (Math.random() > 0.95) {
      onEvent({
        type: "goal",
        team: Math.random() > 0.5 ? "home" : "away",
      });
    }
  }, 1000);

  return () => clearInterval(interval);
}
