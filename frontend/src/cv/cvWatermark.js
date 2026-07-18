// Single source of truth for the CV watermark in preview and PDF export.
// Logo size and gap are separate, so changing spacing never scales the mark.
export const CV_WATERMARK = {
  src: '/watermark.png',
  opacity: 0.055,
  logoWidthPx: 72,
  logoHeightPx: 58,
  gapXPx: 62,
  gapYPx: 38,
  offsetXPx: 15,
  offsetYPx: 10,
  staggerXPx: 67,
  rotationDeg: -30,
  previewColumns: 8,
  previewTileCount: 720,
}
