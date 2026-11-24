// OSMD needs a DOM and canvas even when rendering without a browser.
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { JSDOM } from "jsdom";

const dom = new JSDOM("<!doctype html><div id='score'></div>");
globalThis.window = dom.window;
globalThis.document = dom.window.document;
for (const name of ["HTMLElement", "HTMLAnchorElement", "DOMParser", "Node", "XMLHttpRequest"]) {
  globalThis[name] = dom.window[name];
}
const { default: OSMD } = await import("opensheetmusicdisplay");
const container = document.getElementById("score");
// Render extra pixels without changing the notation layout.
const resolution = 3;
Object.defineProperty(container, "offsetWidth", { value: 640 * resolution });
const osmd = new OSMD.OpenSheetMusicDisplay(container, {
  autoResize: false,
  backend: "canvas",
  drawingParameters: "compact",
  drawTitle: false,
  drawComposer: false,
  drawPartNames: false,
  drawMeasureNumbers: false,
  drawTimeSignatures: false,
  pageBackgroundColor: "#FFFFFF",
});
osmd.Zoom = 2 * resolution;
osmd.EngravingRules.PageTopMargin = 3;
osmd.EngravingRules.PageTopMarginNarrow = 3;
osmd.EngravingRules.PageBottomMargin = 3;

const output = process.argv[2];
if (!output) throw new Error("Usage: node render_notes.mjs OUTPUT_DIR < jobs.json");
const jobs = JSON.parse(readFileSync(0, "utf8"));
mkdirSync(output, { recursive: true });
const rendered = [];
for (const { filename, xml, showTimeSignature = false } of jobs) {
  if (!/^mnm-(?:note-(?:treble|bass)-[A-G][0-9]|(?:rhythm|meter)-[a-z0-9]+(?:-[a-z0-9]+)*)\.png$/.test(filename)) {
    throw new Error(`Invalid image filename: ${filename}`);
  }
  osmd.setOptions({ drawTimeSignatures: showTimeSignature });
  await osmd.load(xml);
  osmd.render();
  const canvas = container.querySelector("canvas");
  if (!canvas || !canvas.width || !canvas.height) {
    throw new Error(`OSMD did not render ${filename}`);
  }
  // Crop OSMD's page whitespace, keeping padding around every clef and note.
  const context = canvas.getContext("2d");
  const { data } = context.getImageData(0, 0, canvas.width, canvas.height);
  let left = canvas.width, top = canvas.height, right = -1, bottom = -1;
  for (let y = 0; y < canvas.height; y++) {
    for (let x = 0; x < canvas.width; x++) {
      const i = (y * canvas.width + x) * 4;
      if (data[i + 3] > 0 && Math.min(data[i], data[i + 1], data[i + 2]) < 240) {
        left = Math.min(left, x); right = Math.max(right, x);
        top = Math.min(top, y); bottom = Math.max(bottom, y);
      }
    }
  }
  if (right < left) throw new Error(`Empty notation image: ${filename}`);
  if (top === 0 || bottom === canvas.height - 1) {
    throw new Error(`Notation touches the page boundary: ${filename}`);
  }
  const padding = 24 * resolution;
  const cropped = document.createElement("canvas");
  cropped.width = right - left + 1 + 2 * padding;
  cropped.height = bottom - top + 1 + 2 * padding;
  const cropContext = cropped.getContext("2d");
  cropContext.fillStyle = "white";
  cropContext.fillRect(0, 0, cropped.width, cropped.height);
  cropContext.drawImage(canvas, left, top, right - left + 1, bottom - top + 1,
    padding, padding, right - left + 1, bottom - top + 1);
  rendered.push({ filename, canvas: cropped });
}
// Equal canvases prevent Anki's width:100% styling from magnifying shorter bars.
const rhythms = rendered.filter(({ filename }) => filename.startsWith("mnm-rhythm-"));
const meters = rendered.filter(({ filename }) => filename.startsWith("mnm-meter-"));
const meterWidth = Math.max(0, ...meters.map(({ canvas }) => canvas.width));
const meterHeight = Math.max(0, ...meters.map(({ canvas }) => canvas.height));
const rhythmWidth = Math.max(0, ...rhythms.map(({ canvas }) => canvas.width));
const rhythmHeight = Math.max(0, ...rhythms.map(({ canvas }) => canvas.height));
for (const { filename, canvas } of rendered) {
  let result = canvas;
  if (filename.startsWith("mnm-rhythm-") || filename.startsWith("mnm-meter-")) {
    const isMeter = filename.startsWith("mnm-meter-");
    result = document.createElement("canvas");
    result.width = isMeter ? meterWidth : rhythmWidth;
    result.height = isMeter ? meterHeight : rhythmHeight;
    const context = result.getContext("2d");
    context.fillStyle = "white";
    context.fillRect(0, 0, result.width, result.height);
    context.drawImage(canvas, Math.floor((result.width - canvas.width) / 2),
      Math.floor((result.height - canvas.height) / 2));
  }
  const png = result.toDataURL("image/png").split(",")[1];
  writeFileSync(join(output, filename), Buffer.from(png, "base64"));
}
dom.window.close();
