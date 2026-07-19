import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CineMind AI Director",
  description: "Continuity-first AI filmmaking director console"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
