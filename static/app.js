const API = window.location.origin;
const USER_KEY = 'eating_out_user_id';

let userId = parseInt(localStorage.getItem(USER_KEY), 10);

async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function show(el) { el.style.display = 'block'; }
function hide(el) { el.style.display = 'none'; }

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
}

document.getElementById('setupForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = await api('/users', {
    method: 'POST',
    body: JSON.stringify({
      daily_calorie_limit: parseInt(document.getElementById('calorieLimit').value, 10),
      daily_budget_limit: parseInt(document.getElementById('budgetLimit').value, 10),
    }),
  });
  userId = data.user_id;
  localStorage.setItem(USER_KEY, userId);
  hide(document.getElementById('setup'));
  show(document.getElementById('main'));
  await refreshSummary();
});

async function refreshSummary() {
  if (!userId) return;
  const s = await api(`/meal-logs/users/${userId}/today`);
  document.getElementById('remainingCal').textContent = s.remaining_calories;
  document.getElementById('remainingBudget').textContent = s.remaining_budget;
  document.getElementById('mealCount').textContent = s.meal_count;
}

document.getElementById('findBtn')?.addEventListener('click', async () => {
  const status = document.getElementById('locationStatus');
  const list = document.getElementById('recommendList');
  status.textContent = '位置情報を取得中...';
  list.innerHTML = '';
  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 10000 });
    });
    const lat = pos.coords.latitude;
    const lng = pos.coords.longitude;
    status.textContent = `検索中 (${lat.toFixed(4)}, ${lng.toFixed(4)})...`;
    const data = await api(`/recommend?lat=${lat}&lng=${lng}&radius_km=2&user_id=${userId}`);
    status.textContent = `${data.count}件見つかりました（予算${data.budget_limit}円・${data.calorie_limit}kcal以内）`;
    list.innerHTML = data.recommendations.map(r => `
      <div class="rec-item" data-menu-id="${r.menu_id}">
        <div class="info">
          <div class="name">${r.menu_name}</div>
          <div class="meta">${r.chain_name} ${r.restaurant_name} · ${r.price}円 · ${r.calories}kcal · ${r.distance_walk}</div>
        </div>
        <button class="log-btn" onclick="logFromRecommend(${r.menu_id})">記録</button>
      </div>
    `).join('');
  } catch (err) {
    status.textContent = 'エラー: ' + (err.message || '位置情報を取得できませんでした');
  }
});

async function logFromRecommend(menuId) {
  if (!userId) return;
  try {
    await api(`/meal-logs/users/${userId}`, {
      method: 'POST',
      body: JSON.stringify({ menu_id: menuId }),
    });
    await refreshSummary();
    alert('記録しました！');
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
  if (!menu || isNaN(cal) || isNaN(price)) {
    alert('すべて入力してください');
    return;
  }
  try {
    await api(`/meal-logs/users/${userId}`, {
      method: 'POST',
      body: JSON.stringify({
        manual_calories: cal,
        manual_price: price,
        eaten_at: new Date().toISOString(),
      }),
    });
    document.getElementById('manualMenu').value = '';
    document.getElementById('manualCal').value = '';
    document.getElementById('manualPrice').value = '';
    await refreshSummary();
    alert('記録しました！');
  } catch (e) {
    alert('記録に失敗: ' + e.message);
  }
});

document.getElementById('settingsBtn')?.addEventListener('click', async () => {
  const u = await api(`/users/${userId}`);
  document.getElementById('settingsCal').value = u.daily_calorie_limit;
  document.getElementById('settingsBudget').value = u.daily_budget_limit;
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
    }),
  });
  document.getElementById('settingsModal').style.display = 'none';
  await refreshSummary();
});

init();
