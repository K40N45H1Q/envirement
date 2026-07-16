<script setup>
import { computed } from 'vue'
import { useI18n } from '@/i18n'

const { t } = useI18n()

const metrics = computed(() => [
  { label: t('match.experience'), width: '92%', color: '#19785a' },
  { label: t('match.language'), width: '95%', color: '#19785a' },
  { label: t('match.skills'), width: '88%', color: '#19785a' },
  { label: t('match.motivation'), width: '90%', color: '#19785a' },
])

const metricsTwo = computed(() => [
  { label: t('match.experience'), width: '75%', color: 'rgba(29, 168, 107, 0.82)' },
  { label: t('match.language'), width: '80%', color: 'rgba(29, 168, 107, 0.82)' },
  { label: t('match.skills'), width: '72%', color: 'rgba(29, 168, 107, 0.82)' },
  { label: t('match.motivation'), width: '78%', color: 'rgba(29, 168, 107, 0.82)' },
])

const metricsThree = computed(() => [
  { label: t('match.experience'), width: '40%', color: '#f5a623' },
  { label: t('match.language'), width: '50%', color: '#f5a623' },
  { label: t('match.skills'), width: '45%', color: '#f5a623' },
  { label: t('match.motivation'), width: '55%', color: '#f5a623' },
])
</script>

<template>
  <div class="match-score-section">
    <div class="match-score-title">{{ t('match.title') }}</div>

    <div class="candidate-row">
      <div class="candidate-main">
        <div class="avatar" style="background: #19785a">AV</div>
        <div class="candidate-details">
          <div class="name">{{ t('match.candidate1Name') }}</div>
          <div class="role">{{ t('match.candidate1Role') }}</div>
        </div>
      </div>
      <div class="score-block">
        <div class="score-value" style="color: #19785a">91</div>
        <div class="score-badge" style="background: #e6f0ec; color: #19785a">
          {{ t('match.candidate1Badge') }}
        </div>
      </div>
    </div>
    <div class="progress-bars">
      <div v-for="metric in metrics" :key="metric.label" class="progress-item">
        <span class="label">{{ metric.label }}</span>
        <div class="track">
          <div class="fill" :style="{ width: metric.width, background: metric.color }"></div>
        </div>
      </div>
    </div>

    <div class="candidate-row">
      <div class="candidate-main">
        <div class="avatar" style="background: rgba(29, 168, 107, 0.82)">MK</div>
        <div class="candidate-details">
          <div class="name">{{ t('match.candidate2Name') }}</div>
          <div class="role">{{ t('match.candidate2Role') }}</div>
        </div>
      </div>
      <div class="score-block">
        <div class="score-value" style="color: rgba(22, 155, 97, 0.92)">77</div>
        <div class="score-badge" style="background: rgba(29, 168, 107, 0.12); color: rgba(22, 155, 97, 0.92)">
          {{ t('match.candidate2Badge') }}
        </div>
      </div>
    </div>
    <div class="progress-bars">
      <div v-for="metric in metricsTwo" :key="metric.label" class="progress-item">
        <span class="label">{{ metric.label }}</span>
        <div class="track">
          <div class="fill" :style="{ width: metric.width, background: metric.color }"></div>
        </div>
      </div>
    </div>

    <div class="candidate-row">
      <div class="candidate-main">
        <div class="avatar" style="background: #f5a623">DP</div>
        <div class="candidate-details">
          <div class="name">{{ t('match.candidate3Name') }}</div>
          <div class="role">{{ t('match.candidate3Role') }}</div>
        </div>
      </div>
      <div class="score-block">
        <div class="score-value" style="color: #f5a623">48</div>
        <div class="score-badge" style="background: #fef3e2; color: #f5a623">
          {{ t('match.candidate3Badge') }}
        </div>
      </div>
    </div>
    <div class="progress-bars">
      <div v-for="metric in metricsThree" :key="metric.label" class="progress-item">
        <span class="label">{{ metric.label }}</span>
        <div class="track">
          <div class="fill" :style="{ width: metric.width, background: metric.color }"></div>
        </div>
      </div>
    </div>

    <div class="stats">
      <div class="stats-avatars">
        <div class="avatar" style="background: #19785a">AV</div>
        <div class="avatar" style="background: rgba(29, 168, 107, 0.82)">MK</div>
        <div class="avatar" style="background: #f5a623">DP</div>
      </div>
      <div class="stats-text">
        <strong>50 000+</strong> {{ t('match.stats') }}
      </div>
    </div>
  </div>
</template>

<style>
.match-score-section {
  cursor: default;
  user-select: none;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  min-width: 375;
}

.match-score-title {
  font-size: 15px;
  font-weight: 700;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
  color: #1e2326;
  margin-bottom: 16px;
}

.candidate-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
}

.candidate-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
  font-size: 13px;
  flex-shrink: 0;
  box-sizing: border-box;
}

.candidate-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.name {
  font-weight: 700;
  font-size: 14px;
  color: #1e2326;
}

.role {
  font-size: 12px;
  color: #999;
}

.score-block {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.score-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 12px;
}

.progress-bars {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding-bottom: 16px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 11px;
  color: #999;
  font-weight: 500;
}

.track {
  width: 100%;
  height: 4px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.fill {
  height: 100%;
  border-radius: 4px;
}

.stats {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.stats-avatars {
  display: flex;
}

.stats .avatar {
  width: 28px;
  height: 28px;
  font-size: 10px;
  border: 2px solid #fff;
  box-sizing: border-box;
}

.stats-avatars .avatar:not(:first-child) {
  margin-left: -8px;
}

.stats-text {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

.stats-text strong {
  color: #1e2326;
  font-weight: 700;
}
</style>
