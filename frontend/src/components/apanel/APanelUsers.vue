<script setup>
defineProps({
  users: {
    type: Array,
    default: () => [],
  },
  emptyText: {
    type: String,
    default: 'Нет данных',
  },
})

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

const roleLabel = (value) => {
  const labels = {
    admin: 'Админ',
    candidate: 'Кандидат',
    user: 'Кандидат',
    employer: 'Работодатель',
  }
  return labels[value] || value || '-'
}

const statusLabel = (value) => {
  const labels = {
    active: 'Активен',
    inactive: 'Неактивен',
    blocked: 'Заблокирован',
  }
  return labels[value] || value || 'Активен'
}
</script>

<template>
  <section class="apanel-card">
    <div class="apanel-table-wrap">
      <table v-if="users.length" class="apanel-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Имя / компания</th>
            <th>Email</th>
            <th>Роль</th>
            <th>Статус</th>
            <th>Beta</th>
            <th>Телефон</th>
            <th>Дата создания</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td><span class="apanel-id">#{{ user.id }}</span></td>
            <td>
              <div class="apanel-user">
                <span>{{ user.company_name || user.full_name || '-' }}</span>
                <small>{{ user.account_type === 'employer' ? 'Компания' : 'Профиль' }}</small>
              </div>
            </td>
            <td><span class="apanel-email">{{ user.email }}</span></td>
            <td>
              <span class="apanel-pill">{{ roleLabel(user.account_type) }}</span>
            </td>
            <td>
              <span class="apanel-status-pill">{{ statusLabel(user.status) }}</span>
            </td>
            <td>
              <span class="apanel-beta" :class="{ 'apanel-beta--active': user.has_beta_access }">
                {{ user.has_beta_access ? 'Есть' : 'Нет' }}
              </span>
            </td>
            <td>{{ user.phone || '-' }}</td>
            <td>{{ formatDate(user.created_at) }}</td>
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
  min-width: 56rem;
  border-collapse: separate;
  border-spacing: 0;
}

.apanel-table th,
.apanel-table td {
  padding: 0.85rem 0.8rem;
  border-bottom: 0.0625rem solid var(--border-subtle);
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

.apanel-table td {
  color: var(--text-primary);
  font-size: 0.92rem;
}

.apanel-table tbody tr {
  transition: background 0.16s ease;
}

.apanel-table tbody tr:hover {
  background: color-mix(in srgb, var(--brand-soft) 34%, transparent);
}

.apanel-table tbody tr:last-child td {
  border-bottom: 0;
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

.apanel-id {
  color: var(--text-muted);
  font-weight: 800;
}

.apanel-user {
  display: grid;
  gap: 0.16rem;
}

.apanel-user span {
  font-weight: 800;
}

.apanel-user small,
.apanel-email {
  color: var(--text-muted);
}

.apanel-status-pill,
.apanel-beta {
  display: inline-flex;
  min-height: 1.75rem;
  align-items: center;
  padding: 0.22rem 0.62rem;
  border-radius: 999rem;
  font-size: 0.76rem;
  font-weight: 900;
}

.apanel-status-pill {
  background: color-mix(in srgb, var(--surface-secondary) 84%, var(--brand-soft));
  color: var(--text-primary);
}

.apanel-beta {
  background: color-mix(in srgb, #f1f5f9 78%, white);
  color: var(--text-muted);
}

.apanel-beta--active {
  background: color-mix(in srgb, var(--brand-soft) 78%, white);
  color: var(--brand-strong);
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
