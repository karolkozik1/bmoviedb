import type { Metadata } from "next";
import { Cutive_Mono, Josefin_Sans, Lora, Oxanium } from "next/font/google";
import SiteHeader, { SiteFooter } from "@/components/SiteHeader";
import "./globals.css";

const cutiveMono = Cutive_Mono({
  weight: "400",
  variable: "--font-cutive-mono",
  subsets: ["latin"],
  display: "swap",
});

const josefinSans = Josefin_Sans({
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
  variable: "--font-josefin-sans",
  subsets: ["latin"],
  display: "swap",
});

const lora = Lora({
  weight: ["400", "500"],
  variable: "--font-lora",
  subsets: ["latin"],
  display: "swap",
});

const oxanium = Oxanium({
  weight: ["500", "600", "700"],
  variable: "--font-oxanium",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "BMovieDb — Find your next favorite film",
  description:
    "Discover, rate, and save films with BMovieDb, a home for people who stay for the credits.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${cutiveMono.variable} ${josefinSans.variable} ${lora.variable} ${oxanium.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <SiteHeader />
        {children}
        <SiteFooter />
      </body>
    </html>
  );
}
