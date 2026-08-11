import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import YAML from "yaml";

type Item = { id: string };
type Section = Item & { items: Item[] };

function read(relativePath: string): Record<string, unknown> {
  return YAML.parse(readFileSync(resolve(relativePath), "utf8"));
}

function ids(items: Item[]): string[] {
  return items.map((item) => item.id);
}

function same(label: string, left: string[], right: string[]): void {
  if (left.join("|") !== right.join("|")) {
    throw new Error(`${label} translation IDs differ: ${left.join(", ")} / ${right.join(", ")}`);
  }
}

const fiGuide = read("src/content/fi/guide.yaml") as {
  quickActions: Item[];
  sections: Section[];
};
const enGuide = read("src/content/en/guide.yaml") as {
  quickActions: Item[];
  sections: Section[];
};
const fiLevi = read("src/content/fi/levi.yaml") as {
  seasons: Item[];
  links: Item[];
  nature: { items: Item[] };
};
const enLevi = read("src/content/en/levi.yaml") as {
  seasons: Item[];
  links: Item[];
  nature: { items: Item[] };
};

same("Quick actions", ids(fiGuide.quickActions), ids(enGuide.quickActions));
same("Guide sections", ids(fiGuide.sections), ids(enGuide.sections));
fiGuide.sections.forEach((section, index) => {
  same(`Guide section ${section.id}`, ids(section.items), ids(enGuide.sections[index].items));
});
same("Levi seasons", ids(fiLevi.seasons), ids(enLevi.seasons));
same("Levi links", ids(fiLevi.links), ids(enLevi.links));
same("Nature items", ids(fiLevi.nature.items), ids(enLevi.nature.items));

console.log("Content translation parity is valid.");
