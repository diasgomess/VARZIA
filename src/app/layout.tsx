import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VARZIA | Dashboard Técnico",
  description: "Dashboard inicial com placar, jogadores e mapa do campo",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
