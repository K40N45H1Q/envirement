<template>
  <div class="match-score-section">
    <div class="match-score-title">Match Score — умный найм</div>

    <div class="candidate-row">
      <div class="candidate-main">
        <div class="avatar" style="background: #19785a">АВ</div>
        <div class="candidate-details">
          <div class="name">Андрей В.</div>
          <div class="role">CE · 8 лет · Рига · LAT, RUS, ENG</div>
        </div>
      </div>
      <div class="score-block">
        <div class="score-value" style="color: #19785a">91</div>
        <div class="score-badge" style="background: #e6f0ec; color: #19785a">
          Strong match
        </div>
      </div>
    </div>
    <div class="progress-bars">
      <div class="progress-item">
        <span class="label">Опыт</span>
        <div class="track">
          <div class="fill" style="width: 92%; background: #19785a"></div>
        </div>
      </div>
      <div class="progress-item">
        <span class="label">Язык</span>
        <div class="track">
          <div class="fill" style="width: 95%; background: #19785a"></div>
        </div>
      </div>
      <div class="progress-item">
        <span class="label">Навыки</span>
        <div class="track">
          <div class="fill" style="width: 88%; background: #19785a"></div>
        </div>
      </div>
      <div class="progress-item">
        <span class="label">Мотивация</span>
        <div class="track">
          <div class="fill" style="width: 90%; background: #19785a"></div>
        </div>
      </div>
    </div>

    <div class="candidate-row">
      <div class="candidate-main">
        <div class="avatar" style="background: #4a90e2">МК</div>
        <div class="candidate-details">
          <div class="name">Марис К.</div>
          <div class="role">CE · 5 лет · Елгава · LAT, RUS</div>
        </div>
      </div>
      <div class="score-block">
        <div class="score-value" style="color: #4a90e2">77</div>
        <div class="score-badge" style="background: #e8f0fe; color: #4a90e2">
          Good match
        </div>
      </div>
    </div>
    <div class="progress-bars">
      <div class="progress-item">
        <span class="label">Опыт</span>
        <div class="track">
          <div class="fill" style="width: 75%; background: #4a90e2"></div>
        </div>
      </div>
      <div class="progress-item">
        <span class="label">Язык</span>
        <div class="track">
          <div class="fill" style="width: 80%; background: #4a90e2"></div>
        </div>
      </div>
      <div class="progress-item">
        <span class="label">Навыки</span>
        <div class="track">
          <div class="fill" style="width: 72%; background: #4a90e2"></div>
        </div>
      </div>
      <div class="progress-item">
        <span class="label">Мотивация</span>
        <div class="track">
          <div class="fill" style="width: 78%; background: #4a90e2"></div>
        </div>
      </div>
    </div>

    <div class="candidate-row">
      <div class="candidate-main">
        <div class="avatar" style="background: #f5a623">ДП</div>
        <div class="candidate-details">
          <div class="name">Дмитрий П.</div>
          <div class="role">B · 2 года · Даугавпилс · RUS</div>
        </div>
      </div>
      <div class="score-block">
        <div class="score-value" style="color: #f5a623">48</div>
        <div class="score-badge" style="background: #fef3e2; color: #f5a623">
          Partial match
        </div>
      </div>
    </div>
    <div class="progress-bars">
      <div class="progress-item">
        <span class="label">Опыт</span>
        <div class="track">
          <div class="fill" style="width: 40%; background: #f5a623"></div>
        </div>
      </div>
      <div class="progress-item">
        <span class="label">Язык</span>
        <div class="track">
          <div class="fill" style="width: 50%; background: #f5a623"></div>
        </div>
      </div>
      <div class="progress-item">
        <span class="label">Навыки</span>
        <div class="track">
          <div class="fill" style="width: 45%; background: #f5a623"></div>
        </div>
      </div>
      <div class="progress-item">
        <span class="label">Мотивация</span>
        <div class="track">
          <div class="fill" style="width: 55%; background: #f5a623"></div>
        </div>
      </div>
    </div>

    <div class="stats">
      <div class="stats-avatars">
        <div class="avatar" style="background: #19785a">АВ</div>
        <div class="avatar" style="background: #4a90e2">МК</div>
        <div class="avatar" style="background: #f5a623">ДП</div>
      </div>
      <div class="stats-text">
        <strong>50 000+</strong> работодателей <br />
        уже нанимают точнее
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
