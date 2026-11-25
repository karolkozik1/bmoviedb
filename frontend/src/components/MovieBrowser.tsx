"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  apiRequest,
  Genre,
  Movie,
  Rating,
  Review,
  User,
} from "@/lib/api";
import { movieArtworkUrl } from "@/lib/artwork";

function Icon({
  name,
  size = 18,
}: {
  name: "search" | "bookmark" | "arrow" | "star" | "close" | "play" | "user";
  size?: number;
}) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true as const,
  };
  const paths = {
    search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
    bookmark: <><path d="M6 4.8A1.8 1.8 0 0 1 7.8 3h8.4A1.8 1.8 0 0 1 18 4.8V21l-6-4-6 4z" /></>,
    arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
    star: <path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9z" />,
    close: <><path d="m18 6-12 12M6 6l12 12" /></>,
    play: <path d="m8 5 12 7-12 7z" />,
    user: <><circle cx="12" cy="8" r="4" /><path d="M5 21a7 7 0 0 1 14 0" /></>,
  };
  return <svg {...common}>{paths[name]}</svg>;
}

function displayRating(movie: Movie) {
  const value = movie.average_rating ?? movie.rating;
  return value == null ? "—" : value.toFixed(1);
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong. Please try again.";
}

type MovieBrowserProps = {
  mode: "discover" | "search";
  initialQuery?: string;
};

export default function MovieBrowser({
  mode,
  initialQuery = "",
}: MovieBrowserProps) {
  const router = useRouter();
  const [movies, setMovies] = useState<Movie[]>([]);
  const [genres, setGenres] = useState<Genre[]>([]);
  const [query, setQuery] = useState(initialQuery);
  const [searchText, setSearchText] = useState(initialQuery);
  const [releaseYear, setReleaseYear] = useState("");
  const [minRating, setMinRating] = useState("");
  const [genreId, setGenreId] = useState<number | null>(null);
  const [appliedFilters, setAppliedFilters] = useState<{
    releaseYear: string;
    minRating: string;
    genreId: number | null;
  }>({
    releaseYear: "",
    minRating: "",
    genreId: null,
  });
  const [sortBy, setSortBy] = useState("newest");
  const [page, setPage] = useState(0);
  const [searchNonce, setSearchNonce] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [watchlist, setWatchlist] = useState<number[]>([]);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [notice, setNotice] = useState("");
  const [userRating, setUserRating] = useState<Rating | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [reviewText, setReviewText] = useState("");
  const [reviewError, setReviewError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    apiRequest<Genre[]>("/genres")
      .then((data) => {
        if (active) setGenres(data);
      })
      .catch((error: Error) => {
        if (active) setNotice(error.message);
      });

    const savedToken = window.localStorage.getItem("bmoviedb_token");
    if (savedToken) {
      apiRequest<User>("/users/me", { token: savedToken })
        .then((profile) => {
          if (active) {
            setToken(savedToken);
            setUser(profile);
          }
        })
        .catch(() => window.localStorage.removeItem("bmoviedb_token"));
    }

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    const params = new URLSearchParams({
      skip: String(page * 18),
      limit: "18",
      sort_by: sortBy,
      is_active: "true",
    });
    if (mode === "search") {
      if (query.trim().length >= 2) params.set("title", query.trim());
      if (appliedFilters.releaseYear) params.set("release_year", appliedFilters.releaseYear);
      if (appliedFilters.minRating) params.set("min_rating", appliedFilters.minRating);
      if (appliedFilters.genreId !== null) params.set("genre_id", String(appliedFilters.genreId));
    }

    apiRequest<Movie[]>(`/movies?${params.toString()}`)
      .then((data) => {
        if (!active) return;
        setMovies((current) => (page === 0 ? data : [...current, ...data]));
        setHasMore(data.length === 18);
        setApiError("");
      })
      .catch((error: Error) => {
        if (active) setApiError(error.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [appliedFilters, mode, page, query, searchNonce, sortBy]);

  useEffect(() => {
    if (!token) return;
    apiRequest<{ movie_id: number }[]>("/users/me/watchlist", { token })
      .then((items) => setWatchlist(items.map((item) => item.movie_id)))
      .catch((error: Error) => setNotice(error.message));
  }, [token]);

  useEffect(() => {
    if (!selectedMovie) return;
    let active = true;
    const movieId = selectedMovie.id;
    apiRequest<Review[]>(`/movies/${movieId}/reviews`)
      .then((items) => {
        if (active) setReviews(items);
      })
      .catch((error: Error) => {
        if (active) setReviewError(error.message);
      });
    if (token) {
      apiRequest<Rating | null>(`/movies/${movieId}/ratings/me`, { token })
        .then((rating) => {
          if (active) setUserRating(rating);
        })
        .catch((error: Error) => {
          if (active) setReviewError(error.message);
        });
    }
    return () => {
      active = false;
    };
  }, [selectedMovie, token]);

  const featuredMovie = movies[0];

  function applySearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (searchText.trim().length === 1) {
      setNotice("Enter at least 2 characters to search.");
      return;
    }
    setLoading(true);
    setPage(0);
    setQuery(searchText.trim());
    setAppliedFilters({ releaseYear, minRating, genreId });
    setSearchNonce((current) => current + 1);
  }

  function openMovie(movie: Movie) {
    setReviews([]);
    setUserRating(null);
    setReviewError("");
    setSelectedMovie(movie);
  }

  async function toggleWatchlist(movie: Movie) {
    if (!token) {
      router.push("/profile");
      return;
    }
    const saved = watchlist.includes(movie.id);
    try {
      if (saved) {
        await apiRequest<void>(`/users/me/watchlist/${movie.id}`, {
          method: "DELETE",
          token,
        });
        setWatchlist((current) => current.filter((id) => id !== movie.id));
        setNotice("Removed from your watchlist.");
      } else {
        await apiRequest(`/users/me/watchlist/${movie.id}`, {
          method: "POST",
          token,
        });
        setWatchlist((current) => [...current, movie.id]);
        setNotice("Added to your watchlist.");
      }
    } catch (error) {
      setNotice(errorMessage(error));
    }
  }

  async function rateMovie(value: number) {
    if (!selectedMovie || !token) {
      router.push("/profile");
      return;
    }
    try {
      const rating = await apiRequest<Rating>(
        `/movies/${selectedMovie.id}/ratings`,
        { method: "POST", token, body: JSON.stringify({ rating: value }) },
      );
      setUserRating(rating);
      setNotice("Your rating has been saved.");
    } catch (error) {
      setNotice(errorMessage(error));
    }
  }

  async function submitReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedMovie || !userRating || !token) return;
    setBusy(true);
    try {
      await apiRequest<Review>(`/movies/${selectedMovie.id}/reviews`, {
        method: "POST",
        token,
        body: JSON.stringify({
          rating_id: userRating.id,
          content: reviewText.trim() || null,
        }),
      });
      setReviewText("");
      const updatedReviews = await apiRequest<Review[]>(
        `/movies/${selectedMovie.id}/reviews`,
      );
      setReviews(updatedReviews);
      setNotice("Your review has been published.");
    } catch (error) {
      setReviewError(errorMessage(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className={`catalog-page ${mode}-page`}>
      {mode === "discover" ? (
      <section className="hero">
        <div className="hero-image" style={{ backgroundImage: `url("${movieArtworkUrl(7)}")` }} />
        <div className="hero-scrim" />
        <div className="hero-content">
          <div className="eyebrow"><span className="eyebrow-line" /> A REPERTORY OF ODDITIES & OBSESSIONS</div>
          <h1>For the films<br />that get <em>under</em><br />your skin.</h1>
          <p>Cult favorites, midnight movies, and overlooked gems. For curious eyes and people who love the wonderfully weird.</p>
          <button className="hero-cta" onClick={() => document.getElementById("explore")?.scrollIntoView({ behavior: "smooth" })}>
            Dig through the collection <Icon name="arrow" size={17} />
          </button>
        </div>
        {featuredMovie && (
          <button className="featured-card" onClick={() => openMovie(featuredMovie)}>
            <div className="featured-cover" style={{ backgroundImage: `url("${movieArtworkUrl(0)}")` }}>
              <span className="featured-play"><Icon name="play" size={15} /></span>
            </div>
            <span className="featured-copy">
              <span className="featured-label">FROM THE BACK ROW</span>
              <strong>{featuredMovie.title}</strong>
              <span>{featuredMovie.release_year ?? "A must-watch"} <span className="dot">·</span> ★ {displayRating(featuredMovie)}</span>
            </span>
            <Icon name="arrow" size={17} />
          </button>
        )}
        <div className="hero-counter"><span>01</span><i /><span>04</span></div>
      </section>
      ) : (
        <section className="search-page-hero">
          <div className="eyebrow"><span className="eyebrow-line" /> THE ARCHIVE IS OPEN</div>
          <h1>Find something <em>strange.</em></h1>
          <p>Search cult favorites, midnight oddities, and the overlooked films that found their audience after dark.</p>
        </section>
      )}

      {mode === "discover" && <section className="intro-row" id="explore">
        <div>
          <div className="eyebrow eyebrow-dark"><span className="eyebrow-line" /> A SMALL, SLIGHTLY STRANGE FILM CLUB</div>
          <h2>Made for the <em>offbeat.</em></h2>
        </div>
        <p>Lost classics, midnight weirdness, and the ones that never made it to the multiplex.<br className="desktop-break" /> Pull up a chair.</p>
      </section>}

      <section className="discovery">
        {mode === "search" && (
          <form className="search-filter-form" onSubmit={applySearch}>
            <label className="search-title-field">Title or keyword
              <input value={searchText} onChange={(event) => setSearchText(event.target.value)} placeholder="Try a title, director, or obsession…" />
            </label>
            <label>Genre
              <select value={genreId ?? ""} onChange={(event) => setGenreId(event.target.value ? Number(event.target.value) : null)}>
                <option value="">All genres</option>
                {genres.map((genre) => <option value={genre.id} key={genre.id}>{genre.name}</option>)}
              </select>
            </label>
            <label>Release year
              <input type="number" min="1800" max="2100" value={releaseYear} onChange={(event) => setReleaseYear(event.target.value)} placeholder="Any year" />
            </label>
            <label>Minimum rating
              <select value={minRating} onChange={(event) => setMinRating(event.target.value)}>
                <option value="">Any rating</option>
                {[5, 6, 7, 8, 9].map((rating) => <option value={rating} key={rating}>{rating}+ out of 10</option>)}
              </select>
            </label>
            <button className="apply-search-button" type="submit">Search the archive <Icon name="arrow" size={16} /></button>
          </form>
        )}
        <div className="filter-row">
          <span className="section-kicker">{mode === "discover" ? "EVERY ACTIVE TITLE IN THE ARCHIVE" : "SORT YOUR RESULTS"}</span>
          <label className="sort-control">
            <span>Sort by</span>
            <select value={sortBy} onChange={(event) => { setSortBy(event.target.value); setPage(0); setLoading(true); }}>
              <option value="newest">Recently added</option>
              <option value="rating">Highest rated</option>
              <option value="rating_count">Most rated</option>
              <option value="title">Title A–Z</option>
              <option value="oldest">Oldest</option>
            </select>
          </label>
        </div>

        <div className="section-title-row">
          <div>
            <span className="section-kicker">{mode === "discover" ? "NO ALGORITHM. JUST GOOD VIBES." : "THE SEARCH RESULTS"}</span>
            <h3>{mode === "search" ? query ? `Results for “${query}”` : "Search the archive" : "The good stuff"}</h3>
          </div>
          <Link className="watchlist-link" href="/profile/watchlist">
            <Icon name="bookmark" size={16} /> My watchlist <span>{watchlist.length}</span>
          </Link>
        </div>

        {apiError && <div className="error-banner" role="alert">{apiError}. Check that the FastAPI server is running and NEXT_PUBLIC_API_URL points to it.</div>}

        <div className="movie-grid">
          {movies.map((movie, index) => (
            <article className="movie-card" key={`${movie.id}-${index}`} onClick={() => openMovie(movie)}>
              <div className="poster" style={{ backgroundImage: `url("${movieArtworkUrl(movie.id + index)}")` }}>
                <span className="poster-rating"><Icon name="star" size={13} /> {displayRating(movie)}</span>
                <button
                  className={watchlist.includes(movie.id) ? "save-button saved" : "save-button"}
                  aria-label={watchlist.includes(movie.id) ? "Remove from watchlist" : "Add to watchlist"}
                  onClick={(event) => { event.stopPropagation(); void toggleWatchlist(movie); }}
                >
                  <Icon name="bookmark" size={17} />
                </button>
                <span className="poster-open"><Icon name="play" size={14} /> View film</span>
              </div>
              <div className="movie-meta">
                <div className="movie-title-line"><h4>{movie.title}</h4><span>{movie.release_year ?? "—"}</span></div>
                <p>{movie.genres.slice(0, 2).map((genre) => genre.name).join(" · ") || "A story worth discovering"}</p>
              </div>
            </article>
          ))}
          {!loading && !apiError && movies.length === 0 && (
            <div className="empty-state"><span>◌</span><h4>No films found just yet.</h4><p>Try a different search or choose another genre.</p></div>
          )}
          {loading && movies.length === 0 && Array.from({ length: 6 }, (_, index) => <div className="skeleton-card" key={index}><div /><span /><i /></div>)}
        </div>
        {!apiError && hasMore && movies.length > 0 && (
          <div className="load-more-row">
            <button disabled={loading} onClick={() => { setLoading(true); setPage((current) => current + 1); }}>
              {loading ? "Finding more films…" : "Discover more films"} <Icon name="arrow" size={16} />
            </button>
          </div>
        )}
      </section>

      {notice && <div className="toast" role="status"><span>{notice}</span><button aria-label="Dismiss" onClick={() => setNotice("")}>×</button></div>}

      {selectedMovie && (
        <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelectedMovie(null); }}>
          <section className="detail-modal" role="dialog" aria-modal="true" aria-labelledby="detail-title">
            <button className="modal-close" aria-label="Close" onClick={() => setSelectedMovie(null)}><Icon name="close" /></button>
            <div className="detail-cover" style={{ backgroundImage: `url("${movieArtworkUrl(selectedMovie.id)}")` }} />
            <div className="detail-content">
              <div className="detail-overline">{selectedMovie.release_year ?? "A BmovieDb pick"} <span>·</span> {selectedMovie.duration_minutes ? `${selectedMovie.duration_minutes} min` : "Feature film"}</div>
              <h2 id="detail-title">{selectedMovie.title}</h2>
              <div className="detail-genres">{selectedMovie.genres.map((genre) => <span key={genre.id}>{genre.name}</span>)}</div>
              <p className="detail-description">{selectedMovie.description || "A story waiting to be discovered. Add this film to your watchlist, leave a rating, and share what you thought with the community."}</p>
              <div className="detail-rating"><span><Icon name="star" size={17} /> {displayRating(selectedMovie)}</span><small>{selectedMovie.rating_count} community ratings</small></div>
              <button className="detail-watchlist" onClick={() => void toggleWatchlist(selectedMovie)}>
                <Icon name="bookmark" size={17} /> {watchlist.includes(selectedMovie.id) ? "In your watchlist" : "Add to watchlist"}
              </button>
              <div className="your-rating">
                <strong>Your rating</strong>
                <div className="rating-picks">{Array.from({ length: 10 }, (_, index) => <button key={index + 1} aria-label={`Rate ${index + 1} out of 10`} className={(userRating?.rating ?? 0) >= index + 1 ? "rating-picked" : ""} onClick={() => void rateMovie(index + 1)}>{index + 1}</button>)}</div>
                {!user && <small>Sign in to rate and review films.</small>}
              </div>
              <div className="reviews-block">
                <div className="review-heading"><strong>Notes from the audience</strong><span>{reviews.length} reviews</span></div>
                {reviewError && <p className="inline-error">{reviewError}</p>}
                {reviews.slice(0, 3).map((review) => <div className="review-item" key={review.id}><span className="review-avatar">✳</span><p>{review.content || "Rated and added to their collection."}<small>Member #{review.user_id} · {new Date(review.created_at).toLocaleDateString()}</small></p></div>)}
                {userRating && !reviews.some((review) => review.user_id === user?.id) && (
                  <form className="review-form" onSubmit={submitReview}>
                    <textarea aria-label="Write a review" minLength={10} maxLength={5000} placeholder="What stayed with you? (10 characters minimum)" value={reviewText} onChange={(event) => setReviewText(event.target.value)} />
                    <button disabled={busy || (reviewText.length > 0 && reviewText.trim().length < 10)}>{busy ? "Publishing…" : "Share your thoughts"}</button>
                  </form>
                )}
              </div>
            </div>
          </section>
        </div>
      )}

    </main>
  );
}
