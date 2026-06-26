<script setup>
import { ref } from 'vue'
import '@fortawesome/fontawesome-free/css/all.css'

const billingPeriod = ref('monthly')
</script>

<template>
    <section class="pricing-section">
        <!-- HOW IT WORKS -->
        <div class="how-it-works">
            <div class="section-label">КАК ЭТО РАБОТАЕТ</div>
            <h2 class="section-title">Три шага до нужного кандидата</h2>
            <p class="section-subtitle">
                Структурированные профили с обеих сторон — вакансии и кандидат<br>
                говорят на одном языке полей. Система сравнивает поле с полем.
            </p>

            <div class="steps-grid">
                <div class="step-card">
                    <div class="step-number">1</div>
                    <h3 class="step-title">Разместите вакансию</h3>
                    <p class="step-description">
                        Укажите требования: категории, опыт, навыки, права, график, локация, зарплата и др.
                    </p>
                </div>

                <div class="step-card">
                    <div class="step-number">2</div>
                    <h3 class="step-title">Получайте Score<br>по каждому отклику</h3>
                    <p class="step-description">
                        Каждый кандидат получает Match Score 0–100 по вашим критериям. Strong / Good / Partial / Weak — сразу видно, кто подходит.
                    </p>
                </div>

                <div class="step-card">
                    <div class="step-number">3</div>
                    <h3 class="step-title">Нанимайте лучшего</h3>
                    <p class="step-description">
                        Breakdown по каждому параметру в карточке. Пригласите одним кликом — кандидат получит письмо с вашими контактами.
                    </p>
                </div>

                <div class="why-card">
                    <h3 class="why-title">Почему это работает лучше</h3>
                    <ul class="why-list">
                        <li>
                            <i class="fas fa-check check-icon"></i>
                            Никаких «подходит/не подходит» вслепую
                        </li>
                        <li>
                            <i class="fas fa-check check-icon"></i>
                            Сравнение кандидатов по ключевым критериям
                        </li>
                        <li>
                            <i class="fas fa-check check-icon"></i>
                            Экономия времени рекрутера
                        </li>
                        <li>
                            <i class="fas fa-check check-icon"></i>
                            Более точные и быстрые наймы
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- PRICING -->
        <div class="pricing">
            <div class="section-label">ЦЕНЫ</div>
            <div class="pricing-header">
                <div>
                    <h2 class="section-title">Прозрачное ценообразование</h2>
                    <p class="section-subtitle">
                        Одна вакансия — 30 дней. Никакого автопродления.<br>
                        Напоминаем за 3 дня до окончания.
                    </p>
                </div>
                <div class="billing-toggle">
                    <button
                        class="toggle-btn"
                        :class="{ active: billingPeriod === 'monthly' }"
                        @click="billingPeriod = 'monthly'"
                    >
                        Ежемесячно
                    </button>
                    <button
                        class="toggle-btn"
                        :class="{ active: billingPeriod === 'yearly' }"
                        @click="billingPeriod = 'yearly'"
                    >
                        Ежегодно <span class="discount">-15%</span>
                    </button>
                </div>
            </div>

            <div class="pricing-cards">
                <div class="pricing-card">
                    <div class="plan-name">BASIC</div>
                    <div class="plan-price">
                        <span class="price">99</span>
                        <span class="currency">EUR</span>
                    </div>
                    <div class="plan-period">1 вакансия · 30 дней</div>
                    <p class="plan-description">
                        Для тех, кто нанимает редко. Полный Match Score и все инструменты фильтрации.
                    </p>
                    <ul class="plan-features">
                        <li>
                            <i class="fas fa-check feature-check"></i>
                            Match Score по каждому отклику
                        </li>
                        <li>
                            <i class="fas fa-check feature-check"></i>
                            Breakdown по параметрам
                        </li>
                        <li>
                            <i class="fas fa-check feature-check"></i>
                            Кнопка «Пригласить»
                        </li>
                    </ul>
                    <button class="btn-start">Начать</button>
                </div>

                <div class="pricing-card">
                    <div class="plan-name">STANDARD</div>
                    <div class="plan-price">
                        <span class="price">149</span>
                        <span class="currency">EUR</span>
                    </div>
                    <div class="plan-period">3 вакансии · 30 дней каждая</div>
                    <p class="plan-description">
                        Для регулярного найма. Сравнение кандидатов и история откликов по компании.
                    </p>
                    <ul class="plan-features">
                        <li>
                            <i class="fas fa-check feature-check"></i>
                            Всё из Basic
                        </li>
                        <li>
                            <i class="fas fa-check feature-check"></i>
                            Сравнение кандидатов бок о бок
                        </li>
                        <li>
                            <i class="fas fa-check feature-check"></i>
                            История откликов по компании
                        </li>
                    </ul>
                    <button class="btn-start">Начать</button>
                </div>

                <div class="pricing-card">
                    <div class="plan-name">PRO</div>
                    <div class="plan-price">
                        <span class="price">229</span>
                        <span class="currency">EUR</span>
                    </div>
                    <div class="plan-period">Безлимит вакансий · 30 дней</div>
                    <p class="plan-description">
                        Для компаний с постоянным потоком найма. Все функции без ограничений.
                    </p>
                    <ul class="plan-features">
                        <li>
                            <i class="fas fa-check feature-check"></i>
                            Всё из Standard
                        </li>
                        <li>
                            <i class="fas fa-check feature-check"></i>
                            Безлимит активных вакансий
                        </li>
                        <li>
                            <i class="fas fa-check feature-check"></i>
                            Приоритетная поддержка
                        </li>
                    </ul>
                    <button class="btn-start">Начать</button>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.pricing-section {
    max-width: 100rem;
    margin: 0 auto;
    padding: clamp(3rem, 5vw, 5rem) clamp(1rem, 2vw, 1.25rem);
    font-family: inherit;
}

/* ===== HOW IT WORKS ===== */
.how-it-works {
    margin-bottom: clamp(3rem, 5vw, 5rem);
}

.section-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #999;
    margin-bottom: 0.75rem;
}

.section-title {
    font-size: clamp(1.5rem, 4vw, 2rem);
    font-weight: 700;
    color: #1E2326;
    margin: 0 0 0.75rem;
    line-height: 1.2;
}

.section-subtitle {
    font-size: clamp(0.875rem, 1.5vw, 1rem);
    color: #666;
    margin: 0 0 2.5rem;
    line-height: 1.6;
}

.steps-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
    gap: 1.25rem;
}

.step-card, .why-card {
    background: #fff;
    border: 0.0625rem solid #e8e8e8;
    border-radius: 0.75rem;
    padding: clamp(1.5rem, 3vw, 1.75rem) clamp(1.25rem, 2vw, 1.5rem);
    position: relative;
    height: 100%;
    box-sizing: border-box;
}

.step-number {
    width: 2rem;
    height: 2rem;
    background: #19785A;
    color: #fff;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 0.8125rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.step-title, .why-title {
    font-size: clamp(1rem, 1.5vw, 1.125rem);
    font-weight: 700;
    color: #1E2326;
    margin: 0 0 0.625rem;
    line-height: 1.3;
}

.step-description {
    font-size: 0.875rem;
    color: #666;
    margin: 0;
    line-height: 1.5;
}

.why-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    gap: 0.75rem;
}

.why-list li {
    display: flex;
    align-items: flex-start;
    gap: 0.625rem;
    font-size: 0.875rem;
    color: #1E2326;
    line-height: 1.4;
}

.check-icon {
    color: #19785A;
    font-size: 0.75rem;
    margin-top: 0.125rem;
    flex-shrink: 0;
}

/* ===== PRICING ===== */
.pricing {
    border-top: 0.0625rem solid #e8e8e8;
    padding-top: clamp(2.5rem, 4vw, 3.75rem);
}

.pricing-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2.5rem;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.billing-toggle {
    display: flex;
    background: #f5f5f5;
    border-radius: 0.5rem;
    padding: 0.25rem;
    flex-shrink: 0;
}

.toggle-btn {
    padding: 0.625rem 1.25rem;
    border: none;
    background: transparent;
    font-size: 0.875rem;
    font-weight: 600;
    color: #666;
    cursor: pointer;
    border-radius: 0.375rem;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.375rem;
    font-family: inherit;
}

.toggle-btn.active {
    background: #19785A;
    color: #fff;
}

.discount {
    font-size: 0.75rem;
    color: #19785A;
    font-weight: 600;
}

.toggle-btn.active .discount {
    color: #fff;
}

.pricing-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr));
    gap: 1.25rem;
}

.pricing-card {
    background: #fff;
    /*统一的绿色边框风格*/
    border: 0.125rem solid #19785A;
    border-radius: 0.75rem;
    padding: clamp(1.75rem, 3vw, 2rem) clamp(1.5rem, 2vw, 1.75rem);
    display: flex;
    flex-direction: column;
    height: 100%;
    box-sizing: border-box;
}

.plan-name {
    font-size: 0.8125rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.0625rem;
    color: #1E2326;
    margin-bottom: 0.5rem;
}

.plan-price {
    margin-bottom: 0.25rem;
}

.price {
    font-size: clamp(2rem, 4vw, 2.5rem);
    font-weight: 700;
    color: #1E2326;
    line-height: 1;
}

.currency {
    font-size: 1rem;
    font-weight: 600;
    color: #1E2326;
    margin-left: 0.25rem;
}

.plan-period {
    font-size: 0.8125rem;
    color: #999;
    margin-bottom: 1rem;
}

.plan-description {
    font-size: 0.875rem;
    color: #666;
    margin: 0 0 1.25rem;
    line-height: 1.5;
    flex-grow: 1;
}

.plan-features {
    list-style: none;
    padding: 0;
    margin: 0 0 1.5rem;
    display: grid;
    gap: 0.625rem;
}

.plan-features li {
    display: flex;
    align-items: flex-start;
    gap: 0.625rem;
    font-size: 0.875rem;
    color: #1E2326;
    line-height: 1.4;
}

.feature-check {
    color: #19785A;
    font-size: 0.75rem;
    margin-top: 0.125rem;
    flex-shrink: 0;
}

.btn-start {
    width: 100%;
    padding: 0.875rem;
    /*统一的绿色按钮风格*/
    border: 0.125rem solid #19785A;
    background: #19785A;
    color: #fff;
    font-size: 0.875rem;
    font-weight: 700;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: inherit;
}

.btn-start:hover {
    background: #146a4f;
    border-color: #146a4f;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 56.25rem) {
    .steps-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 48rem) {
    .pricing-header {
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .billing-toggle {
        width: 100%;
        justify-content: center;
    }
    
    .toggle-btn {
        flex: 1;
        justify-content: center;
    }
}

@media (max-width: 30rem) {
    .steps-grid {
        grid-template-columns: 1fr;
    }
    
    .pricing-cards {
        grid-template-columns: 1fr;
    }
}
</style>