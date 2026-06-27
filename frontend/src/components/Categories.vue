<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="popular-section">
    <h2 class="pupular-section-title">Популярные категории</h2>
    <div class="popular-grid">
      <RouterLink
        :to="{ path: '/jobs', query: { category: 'construction' } }"
        class="category-card"
      >
        <div class="card-icon-wrapper">
          <svg
            viewBox="0 0 68 56"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M61.8182 49.7778H68V56H0V49.7778H6.18182V3.11111C6.18182 2.28599 6.50747 1.49467 7.08712 0.911223C7.66678 0.327777 8.45297 0 9.27273 0H40.1818C41.0016 0 41.7878 0.327777 42.3674 0.911223C42.9471 1.49467 43.2727 2.28599 43.2727 3.11111V49.7778H49.4545V18.6667H58.7273C59.547 18.6667 60.3332 18.9944 60.9129 19.5779C61.4925 20.1613 61.8182 20.9527 61.8182 21.7778V49.7778Z"
              fill="url(#grad1)"
            />
            <defs>
              <linearGradient
                id="grad1"
                x1="0"
                y1="0"
                x2="80"
                y2="80"
                gradientUnits="userSpaceOnUse"
              >
                <stop stop-color="#19785A" />
                <stop offset="1" stop-color="#19785A" stop-opacity="0" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h3 class="card-title">Строительство</h3>
        <p class="card-vacancies">200 вакансий</p>
      </RouterLink>

      <RouterLink
        :to="{ path: '/jobs', query: { category: 'production' } }"
        class="category-card"
      >
        <div class="card-icon-wrapper">
          <svg
            viewBox="0 0 56 56"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <g clip-path="url(#clip0_178_291)">
              <path
                d="M15.4 4.55C13.3 5.6 12.6 8.4 14 9.8C15.75 6.65 18.55 7.7 22.75 11.2C25.55 13.65 29.4 11.55 29.4 11.55C29.4 11.55 30.1 15.75 35.35 16.45C41.3 17.15 43.4 13.65 43.4 13.65C43.4 13.65 44.8 17.15 50.05 15.05C53.9 13.65 52.5 11.2 52.5 11.2C52.5 11.2 56 11.2 56 8.75C56 5.6 52.15 5.95 52.15 5.95C52.15 5.95 52.85 2.45 49 2.1C45.5 1.75 44.45 3.85 44.45 3.85C44.45 3.85 43.4 0 38.15 0C33.25 0 31.5 4.55 31.5 4.55C31.5 4.55 30.1 2.45 25.9 2.45C22.75 2.45 21.35 4.9 21.35 4.9C21.35 4.9 17.5 3.15 15.4 4.55Z"
                fill="url(#paint0_linear_178_291)"
              />
              <path
                d="M42 42.35V35L28 42.35V35H19.6L17.5 10.5H10.5L8.4 35H0V56H56V35L42 42.35ZM21 49H7V42H21V49Z"
                fill="url(#paint1_linear_178_291)"
              />
            </g>
            <defs>
              <linearGradient
                id="paint0_linear_178_291"
                x1="26.5119"
                y1="-9.11907e-07"
                x2="53.0631"
                y2="24.4755"
                gradientUnits="userSpaceOnUse"
              >
                <stop stop-color="#19785A" />
                <stop offset="1" stop-color="#19785A" stop-opacity="0" />
              </linearGradient>
              <linearGradient
                id="paint1_linear_178_291"
                x1="14.4402"
                y1="10.5"
                x2="51.3007"
                y2="68.3357"
                gradientUnits="userSpaceOnUse"
              >
                <stop stop-color="#19785A" />
                <stop offset="1" stop-color="#19785A" stop-opacity="0" />
              </linearGradient>
              <clipPath id="clip0_178_291">
                <rect width="56" height="56" fill="white" />
              </clipPath>
            </defs>
          </svg>
        </div>
        <h3 class="card-title">Производство</h3>
        <p class="card-vacancies">200 вакансий</p>
      </RouterLink>

      <RouterLink
        :to="{ path: '/jobs', query: { category: 'logistics' } }"
        class="category-card"
      >
        <div class="card-icon-wrapper">
          <svg
            viewBox="0 0 74 74"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M55.5 57.0417C54.2734 57.0417 53.097 56.5544 52.2296 55.6871C51.3623 54.8197 50.875 53.6433 50.875 52.4167C50.875 51.1901 51.3623 50.0137 52.2296 49.1463C53.097 48.279 54.2734 47.7917 55.5 47.7917C56.7266 47.7917 57.903 48.279 58.7703 49.1463C59.6377 50.0137 60.125 51.1901 60.125 52.4167C60.125 53.6433 59.6377 54.8197 58.7703 55.6871C57.903 56.5544 56.7266 57.0417 55.5 57.0417ZM60.125 29.2917L66.1683 37H52.4166V29.2917M18.5 57.0417C17.2734 57.0417 16.097 56.5544 15.2296 55.6871C14.3623 54.8197 13.875 53.6433 13.875 52.4167C13.875 51.1901 14.3623 50.0137 15.2296 49.1463C16.097 48.279 17.2734 47.7917 18.5 47.7917C19.7266 47.7917 20.903 48.279 21.7703 49.1463C22.6377 50.0137 23.125 51.1901 23.125 52.4167C23.125 53.6433 22.6377 54.8197 21.7703 55.6871C20.903 56.5544 19.7266 57.0417 18.5 57.0417ZM61.6666 24.6667H52.4166V12.3334H9.24998C5.82748 12.3334 3.08331 15.0775 3.08331 18.5V52.4167H9.24998C9.24998 54.87 10.2245 57.2227 11.9592 58.9574C13.694 60.6922 16.0467 61.6667 18.5 61.6667C20.9532 61.6667 23.306 60.6922 25.0407 58.9574C26.7754 57.2227 27.75 54.87 27.75 52.4167H46.25C46.25 54.87 47.2245 57.2227 48.9592 58.9574C50.694 60.6922 53.0467 61.6667 55.5 61.6667C57.9532 61.6667 60.306 60.6922 62.0407 58.9574C63.7754 57.2227 64.75 54.87 64.75 52.4167H70.9166V37L61.6666 24.6667Z"
              fill="url(#paint0_linear_178_258)"
            />
            <defs>
              <linearGradient
                id="paint0_linear_178_258"
                x1="15.3696"
                y1="12.3334"
                x2="75.2068"
                y2="76.4126"
                gradientUnits="userSpaceOnUse"
              >
                <stop stop-color="#19785A" />
                <stop offset="1" stop-color="#19785A" stop-opacity="0" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h3 class="card-title">Логистика</h3>
        <p class="card-vacancies">200 вакансий</p>
      </RouterLink>

      <RouterLink
        :to="{ path: '/jobs', query: { category: 'it' } }"
        class="category-card"
      >
        <div class="card-icon-wrapper">
          <svg
            viewBox="0 0 72 72"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M39 54V60H51V66H21V60H33V54H8.97598C8.58201 53.9969 8.19251 53.9161 7.82974 53.7625C7.46696 53.6088 7.13801 53.3852 6.86166 53.1044C6.58531 52.8236 6.36697 52.4911 6.21913 52.1259C6.07128 51.7607 5.99681 51.37 5.99997 50.976V12.024C5.99997 10.353 7.36497 9 8.97598 9H63.024C64.668 9 66 10.347 66 12.021V50.976C66 52.647 64.635 54 63.024 54H39Z"
              fill="url(#paint0_linear_178_267)"
            />
            <defs>
              <linearGradient
                id="paint0_linear_178_267"
                x1="35.9999"
                y1="9"
                x2="66"
                y2="69"
                gradientUnits="userSpaceOnUse"
              >
                <stop stop-color="#19785A" />
                <stop offset="1" stop-color="#19785A" stop-opacity="0" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h3 class="card-title">IT и технологии</h3>
        <p class="card-vacancies">200 вакансий</p>
      </RouterLink>

      <RouterLink :to="{ path: '/jobs', query: { category: 'health' } }" class="category-card">
        <div class="card-icon-wrapper">
          <svg
            viewBox="0 0 64 57"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M25.6088 0L19.2177 6.33333V12.6667H9.63095C5.95604 12.6667 3.62326 15.8333 3.2398 19L0.0442174 50.6667C-0.339252 53.8333 1.76983 57 6.43537 57H57.5646C62.2302 57 64.3392 53.8333 63.9558 50.6667L60.7602 19C60.3767 15.8333 57.7564 12.6667 54.369 12.6667H44.7823V6.33333L38.3912 0H25.6088ZM25.6088 6.33333H38.3912V12.6667H25.6088V6.33333ZM28.8044 22.1667H35.1956V31.6667H44.7823V38H35.1956V47.5H28.8044V38H19.2177V31.6667H28.8044V22.1667Z"
              fill="url(#paint0_linear_178_271)"
            />
            <defs>
              <linearGradient
                id="paint0_linear_178_271"
                x1="7.90313"
                y1="2.04079e-06"
                x2="69"
                y2="67"
                gradientUnits="userSpaceOnUse"
              >
                <stop stop-color="#19785A" />
                <stop offset="1" stop-color="#19785A" stop-opacity="0" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h3 class="card-title">Медицина</h3>
        <p class="card-vacancies">200 вакансий</p>
      </RouterLink>

      <RouterLink
        :to="{ path: '/jobs', query: { category: 'hospitality' } }"
        class="category-card"
      >
        <div class="card-icon-wrapper">
          <svg
            viewBox="0 0 42 54"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M34.702 3.29341V0H7.50975V3.36167H0.0164687V4.47938C0.0164687 10.5479 0.0305848 16.6164 0 22.6849V53.7099H0.0541116C0.0541116 53.791 0.0517589 53.8741 0.0470536 53.9552H19.4261V43.8339H23.1339V54H42V3.29341H34.702ZM15.6265 40.067H12.0575V36.8184H15.6265V40.067ZM15.6265 33.2925H12.0575V30.0438H15.6265V33.2925ZM15.6265 26.7291H12.0763V23.4933H15.6265V26.7291ZM19.379 26.759C19.379 25.8034 19.3414 24.867 19.4119 23.937C19.4237 23.7599 19.8519 23.4826 20.1036 23.4677C21.0282 23.4101 21.9599 23.4442 22.9833 23.4442V26.759H19.379ZM22.981 40.0905H19.4731V36.8184H22.981V40.0905ZM23.0115 33.3479H19.4566V30.063H23.0115V33.3479ZM26.7358 18.8881H23.1056V15.1488H19.4425V18.8838H15.7888V7.88158H19.3649V11.5995H23.0398V7.89224H26.7358V18.8881ZM26.8605 30.0609H30.4507V33.2903H26.8605V30.0609ZM30.4625 40.1054H26.8935V36.861H30.4625V40.1054ZM30.4789 26.7483H26.8746V23.5189H30.4789V26.7483Z"
              fill="url(#paint0_linear_178_279)"
            />
            <defs>
              <linearGradient
                id="paint0_linear_178_279"
                x1="3.98716"
                y1="4.68774e-07"
                x2="48.369"
                y2="76.1664"
                gradientUnits="userSpaceOnUse"
              >
                <stop stop-color="#19785A" />
                <stop offset="1" stop-color="#19785A" stop-opacity="0" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h3 class="card-title">Гостиничный бизнес</h3>
        <p class="card-vacancies">200 вакансий</p>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.popular-section {
  width: 100%;
  max-width: 100rem;
  margin: 0 auto;
  padding: clamp(0.75rem, 2vw, 1.25rem);
  background: #fff;
  border-radius: 0.75rem;
  box-shadow: 0 0.125rem 0.75rem rgba(0, 0, 0, 0.08);
  box-sizing: border-box;
  margin-top: 1.25rem;
}

.pupular-section-title {
  margin: 0 0 1.25rem 0;
  font-weight: 700;
  font-size: clamp(1.25rem, 2.5vw, 1.5rem);
  color: #1e2326;
}

.popular-grid {
  display: grid;
  /* Гарантирует минимум 2 колонки, даже на очень узких экранах */
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  gap: 1rem;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: clamp(1rem, 2vw, 1.25rem) clamp(0.5rem, 1vw, 0.75rem);
  border-radius: 0.75rem;
  background: #fff;
  box-shadow: 0 0 1.25rem rgba(0, 0, 0, 0.04);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  cursor: pointer;
  box-sizing: border-box;
  height: 100%;
  text-decoration: none;
  color: inherit;
}

.category-card:hover {
  transform: translateY(-0.25rem);
  box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.08);
}

.card-icon-wrapper {
  width: 3rem;
  height: 3rem;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon-wrapper svg {
  width: 100%;
  height: 100%;
  display: block;
}

.card-title {
  margin: 0;
  min-height: 2.4em;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-weight: 700;
  font-size: clamp(0.875rem, 1.5vw, 1rem);
  line-height: 1.25;
  color: #1e2326;
}

.card-vacancies {
  margin-top: auto;
  margin-bottom: 0;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
  line-height: 1.3;
  color: rgba(30, 35, 38, 0.5);
}

/* Адаптив для средних экранов - 3 в ряд */
@media (max-width: 87.5rem) {
  .popular-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Адаптив для планшетов - 2 в ряд (минимум) */
@media (max-width: 48rem) {
  .popular-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
}
</style>
