<template>
  <section class="comparison-shell">
    <div class="comparison-card">
      <article class="comparison-column comparison-column--current">
        <p class="comparison-eyebrow">Как сейчас</p>
        <p class="comparison-lead">
          Вы размещаете вакансию, приходят отклики. Дальше — открываете каждое резюме, читаете, решаете на глаз.
          При большом количестве откликов это занимает очень много времени.
        </p>

        <ul class="comparison-list comparison-list--current">
          <li>Все кандидаты в одной куче без приоритета</li>
          <li>Чтобы понять кто подходит — нужно прочитать каждое резюме</li>
          <li>Вакансии закрываются, но процесс занимает слишком много времени из-за ручного отбора кандидатов.</li>
        </ul>
      </article>

      <article class="comparison-column comparison-column--cvhold">
        <p class="comparison-eyebrow">С CVHOLD</p>
        <p class="comparison-lead">
          Кандидаты отсортированы по баллу совпадения с вашей вакансией ещё до того, как вы открыли первое резюме.
          Начинаете с тех, кто подходит лучше всего.
        </p>

        <ul class="comparison-list comparison-list--cvhold">
          <li>Отклики сразу расставлены по приоритету — кто подходит лучше всего виден с первого экрана</li>
          <li>Начинаете с топ-кандидатов — не тратите время на тех кто заведомо не подходит</li>
          <li>Видите ключевые данные до контакта — связываетесь только с тем кто реально интересен</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<style scoped>
.comparison-shell {
  width: min(100%, var(--shell-max-width));
  margin: 0 auto;
  padding: 0 var(--shell-gutter);
}

.comparison-card {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  padding: clamp(2rem, 5vw, 4rem);
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 1.5rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 252, 249, 0.98));
  box-shadow: var(--shadow-soft);
}

.comparison-column {
  min-width: 0;
}

.comparison-column--cvhold {
  padding-left: clamp(2rem, 5vw, 4rem);
  border-left: 0.0625rem solid var(--border-subtle);
}

.comparison-column--current {
  padding-right: clamp(2rem, 5vw, 4rem);
}

.comparison-eyebrow {
  margin: 0 0 0.9rem;
  color: color-mix(in srgb, var(--brand-strong) 68%, #9b6b3d);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}

.comparison-lead {
  max-width: 31rem;
  margin: 0 0 1.4rem;
  color: var(--text-muted);
  line-height: 1.65;
}

.comparison-list {
  list-style: none;
  display: grid;
  padding: 0;
  margin: 0;
}

.comparison-list li {
  position: relative;
  min-height: 3rem;
  padding: 0.8rem 0 0.8rem 1.5rem;
  border-top: 0.0625rem solid var(--border-subtle);
  color: var(--text-primary);
  line-height: 1.45;
}

.comparison-list li:last-child {
  border-bottom: 0.0625rem solid var(--border-subtle);
}

.comparison-list--current li::before {
  content: '-';
  position: absolute;
  top: 0.8rem;
  left: 0;
  color: color-mix(in srgb, var(--text-muted) 76%, transparent);
  font-weight: 800;
}

.comparison-list--cvhold li::before {
  content: '✓';
  position: absolute;
  top: 0.8rem;
  left: 0;
  color: var(--brand-strong);
  font-weight: 900;
}

@media (max-width: 58rem) {
  .comparison-card {
    grid-template-columns: 1fr;
    padding: 1.5rem;
  }

  .comparison-column--current {
    padding-right: 0;
    padding-bottom: 1.5rem;
  }

  .comparison-column--cvhold {
    padding-top: 1.5rem;
    padding-left: 0;
    border-top: 0.0625rem solid var(--border-subtle);
    border-left: 0;
  }
}
</style>
