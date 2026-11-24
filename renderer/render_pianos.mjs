// Build static answer images; no browser or JavaScript is needed in Anki.
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { createHTMLWindow } from "svgdom";
import { createCanvas, loadImage } from "canvas";

globalThis.window = createHTMLWindow();
globalThis.document = window.document;
const { default: { Instrument } } = await import("piano-chart");

const output = process.argv[2];
if (!output) throw new Error("Usage: node render_pianos.mjs OUTPUT_DIR < pitches.json");
const pitches = JSON.parse(readFileSync(0, "utf8"));
mkdirSync(output, { recursive: true });

async function keyboard(pitch, startOctave, startNote, endOctave, endNote, width, height) {
  const container = document.createElement("div");
  document.body.appendChild(container);
  Object.defineProperties(container, { clientWidth: { value: width }, clientHeight: { value: height } });
  const instrument = new Instrument(container, {
    startOctave, startNote, endOctave, endNote,
    showOctaveNumbers: true,
    showNoteNames: "onpress",
    keyPressStyle: "vivid",
    vividKeyPressColor: "#2563eb",
  });
  try {
    instrument.create();
    if (pitch !== "C4" && startOctave <= 4 && endOctave >= 4) {
      instrument.keyDown("C4");
      for (const key of container.querySelectorAll('[fill="#2563eb"]')) {
        key.setAttribute("fill", "#e2e8f0");
      }
    }
    instrument.keyDown(pitch);
    const svg = container.querySelector("svg");
    if (!svg) throw new Error("Piano chart did not produce SVG");
    return await loadImage(Buffer.from(svg.outerHTML));
  } finally {
    instrument.destroy();
    container.remove();
  }
}

for (const pitch of pitches) {
  if (!/^[A-G][1-6]$/.test(pitch)) throw new Error("Invalid piano pitch");
  const octave = Number(pitch.slice(1));
  const canvas = createCanvas(1200, 400);
  const context = canvas.getContext("2d");
  context.fillStyle = "white";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#111827";
  context.font = "30px Arial";
  context.textAlign = "center";
  context.fillText(`${pitch} on an 88-key piano · Middle C = C4`, 600, 36);
  context.drawImage(await keyboard(pitch, 0, "A", 8, "C", 1152, 170), 24, 50, 1152, 105);
  context.fillText(`Close-up: C${octave}–C${octave + 2}`, 600, 190);
  const detail = await keyboard(pitch, octave, "C", octave + 2, "C", 720, 310);
  context.drawImage(detail, 240, 204, 720, 180);
  writeFileSync(join(output, `mnm-piano-${pitch}.png`), canvas.toBuffer("image/png"));
}
