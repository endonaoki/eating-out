const API = window.location.origin;
const USER_KEY = 'eating_out_user_id';
const DEFAULT_LAT = 35.6649;
const DEFAULT_LNG = 139.3382;

let userId = parseInt(localStorage.getItem(USER_KEY), 10);
let map = null, marker = null;
let selectedLat = DEFAULT_LAT, selectedLng = DEFAULT_LNG;

async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function show(el) { if (el) el.style.display = 'block'; }
function hide(el) { if (el) el.style.display = 'none'; }

async function init() {
  if (!userId || isNaN(userId)) {
    show(document.getElementById('setup'));
    hide(document.getElementById('main'));
    return;
  }
  try {
    await api(`/users/${userId}`);
  } catch {
    localStorage.removeItem(USER_KEY);
    userId = null;
    show(document.getElementById('setup'));
    hide(document.getElementById('main'));
    return;
  }
  show(document.getElementById('main'));
  hide(document.getElementById('setup'));
  await refreshSummary();
  await loadStats('day');
}

document.getElementById('setupForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {
    daily_calorie_limit: parseInt(document.getElementById('calorieLimit').value, 10),
    daily_budget_limit: parseInt(document.getElementById('budgetLimit').value, 10),
    gender: document.getElementById('gender').value || null,
    birth_year: document.getElementById('birthYear').value ? parseInt(document.getElementById('birthYear').value, 10) : null,
  };
  const data = await api('/users', { method: 'POST', body: JSON.stringify(body) });
  userId = data.user_id;
  localStorage.setItem(USER_KEY, userId);
  hide(document.getElementById('setup'));
  show(document.getElementById('main'));
  await refreshSummary();
  await loadStats('day');
});

async function refreshSummary() {
  if (!userId) return;
  const s = await api(`/meal-logs/users/${userId}/today`);
  document.getElementById('remainingCal').textContent = s.remaining_calories;
  document.getElementById('remainingBudget').textContent = s.remaining_budget;
  document.getElementById('mealCount').textContent = s.meal_count;
}

async function searchAt(lat, lng) {
  const status = document.getElementById('locationStatus');
  const list = document.getElementById('recommendList');
  status.textContent = `検索中 (${lat.toFixed(4)}, ${lng.toFixed(4)})...`;
  list.innerHTML = '';
  try {
    const data = await api(`/recommend?lat=${lat}&lng=${lng}&radius_km=2&user_id=${userId}`);
    status.textContent = `${data.count}件（予算${data.budget_limit}円・${data.calorie_limit}kcal以内）`;
    list.innerHTML = data.recommendations.map(r => `
      <div class="rec-item">
        <div class="info">
          <div class="name">${r.menu_name}</div>
          <div class="meta">${r.chain_name} ${r.restaurant_name} · ${r.price}円 · ${r.calories}kcal · ${r.distance_walk}</div>
        </div>
        <button class="log-btn" onclick="logFromRecommend(${r.menu_id})">記録</button>
      </div>
    `).join('');
  } catch (err) {
    status.textContent = 'エラー: ' + (err.message || '検索に失敗しました');
  }
}

document.getElementById('findBtn')?.addEventListener('click', async () => {
  const status = document.getElementById('locationStatus');
  status.textContent = '位置情報を取得中...';
  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 10000 });
    });
    await searchAt(pos.coords.latitude, pos.coords.longitude);
  } catch (err) {
    status.textContent = '位置情報を取得できませんでした。地図で場所を指定してください。';
  }
});

document.getElementById('mapBtn')?.addEventListener('click', async () => {
  document.getElementById('mapModal').style.display = 'flex';
  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 3000 });
    });
    selectedLat = pos.coords.latitude;
    selectedLng = pos.coords.longitude;
  } catch (_) {
    selectedLat = DEFAULT_LAT;
    selectedLng = DEFAULT_LNG;
  }
  setTimeout(initMap, 100);
});

function initMap() {
  if (map) {
    map.setView([selectedLat, selectedLng], 15);
    if (marker) marker.setLatLng([selectedLat, selectedLng]);
    return;
  }
  map = L.map('map').setView([selectedLat, selectedLng], 15);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap'
  }).addTo(map);
  marker = L.marker([selectedLat, selectedLng], { draggable: true }).addTo(map);
  map.on('click', (e) => {
    selectedLat = e.latlng.lat;
    selectedLng = e.latlng.lng;
    marker.setLatLng([selectedLat, selectedLng]);
  });
  marker.on('dragend', () => {
    const pos = marker.getLatLng();
    selectedLat = pos.lat;
    selectedLng = pos.lng;
  });
}

document.getElementById('mapSearchBtn')?.addEventListener('click', async () => {
  document.getElementById('mapModal').style.display = 'none';
  await searchAt(selectedLat, selectedLng);
});

document.getElementById('mapClose')?.addEventListener('click', () => {
  document.getElementById('mapModal').style.display = 'none';
});

async function logFromRecommend(menuId) {
  if (!userId) return;
  try {
    await api(`/meal-logs/users/${userId}`, {
      method: 'POST',
      body: JSON.stringify({ menu_id: menuId }),
    });
    await refreshSummary();
    await loadStats(document.querySelector('.period-tabs .tab.active')?.dataset?.period || 'day');
    alert('記録しました');
  } catch (e) {
    alert('記録に失敗: ' + e.message);
  }
}
window.logFromRecommend = logFromRecommend;

document.getElementById('manualLogForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const menu = document.getElementById('manualMenu').value.trim();
  const cal = parseInt(document.getElementById('manualCal').value, 10);
  const price = parseInt(document.getElementById('manualPrice').value, 10);
  const protein = document.getElementById('manualProtein').value ? parseFloat(document.getElementById('manualProtein').value) : null;
  const fat = document.getElementById('manualFat').value ? parseFloat(document.getElementById('manualFat').value) : null;
  const carbs = document.getElementById('manualCarbs').value ? parseFloat(document.getElementById('manualCarbs').value) : null;
  if (!menu || isNaN(cal) || isNaN(price)) {
    alert('メニュー名・カロリー・金額を入力してください');
    return;
  }
  try {
    await api(`/meal-logs/users/${userId}`, {
      method: 'POST',
      body: JSON.stringify({
        manual_calories: cal,
        manual_price: price,
        manual_protein: protein,
        manual_fat: fat,
        manual_carbs: carbs,
        eaten_at: new Date().toISOString(),
      }),
    });
    document.getElementById('manualMenu').value = '';
    document.getElementById('manualCal').value = '';
    document.getElementById('manualPrice').value = '';
    document.getElementById('manualProtein').value = '';
    document.getElementById('manualFat').value = '';
    document.getElementById('manualCarbs').value = '';
    await refreshSummary();
    await loadStats(document.querySelector('.period-tabs .tab.active')?.dataset?.period || 'day');
    alert('記録しました');
  } catch (e) {
    alert('記録に失敗: ' + e.message);
  }
});

document.querySelectorAll('.period-tabs .tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.period-tabs .tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    loadStats(tab.dataset.period);
  });
});

async function loadStats(period) {
  if (!userId) return;
  const container = document.getElementById('statsContent');
  try {
    const s = await api(`/stats/users/${userId}?period=${period}`);
    const rec = s.recommended_daily;
    const avg = s.averages;
    const pct = (v, r) => r > 0 ? Math.min(100, Math.round((v / r) * 100)) : 0;
    container.innerHTML = `
      <div class="row"><span class="label">カロリー</span><span>${s.totals.calories} kcal / 日平均 ${avg.calories}</span></div>
      <div class="bar-wrap"><div class="bar" style="width:${pct(avg.calories, rec.calories)}%"></div></div>
      <div class="row"><span class="label">タンパク質</span><span>${s.totals.protein.toFixed(1)} g / 日平均 ${avg.protein}</span></div>
      <div class="bar-wrap"><div class="bar" style="width:${pct(avg.protein, rec.protein)}%"></div></div>
      <div class="row"><span class="label">脂質</span><span>${s.totals.fat.toFixed(1)} g / 日平均 ${avg.fat}</span></div>
      <div class="bar-wrap"><div class="bar" style="width:${pct(avg.fat, rec.fat)}%"></div></div>
      <div class="row"><span class="label">炭水化物</span><span>${s.totals.carbs.toFixed(1)} g / 日平均 ${avg.carbs}</span></div>
      <div class="bar-wrap"><div class="bar" style="width:${pct(avg.carbs, rec.carbs)}%"></div></div>
      <div class="row"><span class="label">外食費</span><span>${s.totals.price} 円 / 日平均 ${avg.price}</span></div>
      <p class="hint" style="margin-top:12px">推奨（1日）: カロリー${rec.calories}kcal, P${rec.protein}g, F${rec.fat}g, C${rec.carbs}g</p>
    `;
  } catch (e) {
    container.innerHTML = '<p class="hint">データを取得できませんでした</p>';
  }
}

document.getElementById('settingsBtn')?.addEventListener('click', async () => {
  const u = await api(`/users/${userId}`);
  document.getElementById('settingsCal').value = u.daily_calorie_limit;
  document.getElementById('settingsBudget').value = u.daily_budget_limit;
  document.getElementById('settingsGender').value = u.gender || '';
  document.getElementById('settingsBirthYear').value = u.birth_year || '';
  document.getElementById('settingsModal').style.display = 'flex';
});

document.getElementById('settingsClose')?.addEventListener('click', () => {
  document.getElementById('settingsModal').style.display = 'none';
});

document.getElementById('settingsForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  await api(`/users/${userId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      daily_calorie_limit: parseInt(document.getElementById('settingsCal').value, 10),
      daily_budget_limit: parseInt(document.getElementById('settingsBudget').value, 10),
      gender: document.getElementById('settingsGender').value || null,
      birth_year: document.getElementById('settingsBirthYear').value ? parseInt(document.getElementById('settingsBirthYear').value, 10) : null,
    }),
  });
  document.getElementById('settingsModal').style.display = 'none';
  await refreshSummary();
  await loadStats(document.querySelector('.period-tabs .tab.active')?.dataset?.period || 'day');
});

init();
