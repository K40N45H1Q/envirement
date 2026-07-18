// Print-only CSS used inside the hidden iframe before browser printing.
// The builder owns when printing starts; this file owns how the print iframe looks.
export const getPrintableStyles = () => `
  @page {
    size: A4;
    margin: 0;
  }

  * {
    box-sizing: border-box !important;
  }

  html,
  body {
    width: 210mm !important;
    height: 297mm !important;
    margin: 0 !important;
    padding: 0 !important;
    background: #fff !important;
    overflow: hidden !important;
  }

  body {
    display: block !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    font-family: var(--cv-font-family) !important;
  }

  .cv-document {
    --cv-green: #149447;
    --cv-green-dark: #0f7f3c;
    --cv-ink: #101828;
    --cv-muted: #667085;
    --cv-line: #d9dee7;
    --cv-soft: #f3fbf6;
    width: 210mm !important;
    min-width: 210mm !important;
    max-width: 210mm !important;
    height: 297mm !important;
    min-height: 297mm !important;
    max-height: 297mm !important;
    margin: 0 !important;
    padding: 10mm 12mm 8mm !important;
    border: 0 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    background: #fff !important;
    color: var(--cv-ink) !important;
    position: relative !important;
    isolation: isolate !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 0 !important;
    font-family: var(--cv-font-family) !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  .cv-document.cv-document--pdf {
    background: transparent !important;
  }

  .cv-document.cv-document--pdf .cv-watermark {
    display: none !important;
  }

  .cv-watermark {
    position: absolute !important;
    inset: 0 !important;
    z-index: 1 !important;
    pointer-events: none !important;
    overflow: hidden !important;
    background: none !important;
    transform: none !important;
  }

  .cv-watermark img {
    display: block !important;
    object-fit: contain !important;
    transform-origin: center !important;
  }

  .cv-document > :not(.cv-watermark) {
    position: relative !important;
    z-index: 2 !important;
  }

  .cv-header,
  .cv-top,
  .cv-footer {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 9mm !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
  }

  .cv-header > *,
  .cv-top > *,
  .cv-footer > * {
    min-width: 0 !important;
  }

  .cv-header {
    min-height: 15mm !important;
    padding-bottom: 5mm !important;
    border-bottom: 0.35mm solid var(--cv-line) !important;
  }

  .cv-brand {
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
    gap: 3mm !important;
    min-width: 0 !important;
    color: var(--cv-ink) !important;
    background: transparent !important;
  }

  .cv-header .cv-brand__logo,
  .cv-header .cv-brand__logo svg {
    width: 34mm !important;
    max-width: 34mm !important;
    height: 9mm !important;
    max-height: 9mm !important;
    object-fit: contain !important;
    object-position: left center !important;
    display: block !important;
    flex: 0 0 auto !important;
    background: transparent !important;
  }

  .cv-brand small {
    display: block !important;
    color: var(--cv-muted) !important;
    font-size: 6.2pt !important;
    line-height: 1 !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    white-space: nowrap !important;
  }

  .cv-verified {
    display: inline-flex !important;
    align-items: center !important;
    gap: 2.5mm !important;
    color: var(--cv-green) !important;
    flex: 0 0 auto !important;
    background: transparent !important;
  }

  .cv-verified > i {
    font-size: 15pt !important;
  }

  .cv-verified > span {
    display: grid !important;
    gap: 0.8mm !important;
    text-align: right !important;
    background: transparent !important;
  }

  .cv-verified strong {
    color: var(--cv-ink) !important;
    font-size: 8.2pt !important;
    line-height: 1 !important;
  }

  .cv-verified small {
    color: var(--cv-green-dark) !important;
    font-size: 6.3pt !important;
    line-height: 1 !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
  }

  .cv-top {
    padding: 7mm 0 6mm !important;
    border-bottom: 0.35mm solid var(--cv-line) !important;
    align-items: flex-start !important;
    justify-content: space-between !important;
  }

  .cv-person {
    display: grid !important;
    grid-template-columns: 18mm minmax(0, 1fr) !important;
    gap: 4.2mm !important;
    align-items: start !important;
    flex: 1 1 auto !important;
    min-width: 0 !important;
  }

  .cv-top-additional {
    flex: 1 1 45mm !important;
    min-width: 35mm !important;
    padding: 17.5mm 2mm 0 !important;
  }

  .cv-avatar {
    width: 18mm !important;
    height: 18mm !important;
    display: grid !important;
    place-items: center !important;
    overflow: hidden !important;
    border-radius: 50% !important;
    background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%) !important;
    color: #fff !important;
    font-size: 10pt !important;
    line-height: 1 !important;
    font-weight: 900 !important;
  }

  .cv-avatar img {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    display: block !important;
  }

  .cv-person h1 {
    margin: 0 !important;
    color: #05070a !important;
    font-size: 25pt !important;
    line-height: 0.95 !important;
    letter-spacing: -0.055em !important;
    max-width: 126mm !important;
    overflow-wrap: anywhere !important;
  }

  .cv-person p {
    margin: 2mm 0 3.2mm !important;
    color: var(--cv-green) !important;
    font-size: 10.3pt !important;
    line-height: 1.1 !important;
    font-weight: 800 !important;
  }

  .cv-contact-list,
  .cv-list,
  .cv-extra-list {
    margin: 0 !important;
    padding: 0 !important;
    list-style: none !important;
  }

  .cv-contact-list {
    display: grid !important;
    gap: 1.4mm !important;
  }

  .cv-contact-list li {
    display: flex !important;
    align-items: center !important;
    gap: 2mm !important;
    color: var(--cv-ink) !important;
    font-size: 7.7pt !important;
    line-height: 1.2 !important;
    min-width: 0 !important;
  }

  .cv-contact-list span,
  .cv-extra-list span,
  .cv-list li,
  .cv-sector span {
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
    white-space: pre-wrap !important;
  }

  .cv-contact-list i,
  .cv-extra-list i {
    width: 4mm !important;
    color: var(--cv-green) !important;
    text-align: center !important;
    flex: 0 0 auto !important;
  }

  .cv-id {
    display: grid !important;
    justify-items: center !important;
    align-self: flex-start !important;
    gap: 1mm !important;
    color: var(--cv-ink) !important;
    flex: 0 0 auto !important;
  }

  .cv-id small {
    margin-top: 1.2mm !important;
    color: var(--cv-green) !important;
    font-size: 6.2pt !important;
    line-height: 1 !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
  }

  .cv-id > strong {
    font-size: 7.5pt !important;
    line-height: 1 !important;
  }

  .cv-qr {
    position: relative !important;
    width: 5.5rem !important;
    height: 5.5rem !important;
    display: block !important;
    padding: 0.24rem !important;
    border: 0.0625rem solid var(--cv-line) !important;
    border-radius: 0.32rem !important;
    background: #fff !important;
    overflow: hidden !important;
  }

  .cv-qr img {
    width: 100% !important;
    height: 100% !important;
    max-width: 100% !important;
    display: block !important;
    margin: 0 !important;
    object-fit: contain !important;
    object-position: center !important;
  }

  .cv-qr-cell {
    background: transparent !important;
    border-radius: 0.15mm !important;
  }

  .cv-qr-cell--active {
    background: #111 !important;
  }

  .cv-qr strong {
    position: absolute !important;
    inset: 50% auto auto 50% !important;
    width: 6.4mm !important;
    height: 6.4mm !important;
    display: grid !important;
    place-items: center !important;
    transform: translate(-50%, -50%) !important;
    border-radius: 1mm !important;
    background: #111 !important;
    color: var(--cv-green) !important;
    font-size: 5.4pt !important;
    line-height: 1 !important;
    font-weight: 900 !important;
  }

  .cv-body {
    display: grid !important;
    grid-template-columns: minmax(0, 1.34fr) minmax(45mm, 0.82fr) !important;
    gap: 7mm !important;
    padding-top: 6mm !important;
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow: hidden !important;
  }

  .cv-main {
    min-height: 0 !important;
    overflow: hidden !important;
    padding-right: 7mm !important;
    border-right: 0.35mm solid var(--cv-line) !important;
  }

  .cv-aside {
    min-height: 0 !important;
    overflow: hidden !important;
  }

  .cv-body > .cv-flow-item--full {
    grid-column: 1 / -1 !important;
  }

  .cv-document--balanced .cv-body {
    row-gap: 0 !important;
    grid-auto-rows: max-content !important;
    align-content: start !important;
  }

  .cv-document--balanced .cv-flow-item--work-split {
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
    border-bottom: 0 !important;
  }

  .cv-flow-item--work-continuation {
    padding-right: 0 !important;
  }

  .cv-flow-item--work-continuation .cv-summary-text {
    text-align: justify !important;
    text-align-last: left !important;
    hyphens: auto !important;
  }

  .cv-entry__description {
    text-align: justify !important;
    text-align-last: left !important;
    hyphens: auto !important;
  }

  .cv-section {
    padding-bottom: 4mm !important;
    margin-bottom: 4mm !important;
    border-bottom: 0.35mm solid var(--cv-line) !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .cv-section:last-child {
    margin-bottom: 0 !important;
  }

  .cv-section h2 {
    margin: 0 0 2.3mm !important;
    color: var(--cv-green) !important;
    font-size: 8.2pt !important;
    line-height: 1.1 !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
  }

  .cv-section p {
    margin: 0 !important;
    color: var(--cv-ink) !important;
    font-size: 7.6pt !important;
    line-height: 1.4 !important;
  }

  .cv-summary-text {
    display: block !important;
    overflow: visible !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
    white-space: pre-wrap !important;
  }

  .cv-section p + p {
    margin-top: 2mm !important;
  }

  .cv-list {
    display: grid !important;
    gap: 1.45mm !important;
  }

  .cv-list li {
    position: relative !important;
    padding-left: 3.7mm !important;
    color: var(--cv-ink) !important;
    font-size: 7.4pt !important;
    line-height: 1.24 !important;
  }

  .cv-list li::before {
    content: '' !important;
    position: absolute !important;
    top: 3.1mm !important;
    left: 0.55mm !important;
    width: 1mm !important;
    height: 1mm !important;
    border-radius: 50% !important;
    background: var(--cv-green) !important;
  }

  .cv-sector-grid {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 1.8mm !important;
  }

  .cv-sector {
    display: flex !important;
    align-items: center !important;
    gap: 1.8mm !important;
    min-height: 8.5mm !important;
    padding: 1.8mm 2.1mm !important;
    border: 0.35mm solid #d9f2e2 !important;
    border-radius: 2.5mm !important;
    background: var(--cv-soft) !important;
    color: var(--cv-ink) !important;
    font-size: 7pt !important;
    line-height: 1.16 !important;
    font-weight: 800 !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .cv-sector i {
    color: var(--cv-green) !important;
    flex: 0 0 auto !important;
  }

  .cv-extra-list {
    display: grid !important;
    gap: 1.8mm !important;
  }

  .cv-extra-list li {
    display: grid !important;
    grid-template-columns: 4.2mm minmax(0, 1fr) !important;
    gap: 1.7mm !important;
    align-items: start !important;
    color: var(--cv-ink) !important;
    font-size: 7.2pt !important;
    line-height: 1.25 !important;
  }

  .cv-more-item {
    color: var(--cv-muted) !important;
    font-weight: 800 !important;
  }

  .cv-footer {
    margin-top: auto !important;
    padding-top: 3mm !important;
    border-top: 0.35mm solid var(--cv-line) !important;
    color: var(--cv-muted) !important;
    font-size: 6.8pt !important;
    line-height: 1.1 !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  .cv-brand--small .cv-brand__logo,
  .cv-brand--small .cv-brand__logo svg {
    width: 26mm !important;
    max-width: 26mm !important;
    max-height: 7mm !important;
  }
`
