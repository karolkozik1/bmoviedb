"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiRequest, Movie } from "@/lib/api";
import { movieArtworkUrl } from "@/lib/artwork";

type WatchlistEntry = { movie_id: number; movie: Movie };

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong. Please try again.";
}

function displayRating(movie: Movie) {
  const value = movie.average_rating ?? movie.rating;
  return value == null ? "—" : value.toFixed(1);
}

export default function WatchlistPage() {
  const [entries, setEntries] = useState<WatchlistEntry[]>([]);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let active = true;
    const savedToken = window.localStorage.getItem("bmoviedb_token");

    void Promise.resolve().then(() => {
      if (!savedToken) {
        if (active) setLoading(false);
        return;
      }
      if (active) setToken(savedToken);
      return apiRequest<WatchlistEntry[]>("/users/me/watchlist", { token: savedToken })
        .then((items) => {
          if (active) setEntries(items);
        })
        .catch((requestError: unknown) => {
          if (active) setError(errorMessage(requestError));
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    });

    return () => {
      active = false;
    };
  }, []);

  async function removeMovie(movieId: number) {
    if (!token) return;
    try {
      await apiRequest<void>(`/users/me/watchlist/${movieId}`, {
        method: "DELETE",
        token,
      });
      setEntries((current) => current.filter((entry) => entry.movie_id !== movieId));
      setNotice("Film removed from your watchlist.");
    } catch (requestError) {
      setError(errorMessage(requestError));
    }
  }

  return (
    <main className="watchlist-page">
      <div className="account-heading">
        <Link className="back-link" href="/profile">← Back to profile</Link>
        <span className="section-kicker">THE FILMS YOU’VE BEEN MEANING TO SEE</span>
        <h1>Your watchlist<span className="heading-period">.</span></h1>
        <p>A growing pile of good intentions. No rush.</p>
      </div>

      {!token && !loading ? (
        <section className="watchlist-empty">
          <span className="empty-mark">✳</span>
          <h2>This list is yours to make.</h2>
          <p>Sign in to save films for later and find them here again.</p>
          <Link className="hero-cta" href="/profile">Sign in to your account <span>→</span></Link>
        </section>
      ) : (
        <>
          {error && <div className="error-banner" role="alert">{error}</div>}
          {notice && <div className="watchlist-notice" role="status">{notice}</div>}
          {loading ? (
            <div className="account-loading" role="status">Gathering your films…</div>
          ) : entries.length ? (
            <div className="movie-grid watchlist-grid">
              {entries.map(({ movie, movie_id: movieId }, index) => (
                <article className="movie-card" key={movieId}>
                  <div className="poster" style={{ backgroundImage: `url("${movieArtworkUrl(movieId + index)}")` }}>
                    <span className="poster-rating">★ {displayRating(movie)}</span>
                    <button className="save-button saved watchlist-remove" aria-label={`Remove ${movie.title} from watchlist`} onClick={() => void removeMovie(movieId)}>×</button>
                  </div>
                  <div className="movie-meta">
                    <div className="movie-title-line"><h4>{movie.title}</h4><span>{movie.release_year ?? "—"}</span></div>
                    <p>{movie.genres.slice(0, 2).map((genre) => genre.name).join(" · ") || "A story worth discovering"}</p>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            !error && (
              <section className="watchlist-empty">
                <span className="empty-mark">✳</span>
                <h2>A blank page, for now.</h2>
                <p>When a film catches your eye, save it here for a future movie night.</p>
                <Link className="hero-cta" href="/discover">Find a film <span>→</span></Link>
              </section>
            )
          )}
        </>
      )}
    </main>
  );
}
