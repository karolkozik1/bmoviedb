import MovieBrowser from "@/components/MovieBrowser";

type SearchPageProps = {
  searchParams: Promise<{ q?: string | string[] }>;
};

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const { q } = await searchParams;
  const initialQuery = Array.isArray(q) ? q[0] ?? "" : q ?? "";

  return <MovieBrowser key={initialQuery} mode="search" initialQuery={initialQuery} />;
}
