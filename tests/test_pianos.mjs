import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";
import { createCanvas, loadImage } from "../renderer/node_modules/canvas/index.js";

test("piano images highlight the exact key across octave boundaries", async () => {
  const directory = mkdtempSync(join(tmpdir(), "mnm-pianos-"));
  const pitches = ["C1", "B3", "C4", "C6"];
  try {
    execFileSync("node", ["renderer/render_pianos.mjs", directory], { input: JSON.stringify(pitches) });
    for (const pitch of pitches) {
      const image = await loadImage(readFileSync(join(directory, `mnm-piano-${pitch}.png`)));
      assert.equal(image.width, 1200);
      assert.equal(image.height, 400);
      const context = createCanvas(1200, 400).getContext("2d");
      context.drawImage(image, 0, 0);
      const target = 2 + (Number(pitch[1]) - 1) * 7 + "CDEFGAB".indexOf(pitch[0]);
      for (let key = 0; key < 52; key++) {
        const x = Math.floor(24 + (key + 0.5) * 1152 / 52);
        const [r, g, b] = context.getImageData(x, 132, 1, 1).data;
        assert.equal(b > 180 && r < 80 && g < 150, key === target, `${pitch}: white key ${key}`);
      }
    }
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
