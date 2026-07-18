// DOM-only preparation for CV PDF rendering.
// This file owns visual layout mutations that are needed before html2canvas:
// QR normalization and the two-column-to-full-width work-experience flow.

export const normalizePdfQr = (root) => {
  const qr = root.querySelector('.cv-qr')
  const qrImage = qr?.querySelector('img')
  if (!qr || !qrImage) return

  qr.style.position = 'relative'
  qr.style.display = 'block'
  qr.style.overflow = 'hidden'
  qr.style.width = '5.5rem'
  qr.style.height = '5.5rem'
  qr.style.padding = '0.24rem'

  qrImage.style.position = ''
  qrImage.style.top = ''
  qrImage.style.left = ''
  qrImage.style.width = '100%'
  qrImage.style.height = '100%'
  qrImage.style.maxWidth = '100%'
  qrImage.style.margin = '0'
  qrImage.style.objectFit = 'contain'
  qrImage.style.objectPosition = 'center'
  qrImage.style.transform = ''
}

export const balancePdfColumns = (root) => {
  const body = root.querySelector('.cv-body')
  const main = root.querySelector('.cv-main')
  const aside = root.querySelector('.cv-aside')
  const workSection = root.querySelector('.cv-flow-item--work')
  const sectorsSection = root.querySelector('.cv-flow-item--sectors')

  if (!body || !main || !aside) return

  root.classList.add('cv-document--pdf', 'cv-document--balanced')

  if (!workSection) return

  const entries = Array.from(workSection.querySelectorAll(':scope > .cv-entry'))
  if (!entries.length) return

  const asideChildren = Array.from(aside.children)
  const asideBottom = asideChildren.length
    ? Math.max(...asideChildren.map((child) => child.getBoundingClientRect().bottom))
    : aside.getBoundingClientRect().top
  const flowText = workSection.querySelector('.cv-summary-text')
  const flowLineHeight = flowText ? parseFloat(window.getComputedStyle(flowText).lineHeight) || 16 : 16
  const columnBottom = asideBottom + flowLineHeight
  const splitIndex = entries.findIndex((entry) => (
    entry.getBoundingClientRect().bottom > columnBottom
  ))

  if (splitIndex < 0) return

  const continuation = workSection.cloneNode(false)
  continuation.classList.add('cv-flow-item--full', 'cv-flow-item--work-continuation')
  continuation.classList.remove('cv-flow-item--main')
  continuation.removeAttribute('id')

  const crossingEntry = entries[splitIndex]
  const description = crossingEntry.querySelector(':scope > .cv-summary-text:last-child')
  const paragraphs = crossingEntry.querySelectorAll(':scope > .cv-summary-text')
  const words = description && paragraphs.length > 2
    ? description.textContent.trim().split(/\s+/).filter(Boolean)
    : []
  let continuationEntry = null

  if (words.length > 1 && crossingEntry.getBoundingClientRect().top < columnBottom) {
    let low = 1
    let high = words.length
    let fitCount = 0

    while (low <= high) {
      const middle = Math.floor((low + high) / 2)
      description.textContent = words.slice(0, middle).join(' ')

      if (crossingEntry.getBoundingClientRect().bottom <= columnBottom) {
        fitCount = middle
        low = middle + 1
      } else {
        high = middle - 1
      }
    }

    if (fitCount > 0 && fitCount < words.length) {
      description.textContent = words.slice(0, fitCount).join(' ')
      continuationEntry = crossingEntry.cloneNode(false)
      continuationEntry.classList.add('cv-entry--continued')
      const continuedDescription = description.cloneNode(false)
      continuedDescription.textContent = words.slice(fitCount).join(' ')
      continuationEntry.appendChild(continuedDescription)
      continuation.appendChild(continuationEntry)
    } else {
      description.textContent = words.join(' ')
    }
  }

  const moveFromIndex = continuationEntry ? splitIndex + 1 : splitIndex
  entries.slice(moveFromIndex).forEach((entry) => {
    continuation.appendChild(entry)
  })

  const moreItem = workSection.querySelector(':scope > .cv-more-item')
  if (moreItem) continuation.appendChild(moreItem)

  if (continuation.children.length) {
    workSection.classList.add('cv-flow-item--work-split')
    body.insertBefore(continuation, sectorsSection?.parentElement === body ? sectorsSection : null)
  }

  if (!workSection.querySelector(':scope > .cv-entry')) {
    workSection.remove()
  }
}

export const preparePdfCvDocument = (root) => {
  if (!root) return

  root.classList.add('cv-document--pdf')
  root.style.background = 'transparent'
  root.style.boxShadow = 'none'
  root.querySelector('.cv-watermark')?.setAttribute('hidden', '')
  normalizePdfQr(root)
  balancePdfColumns(root)
}
