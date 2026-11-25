"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

function SearchIcon() {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-4-4" />
    </svg>
  );
}

export default function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="topbar">
      <Link className="brand" href="/discover" aria-label="BmovieDb home">
        <span className="brand-mark"><span /></span>
        <span>bmovie<span className="brand-light">db</span></span>
      </Link>
      <nav className="main-nav" aria-label="Main navigation">
        <Link className={pathname === "/discover" ? "nav-active" : ""} href="/discover">Discover</Link>
        <Link className={pathname === "/search" ? "nav-active" : ""} href="/search">Search</Link>
      </nav>
      <form className="search" action="/search" method="get">
        <SearchIcon />
        <input aria-label="Search movies" name="q" placeholder="Search movies..." />
        <kbd>↵</kbd>
      </form>
      <div className="account-area">
        <Link className={`profile-link ${pathname.startsWith("/profile") ? "profile-active" : ""}`} href="/profile">
          <span className="profile-link-mark">✳</span>
          Profile
        </Link>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="footer">
      <Link className="brand" href="/discover">
        <span className="brand-mark"><span /></span>
        <span>bmovie<span className="brand-light">db</span></span>
      </Link>
      <span>Good films. Strange corners. No dress code.</span>
      <span>For the beautifully offbeat <b>✳</b></span>
    </footer>
  );
}
