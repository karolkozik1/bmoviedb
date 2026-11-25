const posters = [
  "photo-1489599849927-2ee91cede3ba",
  "photo-1440404653325-ab127d49abc1",
  "photo-1517604931442-7e0c8ed2963c",
  "photo-1478720568477-152d9b164e26",
  "photo-1485846234645-a62644f84728",
  "photo-1446776811953-b23d57bd21aa",
  "photo-1536440136628-849c177e76a1",
  "photo-1500530855697-b586d89ba3ee",
  "photo-1519608487953-e999c86e7455",
  "photo-1500534623283-312aade485b7",
  "photo-1470252649378-9c29740c9fa8",
  "photo-1500534314209-a25ddb2bd429",
];

export function movieArtworkUrl(index: number) {
  return `https://images.unsplash.com/${posters[index % posters.length]}?auto=format&fit=crop&w=900&q=82`;
}
