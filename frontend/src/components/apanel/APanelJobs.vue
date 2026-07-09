<script setup>
defineProps({
  jobs: {
    type: Array,
    default: () => [],
  },
  moderation: {
    type: Boolean,
    default: false,
  },
  emptyText: {
    type: String,
    default: 'Нет вакансий',
  },
})

const emit = defineEmits(['approve', 'reject'])

const formatDate = (value) => {
  if (!value) return '-'
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

const statusLabel = (value) => {
  const labels = {
    pending: 'На модерации',
    approved: 'Одобрена',
    rejected: 'Отклонена',
    active: 'Активна',
    inactive: 'Неактивна',
  }
  return labels[value] || value || '-'
}
</script>

<template>
  <section class="apanel-card">
    <div class="apanel-table-wrap">
      <table v-if="jobs.length" class="apanel-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Вакансия</th>
            <th>Компания</th>
            <th>Статус</th>
            <th>Локация</th>
            <th>Зарплата</th>
            <th>Employer ID</th>
            <th>Создана</th>
            <th v-if="moderation"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id">
            <td><span class="apanel-id">#{{ job.id }}</span></td>
            <td>
              <div class="apanel-job-title">
                <span>{{ job.title }}</span>
                <small>{{ job.location || 'Локация не указана' }}</small>
              </div>
            </td>
            <td>{{ job.company || '-' }}</td>
            <td>
              <span class="apanel-pill" :class="`apanel-pill--${job.status || 'default'}`">
                {{ statusLabel(job.status) }}
              </span>
            </td>
            <td>{{ job.location || '-' }}</td>
            <td>{{ job.salary || '-' }}</td>
            <td><span class="apanel-id">#{{ job.user_id }}</span></td>
            <td>{{ formatDate(job.created_at) }}</td>
            <td v-if="moderation" class="apanel-actions">
              <button type="button" class="btn-primary" @click="emit('approve', job)">Одобрить</button>
              <button type="button" class="btn-secondary" @click="emit('reject', job)">Отклонить</button>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else class="apanel-empty">{{ emptyText }}</p>
    </div>
  </section>
</template>

<style scoped>
.apanel-card {
  border: 0.0625rem solid var(--border-subtle);
  border-radius: 0.95rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(250, 253, 251, 0.98)),
    var(--surface-primary);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
}

.apanel-table-wrap {
  width: 100%;
  overflow-x: auto;
}

.apanel-table {
  width: 100%;
  min-width: 60rem;
  border-collapse: separate;
  border-spacing: 0;
}

.apanel-table th,
.apanel-table td {
  padding: 0.85rem 0.8rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
  color: var(--text-primary);
  text-align: left;
  vertical-align: middle;
}

.apanel-table th {
  background: color-mix(in srgb, var(--brand-soft) 42%, white);
  color: color-mix(in srgb, var(--text-muted) 86%, var(--brand-strong));
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.apanel-table tbody tr:last-child td {
  border-bottom: 0;
}

.apanel-table tbody tr {
  transition: background 0.16s ease;
}

.apanel-table tbody tr:hover {
  background: color-mix(in srgb, var(--brand-soft) 34%, transparent);
}

.apanel-id {
  color: var(--text-muted);
  font-weight: 800;
}

.apanel-job-title {
  display: grid;
  gap: 0.18rem;
}

.apanel-job-title span {
  font-weight: 850;
}

.apanel-job-title small {
  color: var(--text-muted);
}

.apanel-pill {
  display: inline-flex;
  min-height: 1.8rem;
  align-items: center;
  padding: 0.25rem 0.65rem;
  border-radius: 999rem;
  background: color-mix(in srgb, var(--brand-soft) 76%, white);
  color: var(--brand-strong);
  font-size: 0.78rem;
  font-weight: 800;
}

.apanel-pill--pending {
  background: #fff7ed;
  color: #c2410c;
}

.apanel-pill--approved,
.apanel-pill--active {
  background: color-mix(in srgb, var(--brand-soft) 78%, white);
  color: var(--brand-strong);
}

.apanel-pill--rejected,
.apanel-pill--inactive {
  background: #fff1f2;
  color: #be123c;
}

.apanel-actions {
  display: flex;
  gap: 0.5rem;
  white-space: nowrap;
}

.btn-primary,
.btn-secondary {
  min-height: 2.35rem;
  padding: 0.55rem 0.85rem;
  border: 0.0625rem solid transparent;
  border-radius: 0.72rem;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 850;
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.btn-primary {
  background: linear-gradient(135deg, var(--brand-base), var(--brand-strong));
  color: white;
  box-shadow: 0 0.6rem 1.1rem rgba(22, 155, 97, 0.18);
}

.btn-secondary {
  border-color: color-mix(in srgb, var(--border-subtle) 70%, var(--brand-base));
  background: var(--surface-secondary);
  color: var(--text-primary);
}

.btn-primary:hover,
.btn-secondary:hover {
  transform: translateY(-0.08rem);
}

.apanel-empty {
  margin: 0;
  padding: 3rem 1.5rem;
  background:
    radial-gradient(circle at top, color-mix(in srgb, var(--brand-soft) 50%, transparent), transparent 44%),
    transparent;
  color: var(--text-muted);
  text-align: center;
  font-weight: 800;
}
</style>
