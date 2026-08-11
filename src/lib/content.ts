import YAML from "yaml";
import { z } from "zod";

const yamlFiles = import.meta.glob("../content/**/*.yaml", {
  eager: true,
  query: "?raw",
  import: "default"
}) as Record<string, string>;

const linkSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  body: z.string().min(1),
  href: z.url(),
  label: z.string().min(1)
});

const itemSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  body: z.string().min(1),
  badge: z.string().optional(),
  href: z.url().optional(),
  linkLabel: z.string().optional()
});

const sectionSchema = z.object({
  id: z.string().min(1),
  number: z.string().min(1),
  kicker: z.string().min(1),
  title: z.string().min(1),
  intro: z.string().min(1),
  tone: z.enum(["light", "soft", "dark"]).default("light"),
  items: z.array(itemSchema).min(1)
});

const guideSchema = z.object({
  locale: z.enum(["fi", "en"]),
  languageName: z.string().min(1),
  meta: z.object({
    title: z.string().min(1),
    description: z.string().min(1),
    updated: z.string().regex(/^\d{4}-\d{2}-\d{2}$/)
  }),
  navigation: z.object({
    guide: z.string().min(1),
    levi: z.string().min(1),
    language: z.string().min(1),
    menu: z.string().min(1)
  }),
  hero: z.object({
    eyebrow: z.string().min(1),
    title: z.string().min(1),
    subtitle: z.string().min(1),
    intro: z.string().min(1),
    primaryAction: z.string().min(1),
    secondaryAction: z.string().min(1),
    locationLabel: z.string().min(1)
  }),
  quickTitle: z.string().min(1),
  quickIntro: z.string().min(1),
  quickActions: z.array(z.object({
    id: z.string().min(1),
    number: z.string().min(1),
    title: z.string().min(1),
    detail: z.string().min(1)
  })).min(3),
  sections: z.array(sectionSchema).min(4),
  emergency: z.object({
    eyebrow: z.string().min(1),
    title: z.string().min(1),
    number: z.literal("112"),
    body: z.string().min(1),
    addressLabel: z.string().min(1),
    address: z.literal("Keskitaalo 33B, 99130 Sirkka"),
    steps: z.array(z.string().min(1)).min(3),
    sourceLabel: z.string().min(1),
    sourceHref: z.url()
  }),
  contact: z.object({
    eyebrow: z.string().min(1),
    title: z.string().min(1),
    body: z.string().min(1),
    note: z.string().min(1)
  }),
  footer: z.object({
    updatedLabel: z.string().min(1),
    privacy: z.string().min(1)
  })
});

const leviSchema = z.object({
  locale: z.enum(["fi", "en"]),
  languageName: z.string().min(1),
  meta: z.object({
    title: z.string().min(1),
    description: z.string().min(1),
    updated: z.string().regex(/^\d{4}-\d{2}-\d{2}$/)
  }),
  navigation: guideSchema.shape.navigation,
  hero: z.object({
    eyebrow: z.string().min(1),
    title: z.string().min(1),
    intro: z.string().min(1),
    backLabel: z.string().min(1)
  }),
  seasonsTitle: z.string().min(1),
  seasonsIntro: z.string().min(1),
  seasons: z.array(z.object({
    id: z.string().min(1),
    number: z.string().min(1),
    title: z.string().min(1),
    body: z.string().min(1),
    accent: z.enum(["snow", "sun", "ember", "night"])
  })).length(4),
  linksTitle: z.string().min(1),
  linksIntro: z.string().min(1),
  links: z.array(linkSchema).min(3),
  nature: z.object({
    eyebrow: z.string().min(1),
    title: z.string().min(1),
    intro: z.string().min(1),
    items: z.array(itemSchema).min(3)
  }),
  footer: guideSchema.shape.footer
});

export type GuideContent = z.infer<typeof guideSchema>;
export type LeviContent = z.infer<typeof leviSchema>;
export type Locale = "fi" | "en";

function readYaml(relativePath: string): unknown {
  const key = `../content/${relativePath}`;
  const source = yamlFiles[key];
  if (!source) {
    throw new Error(`Missing content file: ${relativePath}`);
  }
  return YAML.parse(source);
}

export function loadGuide(locale: Locale): GuideContent {
  return guideSchema.parse(readYaml(`${locale}/guide.yaml`));
}

export function loadLevi(locale: Locale): LeviContent {
  return leviSchema.parse(readYaml(`${locale}/levi.yaml`));
}

function assertSameIds(label: string, left: string[], right: string[]): void {
  if (left.join("|") !== right.join("|")) {
    throw new Error(`${label} translation IDs differ: ${left.join(", ")} / ${right.join(", ")}`);
  }
}

export function validateTranslationParity(): void {
  const fiGuide = loadGuide("fi");
  const enGuide = loadGuide("en");
  const fiLevi = loadLevi("fi");
  const enLevi = loadLevi("en");

  assertSameIds("Quick actions", fiGuide.quickActions.map((item) => item.id), enGuide.quickActions.map((item) => item.id));
  assertSameIds("Guide sections", fiGuide.sections.map((item) => item.id), enGuide.sections.map((item) => item.id));
  fiGuide.sections.forEach((section, index) => {
    assertSameIds(`Guide section ${section.id}`, section.items.map((item) => item.id), enGuide.sections[index].items.map((item) => item.id));
  });
  assertSameIds("Levi seasons", fiLevi.seasons.map((item) => item.id), enLevi.seasons.map((item) => item.id));
  assertSameIds("Levi links", fiLevi.links.map((item) => item.id), enLevi.links.map((item) => item.id));
  assertSameIds("Nature items", fiLevi.nature.items.map((item) => item.id), enLevi.nature.items.map((item) => item.id));
}

export function withBase(path: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalized}`.replace(/\/+/g, "/");
}

validateTranslationParity();
