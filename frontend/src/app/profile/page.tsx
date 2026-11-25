"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { apiRequest, User } from "@/lib/api";

type Profile = User & {
  role: string;
  trust_score: number;
  created_at: string;
};

type WatchlistEntry = { movie_id: number };

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong. Please try again.";
}

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<Profile | null>(null);
  const [watchlistCount, setWatchlistCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const savedToken = window.localStorage.getItem("bmoviedb_token");

    void Promise.resolve().then(async () => {
      if (!savedToken) {
        if (active) setLoading(false);
        return;
      }

      try {
        const [profile, items] = await Promise.all([
          apiRequest<Profile>("/users/me", { token: savedToken }),
          apiRequest<WatchlistEntry[]>("/users/me/watchlist", { token: savedToken }),
        ]);
        if (active) {
          setUser(profile);
          setWatchlistCount(items.length);
        }
      } catch (requestError) {
        if (active) {
          setError(errorMessage(requestError));
          window.localStorage.removeItem("bmoviedb_token");
        }
      } finally {
        if (active) setLoading(false);
      }
    });

    return () => {
      active = false;
    };
  }, []);

  async function submitAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email"));
    const password = String(formData.get("password"));

    try {
      if (authMode === "register") {
        await apiRequest("/auth/register", {
          method: "POST",
          body: JSON.stringify({
            username: formData.get("username"),
            email,
            password,
          }),
        });
      }
      const result = await apiRequest<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      window.localStorage.setItem("bmoviedb_token", result.access_token);
      const [profile, items] = await Promise.all([
        apiRequest<Profile>("/users/me", { token: result.access_token }),
        apiRequest<WatchlistEntry[]>("/users/me/watchlist", { token: result.access_token }),
      ]);
      setUser(profile);
      setWatchlistCount(items.length);
      setError("");
    } catch (requestError) {
      setError(errorMessage(requestError));
      setBusy(false);
    }
  }

  function signOut() {
    window.localStorage.removeItem("bmoviedb_token");
    setUser(null);
    setWatchlistCount(0);
    router.push("/discover");
  }

  return (
    <main className="account-page">
      <div className="account-heading">
        <span className="section-kicker">YOUR CORNER OF THE ARCHIVE</span>
        <h1>{user ? "Your profile" : "Find your people."}</h1>
        <p>A little space for your films, your notes, and your own particular taste.</p>
      </div>

      {loading ? (
        <div className="account-loading" role="status">Opening your file…</div>
      ) : user ? (
        <section className="profile-card">
          <div className="profile-identity">
            <span className="profile-avatar">{user.username.slice(0, 1).toUpperCase()}</span>
            <div>
              <span className="section-kicker">B-MOVIE CLUB MEMBER</span>
              <h2>{user.username}</h2>
              <p>{user.email}</p>
            </div>
          </div>
          <div className="profile-facts">
            <div><span>Membership</span><strong>{user.role}</strong></div>
            <div><span>Trust score</span><strong>{user.trust_score}</strong></div>
            <div><span>Here since</span><strong>{new Date(user.created_at).getUTCFullYear()}</strong></div>
          </div>
          <Link className="watchlist-panel" href="/profile/watchlist">
            <span className="watchlist-panel-icon">✳</span>
            <span><strong>Your watchlist</strong><small>Films you mean to get around to</small></span>
            <span className="watchlist-total">{watchlistCount}</span>
          </Link>
          <div className="profile-actions">
            <Link href="/discover">Back to discovering <span>→</span></Link>
            <button onClick={signOut}>Sign out</button>
          </div>
        </section>
      ) : (
        <section className="auth-page-card">
          <div className="auth-page-copy">
            <span className="section-kicker">{authMode === "login" ? "PULL UP A CHAIR" : "JOIN THE BACK ROW"}</span>
            <h2>{authMode === "login" ? "Welcome back." : "Make yourself at home."}</h2>
            <p>{authMode === "login" ? "Sign in to pick up where you left off." : "Save the strange ones. Rate the overlooked ones. Find your crowd."}</p>
          </div>
          <form className="auth-form profile-auth-form" onSubmit={submitAuth}>
            {authMode === "register" && (
              <label>Screen name<input name="username" required minLength={3} maxLength={255} placeholder="What should we call you?" /></label>
            )}
            <label>Email address<input name="email" type="email" required placeholder="you@example.com" /></label>
            <label>Password<input name="password" type="password" required minLength={8} placeholder="At least 8 characters" /></label>
            {error && <p className="inline-error" role="alert">{error}</p>}
            <button disabled={busy}>{busy ? "One moment…" : authMode === "login" ? "Sign in" : "Create account"} <span>→</span></button>
          </form>
          <p className="auth-page-switch">
            {authMode === "login" ? "New around here?" : "Already have an account?"}
            <button onClick={() => { setError(""); setAuthMode(authMode === "login" ? "register" : "login"); }}>
              {authMode === "login" ? "Create an account" : "Sign in"}
            </button>
          </p>
        </section>
      )}
    </main>
  );
}
