const rateDisplay = document.getElementById('live-rate');
const fetchedAt = document.getElementById('fetched-at');
const historyTableBody = document.querySelector('#history-table tbody');
const callsCountEl = document.getElementById('calls-count');
const lastLatencyEl = document.getElementById('last-latency');
const baseSelect = document.getElementById('base-select');
const targetSelect = document.getElementById('target-select');
const refreshBtn = document.getElementById('refresh-btn');

let callsCount = 0;
const history = [];

async function fetchRate() {
  const base = baseSelect.value;
  const target = targetSelect.value;
  const start = performance.now();
  try {
    const res = await fetch(`/api/rate?base=${base}&target=${target}`);
    const json = await res.json();
    const latency = Math.round(performance.now() - start);
    callsCount++;
    lastLatencyEl.textContent = latency;
    callsCountEl.textContent = callsCount;
    rateDisplay.textContent = json.rate ? json.rate.toFixed(6) : '--';
    fetchedAt.textContent = json.fetched_at || new Date().toISOString();
    addHistory(json.fetched_at, `${json.base}→${json.target}`, json.rate);
  } catch (err) {
    console.error(err);
  }
}

function addHistory(time, pair, rate) {
  history.unshift({ time, pair, rate });
  if (history.length > 10) history.splice(10);
  renderHistory();
}

function renderHistory() {
  historyTableBody.innerHTML = '';
  history.forEach(h => {
    const tr = document.createElement('tr');
    const t1 = document.createElement('td');
    const t2 = document.createElement('td');
    const t3 = document.createElement('td');
    t1.textContent = h.time || '--';
    t2.textContent = h.pair;
    t3.textContent = h.rate ? h.rate.toFixed(6) : '--';
    tr.appendChild(t1); tr.appendChild(t2); tr.appendChild(t3);
    historyTableBody.appendChild(tr);
  });
}

// RPS logic
document.querySelectorAll('.rps-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const player = btn.dataset.move;
    const choices = ['rock','paper','scissors'];
    const comp = choices[Math.floor(Math.random()*3)];
    const result = decide(player, comp);
    const resultEl = document.getElementById('rps-result');
    resultEl.textContent = `You: ${player} — Computer: ${comp} ⇒ ${result}`;
  });
});

function decide(p, c) {
  if (p === c) return 'Draw';
  if ((p==='rock'&&c==='scissors')||(p==='paper'&&c==='rock')||(p==='scissors'&&c==='paper')) return 'You Win';
  return 'Computer Wins';
}

refreshBtn.addEventListener('click', fetchRate);

// auto-refresh every 30s
fetchRate();
setInterval(fetchRate, 30000);
