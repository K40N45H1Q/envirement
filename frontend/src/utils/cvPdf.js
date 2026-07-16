const PAGE_WIDTH_MM = 210
const PAGE_HEIGHT_MM = 297
const WHITE_THRESHOLD = 244

const findSafeSplitY = (context, width, startY, targetY, pageCapacity, sectionBoundaries = []) => {
  const sectionSplitY = sectionBoundaries
    .filter((boundary) => boundary > startY + 1 && boundary <= targetY)
    .at(-1)

  if (sectionSplitY && sectionSplitY >= startY + Math.floor(pageCapacity * 0.25)) {
    return sectionSplitY
  }

  const searchStart = Math.max(
    startY + Math.floor(pageCapacity * 0.65),
    targetY - 220,
  )

  if (searchStart >= targetY) return targetY

  const searchHeight = targetY - searchStart
  const { data } = context.getImageData(0, searchStart, width, searchHeight)
  let bestY = targetY
  let bestInkCount = Number.POSITIVE_INFINITY

  for (let row = 0; row < searchHeight; row += 1) {
    let inkCount = 0

    for (let column = 0; column < width; column += 4) {
      const offset = (row * width + column) * 4
      const isVisible = data[offset + 3] > 16
      const isInk = data[offset] < WHITE_THRESHOLD
        || data[offset + 1] < WHITE_THRESHOLD
        || data[offset + 2] < WHITE_THRESHOLD

      if (isVisible && isInk) inkCount += 1
    }

    const absoluteY = searchStart + row
    if (inkCount < bestInkCount || (inkCount === bestInkCount && absoluteY > bestY)) {
      bestInkCount = inkCount
      bestY = absoluteY
    }
  }

  return bestY
}

export const createPaginatedCvPdf = (sourceCanvas, sourceElement, JsPdf) => {
  const pdf = new JsPdf({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
    compress: true,
  })
  const documentRect = sourceElement.getBoundingClientRect()
  const headerRect = sourceElement.querySelector('.cv-header')?.getBoundingClientRect()
  const bodyRect = sourceElement.querySelector('.cv-body')?.getBoundingClientRect()
  const footerRect = sourceElement.querySelector('.cv-footer')?.getBoundingClientRect()
  const scale = sourceCanvas.width / documentRect.width
  const sectionBoundaries = Array.from(sourceElement.querySelectorAll('.cv-section'))
    .map((section) => Math.round((section.getBoundingClientRect().bottom - documentRect.top) * scale))
    .sort((left, right) => left - right)
  const pagePixelHeight = Math.round(sourceCanvas.width * PAGE_HEIGHT_MM / PAGE_WIDTH_MM)
  const contentStartY = Math.round((bodyRect?.top - documentRect.top) * scale)
  const repeatedHeaderHeight = Math.round((headerRect?.bottom - documentRect.top) * scale)
  const footerStartY = Math.round((footerRect?.top - documentRect.top) * scale)
  const footerHeight = sourceCanvas.height - footerStartY
  const firstPageCapacity = pagePixelHeight - contentStartY - footerHeight
  const repeatedPageCapacity = pagePixelHeight - repeatedHeaderHeight - footerHeight

  if (
    !headerRect
    || !bodyRect
    || !footerRect
    || repeatedHeaderHeight <= 0
    || contentStartY <= repeatedHeaderHeight
    || footerStartY <= contentStartY
    || firstPageCapacity <= 0
    || repeatedPageCapacity <= 0
  ) {
    const imageData = sourceCanvas.toDataURL('image/jpeg', 0.96)
    const imageHeight = sourceCanvas.height * PAGE_WIDTH_MM / sourceCanvas.width
    pdf.addImage(imageData, 'JPEG', 0, 0, PAGE_WIDTH_MM, imageHeight, undefined, 'FAST')
    return pdf
  }

  const sourceContext = sourceCanvas.getContext('2d', { willReadFrequently: true })
  let sourceY = contentStartY
  let pageIndex = 0

  while (sourceY < footerStartY) {
    const pageHeaderHeight = pageIndex === 0 ? contentStartY : repeatedHeaderHeight
    const pageCapacity = pageIndex === 0 ? firstPageCapacity : repeatedPageCapacity
    const targetY = Math.min(sourceY + pageCapacity, footerStartY)
    const pageEndY = targetY < footerStartY
      ? findSafeSplitY(sourceContext, sourceCanvas.width, sourceY, targetY, pageCapacity, sectionBoundaries)
      : targetY
    const contentHeight = Math.max(1, pageEndY - sourceY)
    const pageCanvas = document.createElement('canvas')
    pageCanvas.width = sourceCanvas.width
    pageCanvas.height = pagePixelHeight
    const pageContext = pageCanvas.getContext('2d')

    pageContext.fillStyle = '#ffffff'
    pageContext.fillRect(0, 0, pageCanvas.width, pageCanvas.height)
    pageContext.drawImage(
      sourceCanvas,
      0,
      0,
      sourceCanvas.width,
      pageHeaderHeight,
      0,
      0,
      sourceCanvas.width,
      pageHeaderHeight,
    )
    pageContext.drawImage(
      sourceCanvas,
      0,
      sourceY,
      sourceCanvas.width,
      contentHeight,
      0,
      pageHeaderHeight,
      sourceCanvas.width,
      contentHeight,
    )
    pageContext.drawImage(
      sourceCanvas,
      0,
      footerStartY,
      sourceCanvas.width,
      footerHeight,
      0,
      pagePixelHeight - footerHeight,
      sourceCanvas.width,
      footerHeight,
    )

    if (pageIndex > 0) pdf.addPage('a4', 'portrait')
    pdf.addImage(
      pageCanvas.toDataURL('image/jpeg', 0.96),
      'JPEG',
      0,
      0,
      PAGE_WIDTH_MM,
      PAGE_HEIGHT_MM,
      undefined,
      'FAST',
    )

    sourceY = pageEndY
    pageIndex += 1
  }

  return pdf
}
