/**
 * Hardware palette. Every color is a Catppuccin hue (palette v1.8.0,
 * https://github.com/catppuccin/palette) or a darkened version of one, so the
 * drawings match the site theme. Same in light and dark themes.
 */
export const HW = {
  ink: '#1e1e2e', // Mocha base: outlines
  board: '#3f4a8b', // Latte lavender #7287fd darkened 45%: the PCB
  boardTrace: '#7287fd', // Latte lavender: copper traces
  silk: '#eff1f5', // Latte base: silkscreen print
  edge: '#f9e2af', // Mocha yellow: the cream core under the board
  chip: '#313244', // Mocha surface0: chips and housings
  chipTop: '#45475a', // Mocha surface1
  metal: '#bcc0cc', // Latte surface1
  metalLight: '#dce0e8', // Latte crust
  beige: '#e6e9ef', // Latte mantle: connector plastic
  brass: '#df8e1d', // Latte yellow
  red: '#d20f39', // Latte red
  green: '#40a02b', // Latte green
  teal: '#c8402a', // vermilion red pen: callout dots (name kept from the ASMC port)
  cream: '#eff1f5', // Latte base: switch knobs
  ledOff: '#73081f', // Latte red darkened 45%
  ledOn: '#df8e1d', // Latte yellow: a lit LED
  ledOnTop: '#f9e2af', // Mocha yellow
  segOn: '#fe640b', // Latte peach
  segOff: '#2b2433', // faint ghost of an unlit segment
  segGood: '#a6e3a1', // Mocha green: a solved challenge
  rust: '#fe640b', // Latte peach
  steel: '#209fb5', // Latte sapphire
  shadow: 'rgba(30, 30, 46, 0.22)',
} as const;

function parseHex(hex: string): [number, number, number] {
  let h = hex.replace('#', '').trim();
  if (h.length === 3) h = h.split('').map((c) => c + c).join('');
  if (!/^[0-9a-fA-F]{6}$/.test(h)) throw new Error(`Bad color: ${hex}`);
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

const toHex2 = (n: number) => Math.round(Math.max(0, Math.min(255, n))).toString(16).padStart(2, '0');

/**
 * Darken (amount < 0) toward black or lighten (amount > 0) toward white.
 * amount is in −1..1, e.g. −0.15 is "15% darker".
 */
export function shade(hex: string, amount: number): string {
  const [r, g, b] = parseHex(hex);
  const t = amount < 0 ? 0 : 255;
  const p = Math.abs(amount);
  return `#${toHex2(r + (t - r) * p)}${toHex2(g + (t - g) * p)}${toHex2(b + (t - b) * p)}`;
}

/** WCAG relative luminance (0 = black, 1 = white). */
export function luminance(hex: string): number {
  const lin = (c: number) => {
    const s = c / 255;
    return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  };
  const [r, g, b] = parseHex(hex);
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

/** WCAG contrast ratio between two colors (1 to 21). */
export function contrast(a: string, b: string): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}
