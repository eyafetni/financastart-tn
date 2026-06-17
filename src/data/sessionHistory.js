/**
 * Simulated session history data.
 * In a real app this would come from a backend/localStorage.
 * Scores are derived from the same logic as dataAdapter.js,
 * showing a progression trajectory for the entrepreneur.
 */
export const sessionHistory = [
  {
    id: "sess-001",
    date: "2026-03-10",
    stade_reel: "Ideation",
    stade_percu: "Ideation",
    gap_detecte: false,
    financingScore: 22,
    status: "non_bankable",
    scores: {
      market: 30,
      commercial: 10,
      innovation: 60,
      scalability: 20,
      green: 40,
    },
  },
  {
    id: "sess-002",
    date: "2026-04-05",
    stade_reel: "Validation",
    stade_percu: "Validation",
    gap_detecte: false,
    financingScore: 31,
    status: "non_bankable",
    scores: {
      market: 38,
      commercial: 15,
      innovation: 68,
      scalability: 28,
      green: 50,
    },
  },
  {
    id: "sess-003",
    date: "2026-05-12",
    stade_reel: "Structuration",
    stade_percu: "Structuration",
    gap_detecte: false,
    financingScore: 38,
    status: "non_bankable",
    scores: {
      market: 42,
      commercial: 18,
      innovation: 75,
      scalability: 32,
      green: 55,
    },
  },
  {
    id: "sess-004",
    date: "2026-06-16",
    stade_reel: "Structuration",
    stade_percu: "Fundraising",
    gap_detecte: true,
    financingScore: 42,
    status: "non_bankable",
    scores: {
      market: 45,
      commercial: 20,
      innovation: 80,
      scalability: 35,
      green: 60,
    },
    isCurrent: true,
  },
];

export const scoreKeys = ["market", "commercial", "innovation", "scalability", "green"];

export const scoreLabels = {
  fr: {
    market: "Marché",
    commercial: "Commercial",
    innovation: "Innovation",
    scalability: "Scalabilité",
    green: "Impact Vert",
  },
  ar: {
    market: "السوق",
    commercial: "التجاري",
    innovation: "الابتكار",
    scalability: "التوسع",
    green: "الأثر البيئي",
  },
};

export const scoreColors = {
  market: "#06b6d4",       // cyan-500
  commercial: "#6366f1",   // indigo-500
  innovation: "#8b5cf6",   // violet-500
  scalability: "#f59e0b",  // amber-500
  green: "#10b981",        // emerald-500
};
