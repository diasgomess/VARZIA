"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "./page.module.css";
import { connectMatchSocket, type MatchEvent } from "@/lib/matchSocketStub";

type FieldEvent = {
  id: number;
  player: string;
  action: string;
  x: number;
  y: number;
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

export default function Home() {
  const [homeScore, setHomeScore] = useState(0);
  const [awayScore, setAwayScore] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [fieldEvents, setFieldEvents] = useState<FieldEvent[]>([]);

  useEffect(() => {
    const onEvent = (event: MatchEvent) => {
      if (event.type === "goal" && event.team) {
        if (event.team === "home") {
          setHomeScore((score) => score + 1);
        } else {
          setAwayScore((score) => score + 1);
        }
      }

      if (event.type === "timer") {
        setSeconds((value) => value + (event.seconds ?? 1));
      }

      if (
        event.type === "event" &&
        event.player &&
        event.action &&
        typeof event.x === "number" &&
        typeof event.y === "number"
      ) {
        const { player, action, x, y } = event;
        setFieldEvents((current) => [
          {
            id: Date.now() + current.length,
            player,
            action,
            x,
            y,
          },
          ...current,
        ].slice(0, 12));
      }
    };

    const disconnect = connectMatchSocket(onEvent);
    return disconnect;
  }, []);

  const timerLabel = useMemo(() => {
    const minutes = String(Math.floor(seconds / 60)).padStart(2, "0");
    const remainingSeconds = String(seconds % 60).padStart(2, "0");
    return `${minutes}:${remainingSeconds}`;
  }, [seconds]);

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <header className={styles.header}>
          <h1>Dashboard do técnico</h1>
          <p>Tempo de jogo: {timerLabel}</p>
        </header>

        <section className={styles.scoreboard}>
          <div>
            <strong>Time A</strong>
            <span>{homeScore}</span>
          </div>
          <div>
            <strong>Time B</strong>
            <span>{awayScore}</span>
          </div>
        </section>

        <section className={styles.content}>
          <aside className={styles.players}>
            <h2>Jogadores em campo</h2>
            <ul>
              {players.map((player) => (
                <li key={player}>{player}</li>
              ))}
            </ul>
          </aside>

          <div className={styles.fieldCard}>
            <h2>Mapa do campo (stub)</h2>
            <div className={styles.field}>
              <div className={styles.halfway} />
              <div className={styles.centerCircle} />
              {fieldEvents.map((event) => (
                <span
                  key={event.id}
                  className={styles.eventPoint}
                  style={{
                    left: `${event.x}%`,
                    top: `${event.y}%`,
                  }}
                  title={`${event.player}: ${event.action}`}
                />
              ))}
            </div>
            <ul className={styles.eventsList}>
              {fieldEvents.length === 0 ? (
                <li>Nenhum evento recebido ainda.</li>
              ) : (
                fieldEvents.slice(0, 5).map((event) => (
                  <li key={`${event.id}-text`}>
                    {event.player} — {event.action} ({event.x}%, {event.y}%)
                  </li>
                ))
              )}
            </ul>
          </div>
        </section>
      </main>
    </div>
  );
}
