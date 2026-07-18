<script setup>
// Shared CV document template.
// It owns only the visible CV markup and styling; pages pass prepared data in.

import { CV_WATERMARK } from '@/cv/cvWatermark'

const props = defineProps({
  avatarPreview: { type: String, default: '' },
  avatarInitials: { type: String, default: '' },
  displayName: { type: String, required: true },
  displayRole: { type: String, required: true },
  contactItems: { type: Array, default: () => [] },
  additionalItems: { type: Array, default: () => [] },
  summaryParagraphs: { type: Array, default: () => [] },
  workExperiences: { type: Array, default: () => [] },
  moreWorkExperiencesCount: { type: Number, default: 0 },
  languages: { type: Array, default: () => [] },
  moreLanguagesCount: { type: Number, default: 0 },
  licenses: { type: Array, default: () => [] },
  skills: { type: Array, default: () => [] },
  moreSkillsCount: { type: Number, default: 0 },
  sectors: { type: Array, default: () => [] },
  moreSectorsCount: { type: Number, default: 0 },
  certificates: { type: Array, default: () => [] },
  educations: { type: Array, default: () => [] },
  moreEducationsCount: { type: Number, default: 0 },
  cvId: { type: String, required: true },
  copy: { type: Object, required: true },
  sectionTitle: { type: Function, default: null },
  formatDate: { type: Function, required: true },
  formatMore: { type: Function, required: true },
  categoryLabel: { type: Function, default: (value) => value },
  displayLanguageName: { type: Function, required: true },
  displayLanguageLevel: { type: Function, default: (value) => value },
  displayEducation: { type: Function, required: true },
  formatCountry: { type: Function, default: (value) => value },
  showEducationSpecialities: { type: Function, default: () => true },
})

const title = (key) => props.sectionTitle?.(key) || props.copy[key]
const watermarkPitchX = CV_WATERMARK.logoWidthPx + CV_WATERMARK.gapXPx
const watermarkPitchY = CV_WATERMARK.logoHeightPx + CV_WATERMARK.gapYPx
const watermarkTiles = Array.from({ length: CV_WATERMARK.previewTileCount }, (_, index) => {
  const column = index % CV_WATERMARK.previewColumns
  const row = Math.floor(index / CV_WATERMARK.previewColumns)
  const stagger = row % 2 === 0 ? 0 : CV_WATERMARK.staggerXPx

  return {
    index,
    left: CV_WATERMARK.offsetXPx + column * watermarkPitchX + stagger - watermarkPitchX,
    top: CV_WATERMARK.offsetYPx + row * watermarkPitchY - watermarkPitchY,
  }
})
const watermarkStyle = {
  opacity: String(CV_WATERMARK.opacity),
}
const watermarkTileStyle = (tile) => ({
  position: 'absolute',
  left: `${tile.left}px`,
  top: `${tile.top}px`,
  width: `${CV_WATERMARK.logoWidthPx}px`,
  height: `${CV_WATERMARK.logoHeightPx}px`,
  transform: `rotate(${CV_WATERMARK.rotationDeg}deg)`,
})
</script>

<template>
  <article class="cv-document">
    <div class="cv-watermark" :style="watermarkStyle" aria-hidden="true">
      <img
        v-for="tile in watermarkTiles"
        :key="tile.index"
        :src="CV_WATERMARK.src"
        :style="watermarkTileStyle(tile)"
        alt=""
      />
    </div>

    <header class="cv-header">
      <div class="cv-brand" aria-label="CVHOLD">
        <img src="/logo-pdf-transparent.png" alt="" class="cv-brand__logo" aria-hidden="true" />
      </div>
      <div class="cv-verified">
        <i class="fas fa-circle-check" aria-hidden="true"></i>
        <span><strong>{{ copy.cvDocument }}</strong></span>
      </div>
    </header>

    <section class="cv-top">
      <div class="cv-person">
        <div class="cv-avatar">
          <img v-if="avatarPreview" :src="avatarPreview" :alt="displayName" />
          <span v-else>{{ avatarInitials }}</span>
        </div>

        <div>
          <h1>{{ displayName }}</h1>
          <p>{{ displayRole }}</p>
          <ul class="cv-contact-list">
            <li v-for="(item, index) in contactItems" :key="`${item.icon}-${index}`">
              <i :class="item.icon"></i>
              <span>{{ item.value }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div v-if="additionalItems.length" class="cv-top-additional">
        <ul class="cv-extra-list">
          <li v-for="item in additionalItems" :key="item.label">
            <i :class="item.icon"></i>
            <span>{{ item.label }}: {{ item.value }}</span>
          </li>
        </ul>
      </div>

      <div class="cv-id">
        <div class="cv-qr">
          <img src="/cvhold-qr-custom.png?v=2" alt="QR code for cvhold.com" width="330" height="330" decoding="sync" />
        </div>
        <small>CVHOLD ID</small>
        <strong>{{ cvId }}</strong>
      </div>
    </section>

    <section class="cv-body">
      <main class="cv-main">
        <section class="cv-section cv-section--summary cv-flow-item cv-flow-item--main">
          <h2>{{ title('aboutMe') }}</h2>
          <p v-for="paragraph in summaryParagraphs" :key="paragraph" class="cv-summary-text">{{ paragraph }}</p>
        </section>

        <section v-if="workExperiences.length" class="cv-section cv-flow-item cv-flow-item--main cv-flow-item--work">
          <h2>{{ title('workExperience') }}</h2>
          <div v-for="(work, index) in workExperiences" :key="`cv-work-${index}`" class="cv-entry">
            <p class="cv-summary-text">
              <strong>{{ work.position }}</strong>
              <span v-if="work.company_name"> · {{ work.company_name }}</span>
            </p>
            <p class="cv-summary-text">
              {{ formatDate(work.start_date) }} — {{ work.current ? copy.present : formatDate(work.end_date) }}
              <span v-if="work.job_category"> · {{ categoryLabel(work.job_category) }}</span>
              <span v-if="work.country"> · {{ formatCountry(work.country) }}</span>
            </p>
            <p v-if="work.description" class="cv-summary-text cv-entry__description">{{ work.description }}</p>
          </div>
          <p v-if="moreWorkExperiencesCount" class="cv-more-item">{{ formatMore('moreItems', moreWorkExperiencesCount) }}</p>
        </section>
      </main>

      <aside class="cv-aside">
        <section v-if="languages.length" class="cv-section cv-flow-item cv-flow-item--aside">
          <h2>{{ title('languages') }}</h2>
          <ul class="cv-list">
            <li v-for="item in languages" :key="`${item.name}-${item.level}`">{{ displayLanguageName(item.name) }} — {{ displayLanguageLevel(item.level) }}</li>
            <li v-if="moreLanguagesCount" class="cv-more-item">{{ formatMore('moreItems', moreLanguagesCount) }}</li>
          </ul>
        </section>

        <section v-if="licenses.length" class="cv-section cv-flow-item cv-flow-item--aside">
          <h2>{{ title('drivingLicense') }}</h2>
          <p class="cv-summary-text">{{ licenses.join(', ') }}</p>
        </section>

        <section v-if="skills.length" class="cv-section cv-flow-item cv-flow-item--aside">
          <h2>{{ title('skills') }}</h2>
          <ul class="cv-list">
            <li v-for="skill in skills" :key="skill">{{ skill }}</li>
            <li v-if="moreSkillsCount" class="cv-more-item">{{ formatMore('moreItems', moreSkillsCount) }}</li>
          </ul>
        </section>

        <section v-if="sectors.length" class="cv-section cv-flow-item cv-flow-item--aside cv-flow-item--sectors">
          <h2>{{ title('workAreas') }}</h2>
          <div class="cv-sector-grid">
            <div v-for="sector in sectors" :key="sector.value" class="cv-sector">
              <i :class="sector.iconClass"></i>
              <span class="cv-sector__copy"><strong>{{ sector.label }}</strong><small v-if="sector.experience">{{ sector.experience }}</small></span>
            </div>
            <div v-if="moreSectorsCount" class="cv-sector cv-more-item"><span>{{ formatMore('moreItems', moreSectorsCount) }}</span></div>
          </div>
        </section>

        <section v-if="certificates.length" class="cv-section cv-flow-item cv-flow-item--aside">
          <h2>{{ title('certificatesAndLicenses') }}</h2>
          <p class="cv-summary-text">{{ certificates.join(', ') }}</p>
        </section>

        <section v-if="educations.length" class="cv-section cv-flow-item cv-flow-item--aside">
          <h2>{{ title('education') }}</h2>
          <div v-for="(education, index) in educations" :key="`cv-education-${index}`" class="cv-entry">
            <p class="cv-summary-text"><strong>{{ education.institution }}</strong></p>
            <p class="cv-summary-text">
              {{ displayEducation(education.level) }}
              <span v-if="showEducationSpecialities(education) && education.speciality"> · {{ education.speciality }}</span>
              <span v-if="showEducationSpecialities(education) && education.second_speciality"> · {{ education.second_speciality }}</span>
              <span v-if="education.country"> · {{ formatCountry(education.country) }}</span>
              <span v-if="education.start_date || education.end_date"> · {{ formatDate(education.start_date) }}—{{ education.current ? copy.present : formatDate(education.end_date) }}</span>
            </p>
            <p v-if="education.additional_information" class="cv-summary-text">{{ education.additional_information }}</p>
          </div>
          <p v-if="moreEducationsCount" class="cv-more-item">{{ formatMore('moreItems', moreEducationsCount) }}</p>
        </section>
      </aside>
    </section>

    <footer class="cv-footer">
      <div class="cv-brand cv-brand--small" aria-label="CVHOLD">
        <img src="/logo-pdf-transparent.png" alt="" class="cv-brand__logo" aria-hidden="true" />
      </div>
      <span>{{ copy.cvFooterTagline }}</span>
      <span>www.cvhold.com</span>
    </footer>
  </article>
</template>

<style scoped>
.cv-document {
  --cv-green: #149447;
  --cv-green-dark: #0f7f3c;
  --cv-ink: #101828;
  --cv-muted: #667085;
  --cv-line: #d9dee7;
  --cv-soft: #f3fbf6;
  width: min(100%, 49.625rem);
  height: auto;
  min-height: 0;
  margin: 0 auto;
  padding: 1.45rem 1.7rem 1.15rem;
  background: #fff;
  color: var(--cv-ink);
  position: relative;
  isolation: isolate;
  border-radius: .8rem;
  box-shadow: 0 1.5rem 3rem rgba(16, 24, 40, .12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: Inter, Arial, sans-serif;
}

.cv-watermark {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
}

.cv-watermark img {
  display: block;
  object-fit: contain;
  transform-origin: center;
}

.cv-document > :not(.cv-watermark) {
  position: relative;
  z-index: 2;
}

.cv-header,
.cv-top,
.cv-footer {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex: 0 0 auto;
  min-width: 0;
}

.cv-header {
  min-height: 3.65rem;
  padding-bottom: .85rem;
  border-bottom: .0625rem solid var(--cv-line);
}

.cv-brand {
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  flex-wrap: nowrap;
  gap: .55rem;
  min-width: 0;
  color: var(--cv-ink);
  background: transparent;
}

.cv-brand__logo,
.cv-brand__logo svg {
  width: 8.2rem;
  max-width: 8.2rem;
  height: 2.15rem;
  max-height: 2.15rem;
  object-fit: contain;
  object-position: left center;
  display: block;
  flex: 0 0 auto;
  background: transparent;
}

.cv-verified {
  display: inline-flex;
  align-items: center;
  gap: .55rem;
  flex: 0 0 auto;
  color: var(--cv-green);
  background: transparent;
}

.cv-verified > i { font-size: 1.25rem; }
.cv-verified > span { display: grid; gap: .12rem; text-align: right; background: transparent; }
.cv-verified strong { color: var(--cv-ink); font-size: .72rem; line-height: 1; }
.cv-top { padding: 1rem 0 .95rem; border-bottom: .0625rem solid var(--cv-line); align-items: flex-start; }
.cv-person { display: grid; grid-template-columns: 4.25rem minmax(0, 1fr); gap: .85rem; align-items: start; min-width: 0; }
.cv-top-additional { flex: 1 1 12rem; min-width: 10rem; padding: 4.45rem 1rem 0; }
.cv-avatar { width: 4.25rem; height: 4.25rem; display: grid; place-items: center; overflow: hidden; border: 0; border-radius: 50%; background: linear-gradient(180deg, #16b85b 0%, #139e4f 100%); box-shadow: none; color: #fff; font-size: 1.05rem; line-height: 1; font-weight: 900; }
.cv-avatar img { width: 100%; height: 100%; object-fit: cover; display: block; }
.cv-person h1 { margin: 0; color: #05070a; font-size: clamp(2rem, 4vw, 2.45rem); line-height: .95; letter-spacing: -.055em; overflow-wrap: anywhere; }
.cv-person p { margin: .4rem 0 .7rem; color: var(--cv-green); font-size: .95rem; line-height: 1.1; font-weight: 800; }
.cv-contact-list, .cv-list, .cv-extra-list { margin: 0; padding: 0; list-style: none; }
.cv-contact-list { display: grid; gap: .3rem; }
.cv-contact-list li { display: flex; align-items: center; gap: .45rem; color: var(--cv-ink); font-size: .74rem; line-height: 1.22; min-width: 0; }
.cv-contact-list span, .cv-extra-list span, .cv-list li, .cv-sector span { overflow-wrap: anywhere; word-break: break-word; white-space: pre-wrap; }
.cv-contact-list i, .cv-extra-list i { width: .95rem; color: var(--cv-green); text-align: center; flex: 0 0 auto; }
.cv-id { display: grid; justify-items: center; gap: .18rem; color: var(--cv-ink); flex: 0 0 auto; }
.cv-id small { margin-top: .18rem; color: var(--cv-green); font-size: .6rem; line-height: 1; font-weight: 900; text-transform: uppercase; }
.cv-id > strong { font-size: .72rem; line-height: 1; }
.cv-qr { position: relative; width: 5.5rem; height: 5.5rem; display: block; padding: .24rem; border: .0625rem solid var(--cv-line); border-radius: .32rem; background: #fff; overflow: hidden; }
.cv-qr img { width: 100%; height: 100%; display: block; object-fit: contain; }
.cv-body { display: grid; grid-template-columns: minmax(0, 1.34fr) minmax(12.5rem, 0.82fr); gap: 1.25rem; padding-top: 1rem; flex: 1 1 auto; min-height: auto; overflow: visible; }
.cv-main { min-height: auto; overflow: visible; padding-right: 1.25rem; border-right: .0625rem solid var(--cv-line); }
.cv-aside { min-height: auto; overflow: visible; }
.cv-body > .cv-flow-item--full { grid-column: 1 / -1; }
.cv-document--balanced .cv-body { row-gap: 0; grid-auto-rows: max-content; align-content: start; }
.cv-document--balanced .cv-flow-item--work-split { margin-bottom: 0; padding-bottom: 0; border-bottom: 0; }
.cv-document--pdf .cv-flow-item--work-continuation { padding-right: 0; }
.cv-document--pdf .cv-flow-item--work-continuation .cv-summary-text { text-align: justify; text-align-last: left; hyphens: auto; }
.cv-document--pdf .cv-entry__description { text-align: justify; text-align-last: left; hyphens: auto; }
.cv-section { padding-bottom: .72rem; margin: 0 0 .72rem; border-bottom: .0625rem solid var(--cv-line); break-inside: avoid; page-break-inside: avoid; }
.cv-section:last-child { margin-bottom: 0; }
.cv-section h2 { margin: 0 0 .48rem; padding: 0; border: 0; color: var(--cv-green); font-size: .78rem; line-height: 1.1; font-weight: 800; text-transform: uppercase; letter-spacing: .04em; }
.cv-section p { margin: 0; color: var(--cv-ink); font-size: .72rem; line-height: 1.42; }
.cv-summary-text { display: block; overflow: visible; overflow-wrap: anywhere; word-break: break-word; white-space: pre-wrap; }
.cv-entry__description { text-align: justify; text-align-last: left; hyphens: auto; }
.cv-section p + p { margin-top: .42rem; }
.cv-entry + .cv-entry { margin-top: .55rem; padding-top: .55rem; border-top: .0625rem solid var(--cv-line); }
.cv-list { display: grid; gap: .3rem; }
.cv-list li { position: relative; padding-left: .78rem; color: var(--cv-ink); font-size: .7rem; line-height: 1.24; }
.cv-list li::before { content: ''; position: absolute; top: .42rem; left: .12rem; width: .22rem; height: .22rem; border-radius: 50%; background: var(--cv-green); }
.cv-sector-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .36rem; }
.cv-flow-item--sectors .cv-sector-grid { grid-template-columns: 1fr !important; }
.cv-sector { display: flex; align-items: center; gap: .36rem; min-height: 1.95rem; padding: .38rem .45rem; border: .0625rem solid #d9f2e2; border-radius: .5rem; background: var(--cv-soft); color: var(--cv-ink); font-size: .66rem; line-height: 1.16; font-weight: 800; break-inside: avoid; page-break-inside: avoid; }
.cv-sector i { color: var(--cv-green); flex: 0 0 auto; }
.cv-sector__copy { display: grid; gap: .08rem; }
.cv-sector__copy strong, .cv-sector__copy small { line-height: 1.12; }
.cv-sector__copy small { color: #557567; font-size: .58rem; font-weight: 700; }
.cv-extra-list { display: grid; gap: .38rem; }
.cv-extra-list li { display: grid; grid-template-columns: .95rem minmax(0, 1fr); gap: .34rem; align-items: start; color: var(--cv-ink); font-size: .69rem; line-height: 1.25; }
.cv-more-item { color: var(--cv-muted) !important; font-weight: 800 !important; }
.cv-footer { margin-top: auto; padding-top: .55rem; border-top: .0625rem solid var(--cv-line); color: var(--cv-muted); font-size: .63rem; line-height: 1.1; break-inside: avoid; page-break-inside: avoid; }
.cv-brand--small .cv-brand__logo { width: 5.8rem; max-width: 5.8rem; height: 1.45rem; max-height: 1.45rem; }

.cv-document--pdf,
.cv-document--preview {
  width: 49.625rem;
  min-width: 49.625rem;
  padding: 1.45rem 1.7rem 1.15rem;
  border-radius: .8rem;
}

.cv-document--pdf .cv-header,
.cv-document--pdf .cv-footer,
.cv-document--preview .cv-header,
.cv-document--preview .cv-footer {
  flex-direction: row;
  align-items: center;
}

.cv-document--pdf .cv-top,
.cv-document--preview .cv-top {
  flex-direction: row;
  align-items: flex-start;
}

.cv-document--pdf .cv-person,
.cv-document--preview .cv-person {
  grid-template-columns: 4.25rem minmax(0, 1fr);
}

.cv-document--pdf .cv-brand,
.cv-document--preview .cv-brand {
  flex-wrap: nowrap;
}

.cv-document--pdf .cv-header .cv-brand__logo,
.cv-document--preview .cv-header .cv-brand__logo {
  width: 8.2rem;
  max-width: 8.2rem;
  max-height: 2.15rem;
}

.cv-document--pdf .cv-footer .cv-brand__logo,
.cv-document--preview .cv-footer .cv-brand__logo {
  width: 5.8rem;
  max-width: 5.8rem;
  max-height: 1.45rem;
}

.cv-document--pdf .cv-id,
.cv-document--preview .cv-id {
  justify-items: center;
}

.cv-document--pdf .cv-qr {
  position: relative;
  display: block;
  width: 5.5rem;
  height: 5.5rem;
  padding: .24rem;
  overflow: hidden;
}

.cv-document--pdf .cv-qr img {
  width: 100%;
  height: 100%;
  max-width: 100%;
  margin: 0;
  object-fit: contain;
  object-position: center;
}

.cv-document--pdf .cv-body,
.cv-document--preview .cv-body {
  grid-template-columns: minmax(0, 1.34fr) minmax(12.5rem, 0.82fr);
}

.cv-document--pdf .cv-main,
.cv-document--preview .cv-main {
  padding-right: 1.25rem;
  border-right: .0625rem solid var(--cv-line);
}

.cv-document--pdf .cv-sector-grid,
.cv-document--preview .cv-sector-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (max-width: 40rem) {
  .cv-body { grid-template-columns: 1fr; }
  .cv-main { padding-right: 0; border-right: 0; }
}

@media (max-width: 56rem) {
  .cv-document { padding: 1.35rem; border-radius: 1rem; }
  .cv-header, .cv-top, .cv-footer { flex-direction: column; align-items: flex-start; }
  .cv-person { grid-template-columns: 1fr; }
  .cv-brand { flex-wrap: wrap; }
  .cv-brand__logo { width: 7.4rem; }
  .cv-id { justify-items: start; }
  .cv-sector-grid { grid-template-columns: 1fr; }
}
</style>
