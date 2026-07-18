const PAGE_WIDTH_MM = 210
const PAGE_HEIGHT_MM = 297

// Пиксель считается «чернильным», если хотя бы один RGB-канал темнее этого значения.
const WHITE_THRESHOLD = 244
const ALPHA_THRESHOLD = 16

// При анализе строки проверяем не каждый пиксель, а каждый N-й по горизонтали.
// Значение 2 даёт более надёжный результат, чем 4, но остаётся достаточно быстрым.
const HORIZONTAL_SAMPLE_STEP = 2

// Не разрешаем переносить страницу слишком рано.
// Это устраняет большие пустые области, которые появлялись из-за границ секций
// в правой колонке, пока текст в левой колонке ещё продолжался.
const MIN_PAGE_FILL_RATIO = 0.9

// Ищем место переноса в нижней части доступной области страницы.
const SEARCH_DEPTH_RATIO = 0.35
const MIN_SEARCH_DEPTH_CSS_PX = 220

// Минимальная высота горизонтальной пустой полосы.
// Значение умножается на scale, поэтому одинаково работает при scale 1, 2 и т. д.
const MIN_BLANK_BAND_CSS_PX = 6

// Допустимое расстояние между DOM-границей блока и найденной пустой полосой.
const DOM_BOUNDARY_TOLERANCE_CSS_PX = 20

// Явные блоки, между которыми обычно безопасно переносить страницу.
// Список можно расширить классами конкретного шаблона CV.
const SEMANTIC_BLOCK_SELECTOR = [
  '.cv-entry',
  '.cv-item',
  '.cv-position',
  '.experience-item',
  '.work-experience-item',
  '.education-item',
  '.project-item',
  '.skill-item',
  '.cv-paragraph',
  'p',
  'li',
  'blockquote',
].join(',')

const HEADING_SELECTOR = [
  'h1',
  'h2',
  'h3',
  'h4',
  'h5',
  'h6',
  '.cv-section-title',
  '.section-title',
  '.entry-title',
].join(',')

const clamp = (value, minimum, maximum) => (
  Math.min(maximum, Math.max(minimum, value))
)

/**
 * Добавляет canvas как изображение на текущую страницу PDF.
 */
const addCanvasToPdfPage = (pdf, canvas) => {
  pdf.addImage(
    canvas.toDataURL('image/jpeg', 0.96),
    'JPEG',
    0,
    0,
    PAGE_WIDTH_MM,
    PAGE_HEIGHT_MM,
    undefined,
    'FAST',
  )
}

/**
 * Запасной режим пагинации.
 *
 * Используется, если в DOM не найдены обязательные элементы шаблона
 * (.cv-header, .cv-body, .cv-footer) или их геометрия некорректна.
 * В отличие от старого варианта, длинный canvas не помещается на одну A4-страницу,
 * а режется на несколько страниц без обрезания нижней части документа.
 */
const addCanvasAsSimplePages = (pdf, sourceCanvas) => {
  const pagePixelHeight = Math.max(
    1,
    Math.round(sourceCanvas.width * PAGE_HEIGHT_MM / PAGE_WIDTH_MM),
  )

  let sourceY = 0
  let pageIndex = 0

  while (sourceY < sourceCanvas.height) {
    const contentHeight = Math.min(
      pagePixelHeight,
      sourceCanvas.height - sourceY,
    )

    const pageCanvas = document.createElement('canvas')
    pageCanvas.width = sourceCanvas.width
    pageCanvas.height = pagePixelHeight

    const pageContext = pageCanvas.getContext('2d')

    if (!pageContext) {
      throw new Error(
        'Не удалось получить 2D-контекст временного canvas.',
      )
    }

    pageContext.fillStyle = '#ffffff'
    pageContext.fillRect(
      0,
      0,
      pageCanvas.width,
      pageCanvas.height,
    )

    pageContext.drawImage(
      sourceCanvas,
      0,
      sourceY,
      sourceCanvas.width,
      contentHeight,
      0,
      0,
      sourceCanvas.width,
      contentHeight,
    )

    if (pageIndex > 0) {
      pdf.addPage('a4', 'portrait')
    }

    addCanvasToPdfPage(pdf, pageCanvas)

    sourceY += contentHeight
    pageIndex += 1
  }

  return pdf
}

/**
 * Проверяет, является ли элемент заголовком.
 *
 * Для заголовка безопасной точкой является его верхняя граница:
 * заголовок должен перейти на следующую страницу вместе с последующим текстом.
 * Нижнюю границу заголовка намеренно не добавляем, чтобы не оставлять
 * заголовок один внизу страницы.
 */
const isHeadingElement = (element) => (
  typeof element.matches === 'function'
  && element.matches(HEADING_SELECTOR)
)

/**
 * Определяет, похож ли элемент на самостоятельный блочный текстовый узел.
 *
 * Это позволяет находить границы не только у известных классов,
 * но и у обычных div-блоков с текстом внутри.
 */
const isLeafTextBlock = (element, view) => {
  const text = element.textContent?.trim()

  if (!text) {
    return false
  }

  const style = view?.getComputedStyle(element)

  if (!style) {
    return false
  }

  const blockLikeDisplays = new Set([
    'block',
    'list-item',
    'flex',
    'grid',
    'table-row',
    'table-cell',
  ])

  if (!blockLikeDisplays.has(style.display)) {
    return false
  }

  const hasBlockChild = Array.from(element.children).some((child) => {
    const childStyle = view.getComputedStyle(child)

    return blockLikeDisplays.has(childStyle.display)
  })

  return !hasBlockChild
}

/**
 * Собирает логические точки переноса из DOM.
 *
 * Важное отличие от старой реализации:
 * границы .cv-section больше не используются как безусловный перенос.
 * Каждая DOM-граница позже должна совпасть с реальной пустой горизонтальной
 * полосой на canvas.
 *
 * Поэтому окончание секции в правой колонке не разрежет текст,
 * который продолжается в левой колонке.
 */
const collectDomBoundaryCandidates = (
  sourceElement,
  bodyElement,
  documentRect,
  scale,
) => {
  const candidatesByY = new Map()

  const view = (
    sourceElement.ownerDocument?.defaultView
    ?? window
  )

  const addBoundary = (element, edge, priority) => {
    const rect = element.getBoundingClientRect()

    if (rect.height <= 0 || rect.width <= 0) {
      return
    }

    const cssY = edge === 'top'
      ? rect.top
      : rect.bottom

    const canvasY = Math.round(
      (cssY - documentRect.top) * scale,
    )

    const existing = candidatesByY.get(canvasY)

    if (!existing || existing.priority < priority) {
      candidatesByY.set(canvasY, {
        y: canvasY,
        priority,
      })
    }
  }

  // Явные смысловые блоки имеют высокий приоритет.
  bodyElement
    .querySelectorAll(SEMANTIC_BLOCK_SELECTOR)
    .forEach((element) => {
      addBoundary(element, 'top', 3)

      if (!isHeadingElement(element)) {
        addBoundary(element, 'bottom', 3)
      }
    })

  // Дополнительно находим обычные блочные элементы с текстом,
  // даже если у них нет специальных CSS-классов.
  bodyElement
    .querySelectorAll('*')
    .forEach((element) => {
      if (!isLeafTextBlock(element, view)) {
        return
      }

      addBoundary(
        element,
        'top',
        isHeadingElement(element) ? 4 : 2,
      )

      if (!isHeadingElement(element)) {
        addBoundary(element, 'bottom', 2)
      }
    })

  // Границы секций оставляем только как слабую подсказку.
  // Они никогда не применяются без проверки пустой полосы
  // на всей ширине canvas.
  bodyElement
    .querySelectorAll('.cv-section')
    .forEach((element) => {
      addBoundary(element, 'top', 1)
      addBoundary(element, 'bottom', 1)
    })

  return Array.from(candidatesByY.values())
    .sort((left, right) => left.y - right.y)
}

/**
 * Считает количество тёмных пикселей
 * в каждой горизонтальной строке.
 *
 * Небольшое постоянное количество тёмных пикселей допустимо:
 * например, на странице может проходить вертикальный разделитель колонок.
 */
const getRowInkAnalysis = (
  context,
  width,
  startY,
  endY,
  scale,
) => {
  const canvasHeight = context.canvas.height

  const safeStartY = clamp(
    Math.floor(startY),
    0,
    canvasHeight,
  )

  const safeEndY = clamp(
    Math.ceil(endY),
    safeStartY,
    canvasHeight,
  )

  const height = safeEndY - safeStartY

  if (height <= 0) {
    return null
  }

  let imageData

  try {
    imageData = context.getImageData(
      0,
      safeStartY,
      width,
      height,
    ).data
  } catch (error) {
    // Canvas может оказаться tainted,
    // например из-за изображения без CORS.
    // В этом случае вызывающий код перейдёт
    // к ограниченному DOM-режиму.
    return null
  }

  const sampledColumns = Math.ceil(
    width / HORIZONTAL_SAMPLE_STEP,
  )

  // Разрешаем примерно 1,2% тёмных отсчётов.
  // Этого достаточно для вертикальных линий,
  // но недостаточно для строки текста.
  const maxInkPerRow = Math.max(
    4,
    Math.round(sampledColumns * 0.012),
  )

  const minimumBlankRun = Math.max(
    4,
    Math.round(MIN_BLANK_BAND_CSS_PX * scale),
  )

  const inkCounts = new Array(height)

  for (let row = 0; row < height; row += 1) {
    let inkCount = 0

    for (
      let column = 0;
      column < width;
      column += HORIZONTAL_SAMPLE_STEP
    ) {
      const offset = (
        row * width + column
      ) * 4

      const isVisible = (
        imageData[offset + 3] > ALPHA_THRESHOLD
      )

      const isInk = (
        imageData[offset] < WHITE_THRESHOLD
        || imageData[offset + 1] < WHITE_THRESHOLD
        || imageData[offset + 2] < WHITE_THRESHOLD
      )

      if (isVisible && isInk) {
        inkCount += 1
      }
    }

    inkCounts[row] = inkCount
  }

  const blankBands = []
  let runStart = null

  // Дополнительная итерация закрывает пустую полосу
  // в самом конце диапазона.
  for (
    let row = 0;
    row <= inkCounts.length;
    row += 1
  ) {
    const isBlank = (
      row < inkCounts.length
      && inkCounts[row] <= maxInkPerRow
    )

    if (isBlank && runStart === null) {
      runStart = row
      continue
    }

    if (!isBlank && runStart !== null) {
      const runEnd = row - 1
      const runLength = runEnd - runStart + 1

      if (runLength >= minimumBlankRun) {
        blankBands.push({
          startY: safeStartY + runStart,
          endY: safeStartY + runEnd,
          centerY: (
            safeStartY
            + Math.round((runStart + runEnd) / 2)
          ),
          length: runLength,
        })
      }

      runStart = null
    }
  }

  return {
    startY: safeStartY,
    inkCounts,
    blankBands,
    maxInkPerRow,
    minimumBlankRun,
  }
}

/**
 * Возвращает расстояние от координаты Y
 * до найденной пустой полосы.
 */
const distanceToBand = (y, band) => {
  if (y < band.startY) {
    return band.startY - y
  }

  if (y > band.endY) {
    return y - band.endY
  }

  return 0
}

/**
 * Находит строку с наименьшим количеством тёмных пикселей.
 *
 * Это последний запасной вариант:
 * он может перенести текст между строками,
 * но старается не разрезать сами буквы.
 */
const findLowestInkRow = (analysis) => {
  let bestRow = analysis.inkCounts.length - 1
  let bestInkCount = Number.POSITIVE_INFINITY

  analysis.inkCounts.forEach((inkCount, row) => {
    // При одинаковом количестве чернил выбираем
    // более позднюю строку, чтобы максимально заполнить страницу.
    if (
      inkCount < bestInkCount
      || (
        inkCount === bestInkCount
        && row > bestRow
      )
    ) {
      bestInkCount = inkCount
      bestRow = row
    }
  })

  return analysis.startY + bestRow
}

/**
 * Ищет безопасную координату переноса страницы.
 *
 * Порядок выбора:
 *
 * 1. DOM-граница смыслового блока,
 *    совпавшая с пустой полосой на всей ширине canvas.
 *
 * 2. Последняя широкая пустая полоса.
 *
 * 3. Последняя обычная пустая полоса.
 *
 * 4. Строка с минимальным количеством тёмных пикселей.
 *
 * 5. targetY, если анализ canvas недоступен.
 */
const findSafeSplitY = (
  context,
  width,
  startY,
  targetY,
  pageCapacity,
  scale,
  boundaryCandidates = [],
) => {
  const minimumFillY = (
    startY
    + Math.floor(
      pageCapacity * MIN_PAGE_FILL_RATIO,
    )
  )

  const searchDepth = Math.max(
    Math.round(
      MIN_SEARCH_DEPTH_CSS_PX * scale,
    ),
    Math.round(
      pageCapacity * SEARCH_DEPTH_RATIO,
    ),
  )

  const searchStart = Math.max(
    minimumFillY,
    targetY - searchDepth,
  )

  if (searchStart >= targetY) {
    return targetY
  }

  const analysis = getRowInkAnalysis(
    context,
    width,
    searchStart,
    targetY,
    scale,
  )

  // Если пиксели canvas прочитать нельзя,
  // разрешаем только DOM-границу,
  // расположенную совсем близко к нижнему краю страницы.
  //
  // Это не даёт снова создать огромную пустую область.
  if (!analysis) {
    const unvalidatedMinimumY = (
      targetY
      - Math.floor(pageCapacity * 0.15)
    )

    const fallbackBoundary = boundaryCandidates
      .filter(({ y }) => (
        y >= Math.max(
          minimumFillY,
          unvalidatedMinimumY,
        )
        && y <= targetY
      ))
      .sort((left, right) => (
        right.y - left.y
        || right.priority - left.priority
      ))[0]

    return fallbackBoundary?.y ?? targetY
  }

  const tolerance = Math.max(
    8,
    Math.round(
      DOM_BOUNDARY_TOLERANCE_CSS_PX * scale,
    ),
  )

  const matchingBoundaries = []

  boundaryCandidates.forEach((candidate) => {
    if (
      candidate.y < minimumFillY
      || candidate.y > targetY
    ) {
      return
    }

    analysis.blankBands.forEach((band) => {
      const distance = distanceToBand(
        candidate.y,
        band,
      )

      if (distance <= tolerance) {
        matchingBoundaries.push({
          y: band.centerY,
          priority: candidate.priority,
          distance,
          bandLength: band.length,
        })
      }
    })
  })

  if (matchingBoundaries.length > 0) {
    matchingBoundaries.sort((left, right) => (
      // В первую очередь максимально заполняем страницу.
      right.y - left.y

      // При одинаковом Y предпочитаем
      // более смысловую DOM-границу.
      || right.priority - left.priority

      // Затем выбираем точное совпадение
      // с пустой полосой.
      || left.distance - right.distance

      // После этого предпочитаем более широкую полосу.
      || right.bandLength - left.bandLength
    ))

    return matchingBoundaries[0].y
  }

  // Широкая пустая полоса с большей вероятностью
  // означает границу абзаца или блока,
  // а не обычный межстрочный интервал.
  const strongBands = analysis.blankBands.filter(
    (band) => (
      band.length
      >= Math.ceil(
        analysis.minimumBlankRun * 1.5,
      )
    ),
  )

  if (strongBands.length > 0) {
    return strongBands.at(-1).centerY
  }

  if (analysis.blankBands.length > 0) {
    return analysis.blankBands.at(-1).centerY
  }

  return findLowestInkRow(analysis)
}

/**
 * Создаёт многостраничный PDF из canvas CV.
 *
 * Ожидаемая структура sourceElement:
 *
 * .cv-header — шапка, повторяемая на следующих страницах.
 * .cv-body   — основное содержимое.
 * .cv-footer — подвал, повторяемый на каждой странице.
 */
export const createPaginatedCvPdf = (
  sourceCanvas,
  sourceElement,
  JsPdf,
) => {
  if (
    !sourceCanvas
    || !sourceElement
    || !JsPdf
  ) {
    throw new TypeError(
      'createPaginatedCvPdf: обязательны sourceCanvas, sourceElement и JsPdf.',
    )
  }

  const pdf = new JsPdf({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
    compress: true,
  })

  const documentRect = (
    sourceElement.getBoundingClientRect()
  )

  const headerElement = (
    sourceElement.querySelector('.cv-header')
  )

  const bodyElement = (
    sourceElement.querySelector('.cv-body')
  )

  const footerElement = (
    sourceElement.querySelector('.cv-footer')
  )

  const headerRect = (
    headerElement?.getBoundingClientRect()
  )

  const bodyRect = (
    bodyElement?.getBoundingClientRect()
  )

  const footerRect = (
    footerElement?.getBoundingClientRect()
  )

  const scale = documentRect.width > 0
    ? sourceCanvas.width / documentRect.width
    : 0

  const pagePixelHeight = Math.max(
    1,
    Math.round(
      sourceCanvas.width
      * PAGE_HEIGHT_MM
      / PAGE_WIDTH_MM,
    ),
  )

  const contentStartY = bodyRect
    ? Math.round(
      (bodyRect.top - documentRect.top)
      * scale,
    )
    : 0

  // На следующих страницах копируем шапку
  // от начала документа до нижней границы .cv-header.
  const repeatedHeaderHeight = headerRect
    ? Math.round(
      (headerRect.bottom - documentRect.top)
      * scale,
    )
    : 0

  const footerStartY = footerRect
    ? Math.round(
      (footerRect.top - documentRect.top)
      * scale,
    )
    : sourceCanvas.height

  const footerHeight = (
    sourceCanvas.height - footerStartY
  )

  const firstPageCapacity = (
    pagePixelHeight
    - contentStartY
    - footerHeight
  )

  const repeatedPageCapacity = (
    pagePixelHeight
    - repeatedHeaderHeight
    - footerHeight
  )

  const layoutIsValid = (
    Boolean(headerRect)
    && Boolean(bodyRect)
    && Boolean(footerRect)
    && scale > 0
    && repeatedHeaderHeight > 0
    && contentStartY >= repeatedHeaderHeight
    && footerStartY > contentStartY
    && footerStartY <= sourceCanvas.height
    && footerHeight >= 0
    && firstPageCapacity > 0
    && repeatedPageCapacity > 0
  )

  if (!layoutIsValid) {
    return addCanvasAsSimplePages(
      pdf,
      sourceCanvas,
    )
  }

  const sourceContext = sourceCanvas.getContext(
    '2d',
    {
      willReadFrequently: true,
    },
  )

  if (!sourceContext) {
    return addCanvasAsSimplePages(
      pdf,
      sourceCanvas,
    )
  }

  const boundaryCandidates = (
    collectDomBoundaryCandidates(
      sourceElement,
      bodyElement,
      documentRect,
      scale,
    )
  )

  let sourceY = contentStartY
  let pageIndex = 0

  // Защита от бесконечного цикла
  // при неожиданной геометрии документа.
  const maximumPageCount = (
    Math.ceil(
      (footerStartY - contentStartY)
      / Math.max(
        1,
        Math.min(
          firstPageCapacity,
          repeatedPageCapacity,
        ),
      ),
    )
    + 20
  )

  while (
    sourceY < footerStartY
    && pageIndex < maximumPageCount
  ) {
    const pageHeaderHeight = (
      pageIndex === 0
        ? contentStartY
        : repeatedHeaderHeight
    )

    const pageCapacity = (
      pageIndex === 0
        ? firstPageCapacity
        : repeatedPageCapacity
    )

    const targetY = Math.min(
      sourceY + pageCapacity,
      footerStartY,
    )

    let pageEndY = targetY

    // Для последней страницы
    // поиск переноса не нужен.
    if (targetY < footerStartY) {
      pageEndY = findSafeSplitY(
        sourceContext,
        sourceCanvas.width,
        sourceY,
        targetY,
        pageCapacity,
        scale,
        boundaryCandidates,
      )
    }

    // Координата обязана двигаться вперёд.
    // Если алгоритм вернул некорректное значение,
    // режем по targetY.
    if (
      !Number.isFinite(pageEndY)
      || pageEndY <= sourceY + 1
      || pageEndY > targetY
    ) {
      pageEndY = targetY
    }

    const contentHeight = Math.max(
      1,
      pageEndY - sourceY,
    )

    const pageCanvas = (
      document.createElement('canvas')
    )

    pageCanvas.width = sourceCanvas.width
    pageCanvas.height = pagePixelHeight

    const pageContext = pageCanvas.getContext('2d')

    if (!pageContext) {
      throw new Error(
        'Не удалось получить 2D-контекст страницы PDF.',
      )
    }

    pageContext.fillStyle = '#ffffff'

    pageContext.fillRect(
      0,
      0,
      pageCanvas.width,
      pageCanvas.height,
    )

    // Первая страница получает исходную верхнюю часть
    // до начала body.
    //
    // Следующие страницы получают только повторяемую шапку.
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

    // Основной фрагмент текущей страницы.
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

    // Повторяем footer внизу каждой A4-страницы.
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

    if (pageIndex > 0) {
      pdf.addPage('a4', 'portrait')
    }

    addCanvasToPdfPage(
      pdf,
      pageCanvas,
    )

    sourceY = pageEndY
    pageIndex += 1
  }

  // Теоретически сюда можно попасть
  // только при повреждённой геометрии.
  if (sourceY < footerStartY) {
    throw new Error(
      'Пагинация остановлена: превышено допустимое количество страниц.',
    )
  }

  return pdf
}
