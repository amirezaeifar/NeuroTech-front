/**
 * useDeviceArt — flat 2D line-art "device renders", one per product category.
 *
 * No product photography ships with the project, so each catalogue item is
 * represented by a crisp, scalable line illustration of a clinical console with
 * a modality-specific signal on its screen. Every entry is split into a `frame`
 * group (the device body, drawn in a muted ink/silver) and a `signal` group (the
 * on-screen trace, drawn in gold) so the cards and the detail hero can render a
 * two-tone "blueprint" look that inverts cleanly between light and dark themes.
 *
 * All paths live in a shared `0 0 48 36` viewBox with fill:none and inherit
 * stroke colour from the consuming component, so they stay sharp at any size and
 * read as flat, technical schematics — never faux-3D renders.
 */

// Shared clinical-console chassis: body, recessed screen, stand and foot.
const CHASSIS = ['M5 4h38v22H5z', 'M8 7h32v16H8z', 'M21 26v5', 'M14 31h20']

const ART = {
  // Electroencephalography — three stacked, out-of-phase brain-wave traces.
  eeg: {
    frame: CHASSIS,
    signal: [
      'M11 12q2-3 4 0t4 0 4 0 4 0 4 0 4 0',
      'M11 16q2 3 4 0t4 0 4 0 4 0 4 0 4 0',
      'M11 20q2-3 4 0t4 0 4 0 4 0 4 0 4 0',
    ],
  },
  // Electromyography — a single high-amplitude motor-unit burst.
  emg: {
    frame: CHASSIS,
    signal: ['M10 16h4l2-7 2 13 3-10 2 6 2-2h6'],
  },
  // Neurostimulation — paired lobes with a directed stimulation pulse.
  neurostim: {
    frame: CHASSIS,
    signal: ['M18 16a6 6 0 0 1 12 0', 'M18 16a6 6 0 0 0 12 0', 'M24 10v12', 'M30 13l3-2', 'M30 19l3 2'],
  },
  // Monitoring — an ECG-style vital trace with a readout bar.
  monitoring: {
    frame: CHASSIS,
    signal: ['M10 16h5l2-5 2 10 2-7 2 2h6', 'M33 12v8'],
  },
}

export function deviceArt(category) {
  return ART[category] || ART.eeg
}
