// Option lists for the Analyze page. These are only choices for the writer (UI),
// not checks. All checking is done by the backend.

export const TYPES = [
  { id: "instagram_post", label: "Instagram post" },
  { id: "email", label: "Email" },
  { id: "blog", label: "Blog" },
  { id: "ad", label: "Ad" },
  { id: "other", label: "Other" },
];

export const SAMPLES = [
  { label: "Bold claim", type: "ad", text: "ABC App is the number one app in the world and we guarantee 100% success!" },
  { label: "Wrong facts", type: "instagram_post", text: "ABC App now supports 25 languages and is used by 2,000 teams, starting at Rs 499 per month." },
  { label: "Casual tone", type: "email", text: "Hey guys!! Our new sale is gonna be insane, don't miss out lol." },
  { label: "Clean post", type: "instagram_post", text: "ABC App helps teams create reports quickly. Plans start at Rs 549 per month." },
];

export const INTENT_GROUPS = [
  { id: "awareness", label: "Awareness", items: ["Announce a new product", "Launch a feature", "Introduce the brand", "Share company news"] },
  { id: "sales", label: "Sales", items: ["Promote a discount", "Drive purchases", "Announce a limited offer", "Upsell an existing plan"] },
  { id: "trust", label: "Trust", items: ["Build trust", "Share a customer story", "Explain how it works", "Show our values"] },
  { id: "engage", label: "Engagement", items: ["Get sign-ups", "Invite to an event", "Start a conversation", "Win back past customers"] },
  { id: "inform", label: "Inform", items: ["Share a tip", "Give an update", "Answer a common question", "Thank our customers"] },
];

// brand: true marks the fonts and colours listed in brand_kit.json
export const FONTS = [
  { label: "Inter", css: '"Inter", system-ui, sans-serif', kind: "Clean sans", brand: true },
  { label: "Poppins", css: '"Poppins", system-ui, sans-serif', kind: "Rounded sans", brand: true },
  { label: "Montserrat", css: '"Montserrat", system-ui, sans-serif', kind: "Modern sans" },
  { label: "Cormorant Garamond", css: '"Cormorant Garamond", Georgia, serif', kind: "Elegant serif" },
  { label: "Playfair Display", css: '"Playfair Display", Georgia, serif', kind: "High-contrast serif" },
  { label: "DM Serif Display", css: '"DM Serif Display", Georgia, serif', kind: "Display serif" },
  { label: "Lora", css: '"Lora", Georgia, serif', kind: "Readable serif" },
  { label: "Dancing Script", css: '"Dancing Script", cursive', kind: "Script" },
  { label: "Space Mono", css: '"Space Mono", monospace', kind: "Monospace" },
  { label: "Georgia", css: "Georgia, serif", kind: "System serif" },
];

export const WEIGHTS = [
  { v: "400", label: "Regular" },
  { v: "500", label: "Medium" },
  { v: "700", label: "Bold" },
];

export const COLORS = [
  { name: "Brand Blue", hex: "#1D4ED8", brand: true },
  { name: "Ink", hex: "#111827", brand: true },
  { name: "Soft Gray", hex: "#F3F4F6", brand: true },
  { name: "Accent Orange", hex: "#F97316", brand: true },
  { name: "Charcoal", hex: "#2B2B2B" },
  { name: "Black", hex: "#000000" },
  { name: "White", hex: "#FFFFFF" },
  { name: "Navy", hex: "#1F2A44" },
  { name: "Forest", hex: "#2F4F3E" },
  { name: "Rose", hex: "#C9877F" },
  { name: "Gold", hex: "#B8923A" },
];