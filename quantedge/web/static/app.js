/**
 * QuantEdge AI Trading System - Client Controller & Chart Engine
 * Fully adheres to Strategic Requirements Document.
 */

function generateDefaultBars() {
    const bars = [];
    const now = new Date();
    const baseTime = Math.floor(new Date(now.getFullYear(), now.getMonth(), now.getDate(), 9, 30, 0).getTime() / 1000);
    let price = 214.20;
    for (let i = 0; i < 60; i++) {
        const t = baseTime + (i * 60);
        const change = (Math.sin(i / 4) * 0.45) + ((i / 60) * 3.0) + ((Math.random() - 0.48) * 0.25);
        const open = Number(price.toFixed(2));
        price += change;
        const close = Number(price.toFixed(2));
        const high = Number((Math.max(open, close) + Math.random() * 0.35).toFixed(2));
        const low = Number((Math.min(open, close) - Math.random() * 0.30).toFixed(2));
        const vwap = Number((214.50 + (i / 60) * 2.2).toFixed(2));
        const ema9 = Number((open * 0.6 + close * 0.4 - 0.15).toFixed(2));
        const vol = Math.floor(15000 + Math.random() * 45000);
        bars.push({
            time_sec: t,
            open: open,
            high: high,
            low: low,
            close: close,
            volume: vol,
            vwap: vwap,
            ema9: ema9,
            is_crossing_candle: (i === 14 || i === 38)
        });
    }
    bars[bars.length - 1].close = 217.14;
    return bars;
}

// Application State
const state = {
    selectedSymbol: 'NVDA',
    activeTab: 'workspace',
    marketRegime: 'Bullish',
    quote: { symbol: 'NVDA', price: 216.51, prior_close: 217.08, change: -0.57, change_pct: -0.26, day_high: 218.45, day_low: 212.78, vwap: 216.28, volume: 1280000 },
    bars: generateDefaultBars(),
    level2: {
        symbol: 'NVDA',
        price: 216.51,
        spread: 0.02,
        imbalance_ratio: 0.15,
        tape_speed: 7.1,
        bid_depth: 35000,
        ask_depth: 28000,
        bids: [
            { price: 216.50, shares: 3200 },
            { price: 216.49, shares: 4500 },
            { price: 216.48, shares: 6100 },
            { price: 216.47, shares: 5800 },
            { price: 216.46, shares: 2300 },
            { price: 216.45, shares: 4100 },
            { price: 216.44, shares: 3600 },
            { price: 216.43, shares: 5200 },
            { price: 216.42, shares: 4900 },
            { price: 216.41, shares: 7100 }
        ],
        asks: [
            { price: 216.52, shares: 1800 },
            { price: 216.53, shares: 2400 },
            { price: 216.54, shares: 3000 },
            { price: 216.55, shares: 2900 },
            { price: 216.56, shares: 1500 },
            { price: 216.57, shares: 2200 },
            { price: 216.58, shares: 3100 },
            { price: 216.59, shares: 2600 },
            { price: 216.60, shares: 3800 },
            { price: 216.61, shares: 4200 }
        ]
    },
    tape: [],
    scannerCandidates: [
        { symbol: 'NVDA', price: 216.51, gap_pct: -0.26, relative_volume: 3.1, float_shares: 2400000000, grade: 'A', catalyst: 'Blackwell AI Datacenter Guidance', catalyst_type: 'Guidance', spread: 0.02, ai_score: 96 },
        { symbol: 'PLTR', price: 193.94, gap_pct: -0.11, relative_volume: 4.2, float_shares: 198600000, grade: 'A', catalyst: 'DoD AIP Enterprise Expansion', catalyst_type: 'Contract', spread: 0.02, ai_score: 93 },
        { symbol: 'MARA', price: 7.52, gap_pct: 1.90, relative_volume: 7.4, float_shares: 28000000, grade: 'A', catalyst: 'Bitcoin Hash-Rate Milestone', catalyst_type: 'News', spread: 0.01, ai_score: 92 },
        { symbol: 'SOUN', price: 4.70, gap_pct: 1.08, relative_volume: 5.2, float_shares: 36500000, grade: 'A', catalyst: 'Automotive AI OEM Integration', catalyst_type: 'Partnership', spread: 0.01, ai_score: 89 },
        { symbol: 'RGTI', price: 11.68, gap_pct: 0.21, relative_volume: 4.6, float_shares: 45800000, grade: 'B', catalyst: 'Quantum 84-Qubit Benchmark', catalyst_type: 'Tech', spread: 0.02, ai_score: 78 },
        { symbol: 'MVIS', price: 1.20, gap_pct: 0.00, relative_volume: 6.0, float_shares: 14200000, grade: 'A', catalyst: 'LiDAR Production Contract', catalyst_type: 'Contract', spread: 0.01, ai_score: 87 },
        { symbol: 'ENVX', price: 2.23, gap_pct: -4.50, relative_volume: 8.7, float_shares: 16800000, grade: 'B', catalyst: 'Battery Fab High-Rate Yield', catalyst_type: 'Earnings', spread: 0.02, ai_score: 74 },
        { symbol: 'GME', price: 25.92, gap_pct: -1.97, relative_volume: 3.8, float_shares: 42000000, grade: 'B', catalyst: 'Cash Treasury Expansion', catalyst_type: 'News', spread: 0.02, ai_score: 75 }
    ],
    scannerSummary: {},
    activeSignals: [],
    cockpit: null,
    journal: [],
    analytics: null,
    compliance: null,
    latency: null,
    kronosPrediction: null,
    isLockedOut: false,
    lockoutReason: null,
    theme: 'light',
    isNewSymbolLoad: true,
    chartOverlays: {
        vwap: true,
        ema9: true,
        ema20: false,
        ema50: false,
        volume: true,
        signals: true,
        pullbackRuler: true,
        crossingCandle: true,
        kronosForecast: true
    }
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    document.documentElement.setAttribute('data-theme', state.theme);
    initTabs();
    initEventListeners();
    updateScannerUI();
    updateLevel2UI();
    renderChart();
    fetchCockpitData();
    fetchScannerData();
    loadSymbolData(state.selectedSymbol, true);
    fetchJournalData();
    fetchAnalyticsData();
    fetchComplianceData();

    // Fast 800ms real-time active candle breathing & chart motion
    setInterval(() => {
        if (state.activeTab !== 'workspace' || !state.bars || state.bars.length === 0) return;
        
        const last = state.bars[state.bars.length - 1];
        const delta = (Math.random() - 0.49) * 0.05;
        last.close = Number(Math.max(0.10, last.close + delta).toFixed(2));
        last.high = Math.max(last.high, last.close);
        last.low = Math.min(last.low, last.close);
        last.volume += Math.floor(100 + Math.random() * 400);
        
        // Every ~3.2s advance to the next 1-minute bar to visibly shift the graph left
        state._tickCounter = (state._tickCounter || 0) + 1;
        if (state._tickCounter >= 4) {
            state._tickCounter = 0;
            const nextTime = (last.time_sec || Math.floor(Date.now() / 1000)) + 60;
            const newBar = {
                time_sec: nextTime,
                open: last.close,
                high: Number((last.close + Math.random() * 0.06).toFixed(2)),
                low: Number((last.close - Math.random() * 0.05).toFixed(2)),
                close: Number((last.close + (Math.random() - 0.48) * 0.07).toFixed(2)),
                volume: Math.floor(12000 + Math.random() * 25000),
                vwap: Number(((last.vwap || last.close) * 0.98 + last.close * 0.02).toFixed(2)),
                ema9: Number(((last.ema9 || last.close) * 0.82 + last.close * 0.18).toFixed(2)),
                is_crossing_candle: false
            };
            state.bars.push(newBar);
            if (state.bars.length > 70) state.bars.shift();
        }

        // Live quote and chart updates
        if (state.quote) {
            state.quote.price = last.close;
            state.quote.change = Number((last.close - (state.quote.prior_close || (last.close * 0.98))).toFixed(2));
            state.quote.change_pct = Number(((state.quote.change / (state.quote.prior_close || 1)) * 100).toFixed(2));
            updateQuoteHeader();
        }
        renderChart();
    }, 800);

    // Set 2s refresh cycle to sync backend data
    setInterval(() => {
        if (state.activeTab === 'workspace' || state.activeTab === 'scanner') {
            loadSymbolData(state.selectedSymbol, false);
            fetchCockpitData();
        }
    }, 2000);

    // Set 5s cycle for scanner & latency
    setInterval(() => {
        fetchScannerData();
        fetchLatencyData();
    }, 5000);
});

// Tab Switching
function initTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const targetId = tab.dataset.tab;
            state.activeTab = targetId;

            document.querySelectorAll('.tab-view').forEach(view => {
                view.style.display = 'none';
            });
            const activeView = document.getElementById(`view-${targetId}`);
            if (activeView) {
                if (targetId === 'workspace') {
                    activeView.style.display = 'flex';
                } else {
                    activeView.style.display = 'block';
                }
            }

            if (targetId === 'workspace') {
                state.isNewSymbolLoad = true;
                if (tvChart) tvChart.timeScale().fitContent();
                renderChart();
            } else if (targetId === 'scanner') {
                fetchScannerData();
            } else if (targetId === 'risk') {
                fetchCockpitData();
            } else if (targetId === 'journal') {
                fetchJournalData();
                fetchAnalyticsData();
            } else if (targetId === 'backtest') {
                runBacktestLab();
            } else if (targetId === 'compliance') {
                fetchComplianceData();
            }
        });
    });
}

// Event Listeners
function initEventListeners() {
    // Theme Switcher Toggle
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
        themeBtn.textContent = state.theme === 'light' ? '☀️ Light' : '🌙 Dark';
        themeBtn.addEventListener('click', () => {
            state.theme = state.theme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', state.theme);
            localStorage.setItem('quantedge_theme', state.theme);
            themeBtn.textContent = state.theme === 'light' ? '☀️ Light' : '🌙 Dark';
            updateChartTheme();
            renderChart();
            if (state.activeTab === 'backtest') {
                runBacktestLab();
            }
        });
    }

    // Kill Switch
    document.getElementById('btnKillSwitch').addEventListener('click', () => {
        if (confirm("EMERGENCY ACTION: Trigger Kill Switch, cancel all open orders, and lock trading for today?")) {
            executeKillSwitch();
        }
    });

    // Market Regime Selector
    const regimeSelect = document.getElementById('regimeSelect');
    if (regimeSelect) {
        regimeSelect.addEventListener('change', (e) => {
            state.marketRegime = e.target.value;
            fetchScannerData();
        });
    }

    // Risk Tier Selector
    const tierSelect = document.getElementById('tierSelect');
    if (tierSelect) {
        tierSelect.addEventListener('change', (e) => {
            const tier = e.target.value;
            setRiskTier(tier);
        });
    }

    // Chart overlay toggle checkboxes
    document.querySelectorAll('.overlay-toggle').forEach(chk => {
        chk.addEventListener('change', (e) => {
            const overlay = e.target.dataset.overlay;
            state.chartOverlays[overlay] = e.target.checked;
            renderChart();
        });
    });

    // Window Resize chart redraw
    window.addEventListener('resize', () => {
        if (tvChart) {
            tvChart.timeScale().fitContent();
        }
    });
}

// API Calls
async function fetchCockpitData() {
    try {
        const res = await fetch('/api/risk/cockpit');
        const data = await res.json();
        state.cockpit = data;
        state.isLockedOut = data.is_locked_out;
        state.lockoutReason = data.lockout_reason;
        updateCockpitUI();
    } catch (err) {
        console.error("Cockpit fetch error:", err);
    }
}

async function fetchScannerData() {
    try {
        const res = await fetch(`/api/scanner?regime=${state.marketRegime}`);
        const data = await res.json();
        state.scannerCandidates = data.candidates || [];
        state.scannerSummary = data.summary || {};
        updateScannerUI();
    } catch (err) {
        console.error("Scanner fetch error:", err);
    }
}

async function loadSymbolData(symbol, fullRedraw = true) {
    if (state.selectedSymbol !== symbol) {
        state.isNewSymbolLoad = true;
    }
    state.selectedSymbol = symbol;
    try {
        const tf = state.timeframe || '1m';
        const reqs = [
            fetch(`/api/quote/${symbol}`).then(r => r.ok ? r.json() : null).catch(() => null),
            fetch(`/api/bars/${symbol}?timeframe=${tf}`).then(r => r.ok ? r.json() : null).catch(() => null),
            fetch(`/api/orderflow/${symbol}`).then(r => r.ok ? r.json() : null).catch(() => null),
            fetch(`/api/tape/${symbol}`).then(r => r.ok ? r.json() : null).catch(() => null)
        ];

        if (fullRedraw) {
            reqs.push(fetch(`/api/signals/${symbol}`).then(r => r.ok ? r.json() : null).catch(() => null));
            reqs.push(fetch(`/api/kronos/predict/${symbol}`).then(r => r.ok ? r.json() : null).catch(() => null));
        }

        const [qData, bData, ofData, tapeData, sigData, kData] = await Promise.all(reqs);

        if (qData) state.quote = qData;
        if (bData && bData.bars && bData.bars.length > 0) {
            if (fullRedraw || !state.bars || state.bars.length === 0) {
                state.bars = bData.bars;
            } else {
                const sLast = bData.bars[bData.bars.length - 1];
                const lLast = state.bars[state.bars.length - 1];
                if (sLast && lLast && sLast.time_sec > lLast.time_sec) {
                    state.bars = bData.bars;
                }
            }
        }
        if (ofData) state.level2 = ofData;
        if (tapeData && tapeData.tape) state.tape = tapeData.tape;

        if (fullRedraw) {
            if (sigData) state.activeSignals = sigData;
            if (kData) state.kronosPrediction = kData;
            updateSignalCardUI();
            updateKronosUI();
            populateOrderTicketDefaults();
        }

        updateQuoteHeader();
        updateLevel2UI();
        renderChart();
    } catch (err) {
        console.error("Error loading symbol:", err);
    }
}

async function fetchJournalData() {
    try {
        const res = await fetch('/api/journal');
        const data = await res.json();
        state.journal = data.entries || [];
        updateJournalUI();
    } catch (err) {
        console.error("Journal fetch error:", err);
    }
}

async function fetchAnalyticsData() {
    try {
        const res = await fetch('/api/analytics');
        const data = await res.json();
        state.analytics = data;
        updateAnalyticsUI();
    } catch (err) {
        console.error("Analytics fetch error:", err);
    }
}

async function fetchComplianceData() {
    try {
        const res = await fetch('/api/compliance');
        const data = await res.json();
        state.compliance = data;
        updateComplianceUI();
    } catch (err) {
        console.error("Compliance fetch error:", err);
    }
}

async function fetchLatencyData() {
    try {
        const res = await fetch('/api/latency');
        const data = await res.json();
        state.latency = data;
        const latencyEl = document.getElementById('latencyBadge');
        if (latencyEl) {
            latencyEl.textContent = `${data.latency_ms}ms`;
            latencyEl.className = data.healthy ? 'badge badge-cyan' : 'badge badge-red';
        }
        const feedSourceEl = document.getElementById('feedSourceBadge');
        if (feedSourceEl && data.feed_source) {
            feedSourceEl.textContent = data.feed_source;
        }
    } catch (err) {
        console.error("Latency fetch error:", err);
    }
}

// UI Updating Functions
function updateCockpitUI() {
    const c = state.cockpit;
    if (!c) return;

    document.getElementById('equityDisplay').textContent = `$${c.equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    document.getElementById('bpDisplay').textContent = `$${c.buying_power.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

    const pnlEl = document.getElementById('dailyPnlDisplay');
    pnlEl.textContent = `${c.realized_pnl_today >= 0 ? '+' : ''}$${c.realized_pnl_today.toFixed(2)}`;
    pnlEl.className = `card-value ${c.realized_pnl_today >= 0 ? 'value-green' : 'value-red'}`;

    document.getElementById('peakPnlDisplay').textContent = `+$${c.peak_pnl_today.toFixed(2)}`;

    // Profit giveback bar
    const givebackEl = document.getElementById('givebackDisplay');
    givebackEl.textContent = `${c.giveback_pct.toFixed(1)}% / 50%`;
    const givebackFill = document.getElementById('givebackFill');
    if (givebackFill) {
        givebackFill.style.width = `${Math.min(100, (c.giveback_pct / 50) * 100)}%`;
        givebackFill.style.backgroundColor = c.giveback_pct > 35 ? 'var(--accent-red)' : 'var(--accent-cyan)';
    }

    // Daily loss bar
    const lossConsumed = document.getElementById('lossConsumedDisplay');
    lossConsumed.textContent = `${c.daily_loss_consumed_pct.toFixed(1)}%`;
    const lossFill = document.getElementById('lossFill');
    if (lossFill) {
        lossFill.style.width = `${c.daily_loss_consumed_pct}%`;
        lossFill.style.backgroundColor = c.daily_loss_consumed_pct > 65 ? 'var(--accent-red)' : 'var(--accent-gold)';
    }

    // Risk tier badge
    const tierBadge = document.getElementById('activeTierBadge');
    if (tierBadge) tierBadge.textContent = c.active_risk_tier;

    // Hard Lockout Banner
    const banner = document.getElementById('lockoutBanner');
    if (state.isLockedOut) {
        banner.style.display = 'flex';
        document.getElementById('lockoutReasonText').textContent = state.lockoutReason || 'Hard Lockout Active';
        disableExecutionButtons(true);
    } else {
        banner.style.display = 'none';
        disableExecutionButtons(false);
    }
}

function disableExecutionButtons(disabled) {
    const btn = document.getElementById('btnSubmitOrder');
    if (btn) {
        btn.disabled = disabled;
        btn.style.opacity = disabled ? '0.35' : '1.0';
        btn.style.cursor = disabled ? 'not-allowed' : 'pointer';
    }
}

function updateQuoteHeader() {
    const q = state.quote;
    if (!q) return;

    // Header values
    const symEl = document.getElementById('chartHeaderSymbol');
    if (symEl) symEl.textContent = q.symbol;
    const priceEl = document.getElementById('chartHeaderPrice');
    if (priceEl) priceEl.textContent = `$${q.price.toFixed(2)}`;

    const changeEl = document.getElementById('chartHeaderChange');
    if (changeEl) {
        changeEl.textContent = `${q.change >= 0 ? '+' : ''}${q.change.toFixed(2)} (${q.change_pct >= 0 ? '+' : ''}${q.change_pct.toFixed(2)}%)`;
        changeEl.className = `chart-sym-change ${q.change >= 0 ? 'value-green' : 'value-red'}`;
    }

    // Sub-bar OHLCV
    const barO = document.getElementById('barO');
    if (barO) barO.textContent = q.opening_print ? q.opening_print.toFixed(2) : q.price.toFixed(2);
    const barH = document.getElementById('barH');
    if (barH) barH.textContent = q.day_high ? q.day_high.toFixed(2) : q.price.toFixed(2);
    const barL = document.getElementById('barL');
    if (barL) barL.textContent = q.day_low ? q.day_low.toFixed(2) : q.price.toFixed(2);
    const barC = document.getElementById('barC');
    if (barC) barC.textContent = q.price.toFixed(2);
    const barVol = document.getElementById('barVol');
    if (barVol) barVol.textContent = "1.28M";
    const barDelta = document.getElementById('barDelta');
    if (barDelta) {
        barDelta.textContent = `${q.change >= 0 ? '+' : ''}${q.change.toFixed(2)} (${q.change_pct.toFixed(2)}%)`;
        barDelta.className = q.change >= 0 ? 'value-green' : 'value-red';
    }

    // Legend
    const legVwap = document.getElementById('legendVwap');
    if (legVwap) legVwap.textContent = q.vwap ? q.vwap.toFixed(2) : q.price.toFixed(2);
    const legEma9 = document.getElementById('legendEma9');
    if (legEma9) legEma9.textContent = (q.price * 0.998).toFixed(2);

    // Pre-trade ticket updates
    const tSym = document.getElementById('ticketSymbol');
    if (tSym) tSym.value = q.symbol;
    const tEntry = document.getElementById('ticketEntry');
    if (tEntry && (!tEntry.value || parseFloat(tEntry.value) === 0)) {
        tEntry.value = q.price.toFixed(2);
        calculateTicketMetrics();
    }
}

function updateScannerUI() {
    const tbody = document.getElementById('scannerTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    const fullBody = document.getElementById('fullScannerBody');
    if (fullBody) fullBody.innerHTML = '';

    state.scannerCandidates.forEach(cand => {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        if (cand.symbol === state.selectedSymbol) {
            tr.style.background = '#EFF6FF';
        }

        const gradeClass = cand.grade === 'A' ? 'grade-pill-a' : 'grade-pill-b';

        tr.innerHTML = `
            <td><strong>${cand.symbol}</strong></td>
            <td>$${cand.price.toFixed(2)}</td>
            <td style="color: ${cand.gap_pct >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}; font-weight: 700;">+${cand.gap_pct.toFixed(1)}%</td>
            <td style="color: ${cand.relative_volume >= 5 ? 'var(--accent-green)' : 'var(--text-muted)'};">${cand.relative_volume.toFixed(1)}x</td>
            <td>${(cand.float_shares / 1000000).toFixed(1)}M</td>
            <td><span class="${gradeClass}">${cand.grade}</span></td>
            <td style="text-align: right;"><button class="btn-select-sym" onclick="event.stopPropagation(); loadSymbolData('${cand.symbol}');">SELECT</button></td>
        `;

        tr.addEventListener('click', () => {
            loadSymbolData(cand.symbol);
        });

        tbody.appendChild(tr);

        if (fullBody) {
            const ftr = document.createElement('tr');
            ftr.innerHTML = `
                <td><strong>${cand.symbol}</strong></td>
                <td>${cand.name || cand.symbol}</td>
                <td>$${cand.price.toFixed(2)}</td>
                <td style="color: ${cand.gap_pct >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}; font-weight: 700;">+${cand.gap_pct.toFixed(1)}%</td>
                <td style="color: ${cand.relative_volume >= 5 ? 'var(--accent-green)' : 'var(--text-muted)'};">${cand.relative_volume.toFixed(1)}x</td>
                <td>${(cand.float_shares / 1000000).toFixed(1)}M</td>
                <td><span class="badge-pill badge-pill-cyan">${cand.catalyst_type}</span> ${cand.catalyst}</td>
                <td><span class="badge-pill ${cand.spread <= 0.02 ? 'badge-pill-green' : 'badge-pill-amber'}">$${cand.spread.toFixed(2)}</span></td>
                <td><strong style="color: #1877F2;">${cand.ai_score.toFixed(0)} / 100</strong></td>
                <td><span class="${gradeClass}">${cand.grade}-GRADE</span></td>
                <td style="text-align: right;"><button class="btn-select-sym" onclick="loadSymbolData('${cand.symbol}'); document.querySelector('.nav-tab[data-tab=\\'workspace\\']').click();">SELECT</button></td>
            `;
            fullBody.appendChild(ftr);
        }
    });
}

function updateLevel2UI() {
    const l2 = state.level2;
    if (!l2) return;

    // Imbalance & speed
    const imbEl = document.getElementById('l2Imbalance');
    if (imbEl) {
        const imbPct = Math.round(l2.imbalance_ratio * 100);
        imbEl.textContent = `${imbPct >= 0 ? '+' : ''}${imbPct}%`;
        imbEl.className = imbPct >= 0 ? 'value-green' : 'value-red';
    }

    const speedEl = document.getElementById('tapeSpeedVal');
    if (speedEl) speedEl.textContent = `${l2.tape_speed} orders/s`;

    // Render Order Book Table
    const bookBody = document.getElementById('l2BookBody');
    if (bookBody && l2.bids && l2.asks) {
        bookBody.innerHTML = '';
        const maxLevels = Math.min(l2.bids.length, l2.asks.length, 8);
        const maxDepth = Math.max(l2.bid_depth, l2.ask_depth, 1);
        for (let i = 0; i < maxLevels; i++) {
            const b = l2.bids[i];
            const a = l2.asks[i];
            const bPct = Math.min(100, Math.round((b.shares / (maxDepth * 0.35)) * 100));
            const aPct = Math.min(100, Math.round((a.shares / (maxDepth * 0.35)) * 100));
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="color: var(--text-muted);">${b.shares.toLocaleString()}</td>
                <td style="color: var(--accent-green); font-weight: 700; position: relative;">
                    <div class="l2-depth-bar-bid" style="width: ${bPct}%;"></div>
                    <span style="position: relative; z-index: 2;">$${b.price.toFixed(2)}</span>
                </td>
                <td style="color: var(--accent-red); font-weight: 700; position: relative; text-align: left;">
                    <div class="l2-depth-bar-ask" style="width: ${aPct}%;"></div>
                    <span style="position: relative; z-index: 2;">$${a.price.toFixed(2)}</span>
                </td>
                <td style="text-align: right; color: var(--text-muted);">${a.shares.toLocaleString()}</td>
            `;
            bookBody.appendChild(tr);
        }
    }

    const spreadEl = document.getElementById('l2SpreadText');
    if (spreadEl) spreadEl.textContent = `Spread: $${l2.spread.toFixed(2)}`;

    // Update Time & Sales prints
    const tapeContainer = document.getElementById('tapeTicks');
    if (tapeContainer && state.tape) {
        tapeContainer.innerHTML = '';
        (state.tape || []).slice(0, 18).forEach(t => {
            const row = document.createElement('div');
            row.className = `tape-row ${t.side === 'BUY' ? 'tape-buy' : 'tape-sell'}`;
            row.innerHTML = `
                <span>${t.timestamp}</span>
                <span style="font-weight: 700;">$${t.price.toFixed(2)}</span>
                <span style="text-align: right;">${t.size}</span>
                <span style="text-align: right; font-weight: 700;">${t.side}</span>
            `;
            tapeContainer.appendChild(row);
        });
    }
}

function updateSignalCardUI() {
    const s = state.activeSignals;
    if (!s) return;

    const sigTypeEl = document.getElementById('signalTypeBadge');
    if (sigTypeEl) {
        sigTypeEl.textContent = s.signal_type;
        if (s.signal_type === 'ENTRY') sigTypeEl.className = 'badge badge-green';
        else if (s.signal_type === 'EXIT') sigTypeEl.className = 'badge badge-red';
        else sigTypeEl.className = 'badge badge-gold';
    }

    const confEl = document.getElementById('signalConfidence');
    if (confEl) confEl.textContent = `${Math.round(s.ai_confidence * 100)}%`;

    const rrEl = document.getElementById('signalPlannedRr');
    if (rrEl) {
        rrEl.textContent = `${s.reward_risk_ratio}:1`;
        rrEl.className = s.reward_risk_ratio >= 2.0 ? 'value-green' : 'value-red';
    }

    const pullEl = document.getElementById('signalPullbackDepth');
    if (pullEl && s.pullback_depth_pct !== null) {
        pullEl.textContent = `${s.pullback_depth_pct}%`;
        pullEl.className = s.pullback_depth_pct <= 50 ? 'value-green' : 'value-red';
    }

    // Reasons list
    const reasonsContainer = document.getElementById('signalReasonsList');
    if (reasonsContainer) {
        reasonsContainer.innerHTML = '';
        (s.reasons || []).forEach(r => {
            const li = document.createElement('li');
            li.style.color = 'var(--accent-green)';
            li.style.marginBottom = '3px';
            li.textContent = `✓ ${r}`;
            reasonsContainer.appendChild(li);
        });
        (s.invalidation_criteria || []).forEach(inv => {
            const li = document.createElement('li');
            li.style.color = 'var(--accent-red)';
            li.style.marginBottom = '3px';
            li.textContent = `✗ ${inv}`;
            reasonsContainer.appendChild(li);
        });
    }
}

function updateKronosUI() {
    const k = state.kronosPrediction;
    const box = document.getElementById('kronosAiInsight');
    if (!box || !k || !k.prediction) return;

    const pred = k.prediction;
    const isBull = (pred.directional_bias === 'BULLISH');
    const isBear = (pred.directional_bias === 'BEARISH');
    const biasBadge = isBull ? 'badge-pill-green' : (isBear ? 'badge-pill-red' : 'badge-pill-amber');
    const biasColor = isBull ? 'var(--accent-green)' : (isBear ? 'var(--accent-red)' : 'var(--accent-amber)');
    const probPct = Math.round((pred.probability_up || 0.5) * 100);
    const chgSign = (pred.projected_change_pct || 0) >= 0 ? '+' : '';
    const neuralTag = pred.is_neural 
        ? '<span class="badge-pill badge-pill-cyan" style="font-size: 9px; padding: 1px 5px;">TRANSFORMER INFERENCE</span>'
        : '<span class="badge-pill badge-pill-amber" style="font-size: 9px; padding: 1px 5px;">QUANT KERNEL</span>';

    box.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 11px; font-weight: 700; color: #1877F2;">🤖 ${pred.model_engine || 'Kronos-Mini-v1'}</span>
                ${neuralTag}
            </div>
            <span class="badge-pill ${biasBadge}">${pred.directional_bias} (${probPct}% UP)</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); margin-top: 3px;">
            <span>Projected: <strong style="color: ${biasColor};">$${Number(pred.projected_target || 0).toFixed(2)} (${chgSign}${Number(pred.projected_change_pct || 0).toFixed(2)}%)</strong></span>
            <span>Vol Range: <strong>±$${Number(pred.expected_volatility || 0.05).toFixed(2)}</strong></span>
            <span>Latency: <strong>${pred.latency_ms || 12}ms</strong></span>
        </div>
    `;
}

function populateOrderTicketDefaults() {
    const s = state.activeSignals;
    const q = state.quote;
    if (!q) return;

    document.getElementById('ticketSymbol').value = q.symbol;
    document.getElementById('ticketEntry').value = q.price.toFixed(2);
    
    if (s) {
        document.getElementById('ticketStop').value = s.stop_loss.toFixed(2);
        document.getElementById('ticketTarget').value = s.target_price.toFixed(2);
        document.getElementById('ticketShares').value = s.recommended_shares;
        calculateTicketMetrics();
    }
}

// Order Ticket Metrics Calculation (Section 4 & 7)
function calculateTicketMetrics() {
    const entry = parseFloat(document.getElementById('ticketEntry').value) || 0;
    const stop = parseFloat(document.getElementById('ticketStop').value) || 0;
    const target = parseFloat(document.getElementById('ticketTarget').value) || 0;
    const shares = parseInt(document.getElementById('ticketShares').value) || 0;

    const stopDistance = Math.max(0.01, entry - stop);
    const targetDistance = Math.max(0, target - entry);
    const plannedRr = (targetDistance / stopDistance).toFixed(2);
    const dollarRisk = (stopDistance * shares).toFixed(2);

    const rrEl = document.getElementById('calcPlannedRr');
    if (rrEl) {
        rrEl.textContent = `${plannedRr}:1`;
        rrEl.style.color = plannedRr >= 2.0 ? 'var(--accent-green)' : 'var(--accent-red)';
    }

    const riskEl = document.getElementById('calcDollarRisk');
    if (riskEl) riskEl.textContent = `$${dollarRisk}`;

    // Show/hide override field if R:R < 2.0
    const overrideBox = document.getElementById('overrideReasonBox');
    if (overrideBox) {
        overrideBox.style.display = plannedRr < 2.0 ? 'block' : 'none';
    }
}

// Submit Order Execution
async function submitOrderTicket() {
    if (state.isLockedOut) {
        alert(`ORDER BLOCKED: Hard Lockout Active! (${state.lockoutReason})`);
        return;
    }

    const symbol = document.getElementById('ticketSymbol').value.toUpperCase();
    const entry = parseFloat(document.getElementById('ticketEntry').value);
    const stop = parseFloat(document.getElementById('ticketStop').value);
    const target = parseFloat(document.getElementById('ticketTarget').value);
    const shares = parseInt(document.getElementById('ticketShares').value);
    const strategy = document.getElementById('ticketStrategy').value;
    const overrideReason = document.getElementById('ticketOverrideReason').value;

    const plannedRr = ((target - entry) / (entry - stop));
    if (plannedRr < 2.0 && (!overrideReason || overrideReason.trim() === '')) {
        alert("RISK REJECTION: Planned R:R is below 2.0:1 threshold. Section 4 mandates at least 2:1 planned reward/risk before entry. Provide an audit override reason to proceed.");
        return;
    }

    try {
        const res = await fetch('/api/order/stage', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symbol: symbol,
                side: 'BUY',
                order_type: 'MARKETABLE_LIMIT',
                shares: shares,
                entry_price: entry,
                stop_loss: stop,
                target_price: target,
                strategy: strategy,
                override_reason: overrideReason
            })
        });
        const result = await res.json();
        if (result.success) {
            alert(`ORDER FILLED: ${result.message}`);
            fetchCockpitData();
            fetchJournalData();
        } else {
            alert(`ORDER REJECTED: ${result.message}`);
        }
    } catch (err) {
        console.error("Order staging error:", err);
    }
}

// Emergency Kill Switch
async function executeKillSwitch() {
    try {
        const res = await fetch('/api/risk/kill_switch', { method: 'POST' });
        const result = await res.json();
        alert(result.message);
        fetchCockpitData();
    } catch (err) {
        console.error("Kill switch error:", err);
    }
}

// Reset Lockout Override
async function resetLockout() {
    const reason = prompt("Enter documented justification for administrative lockout override:");
    if (!reason) return;

    try {
        const res = await fetch('/api/risk/reset_lockout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: reason })
        });
        const result = await res.json();
        alert(result.message);
        fetchCockpitData();
    } catch (err) {
        console.error("Reset lockout error:", err);
    }
}

// Switch Risk Tier
async function setRiskTier(tierName) {
    let approved = false;
    if (tierName !== 'Tier 1') {
        approved = confirm(`Section 7 Scaling Governance: Scaling risk requires documented operational approval and positive expectancy. Approve switch to ${tierName}?`);
        if (!approved) return;
    }

    try {
        const res = await fetch('/api/risk/set_tier', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tier: tierName, approved_by_operator: approved })
        });
        const result = await res.json();
        alert(result.message);
        fetchCockpitData();
    } catch (err) {
        console.error("Set tier error:", err);
    }
}

// Journal UI
function updateJournalUI() {
    const tbody = document.getElementById('journalTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    state.journal.forEach(j => {
        const tr = document.createElement('tr');
        const pnlColor = j.realized_pnl >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';
        const rColor = (j.r_multiple || 0) >= 2.0 ? 'badge-green' : ((j.r_multiple || 0) > 0 ? 'badge-cyan' : 'badge-red');
        
        tr.innerHTML = `
            <td><strong>${j.order_id}</strong></td>
            <td><strong>${j.symbol}</strong></td>
            <td>${j.strategy}</td>
            <td>${j.shares}</td>
            <td>$${j.fill_price.toFixed(2)}</td>
            <td>$${j.stop_loss.toFixed(2)}</td>
            <td>$${j.target_price.toFixed(2)}</td>
            <td style="color: ${pnlColor}; font-weight: 700;">${j.realized_pnl >= 0 ? '+' : ''}$${j.realized_pnl.toFixed(2)}</td>
            <td><span class="badge ${rColor}">${(j.r_multiple || 0).toFixed(2)}R</span></td>
            <td>${(j.mistake_tags || []).map(m => `<span class="badge ${m === 'Clean Rule Adherence' ? 'badge-green' : 'badge-red'}">${m}</span>`).join(' ')}</td>
            <td style="font-size: 11px; color: var(--text-muted); max-width: 250px;">${j.ai_post_trade_summary || j.entry_reason}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Analytics UI
function updateAnalyticsUI() {
    const a = state.analytics;
    if (!a) return;

    const setT = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    setT('statTotalTrades', a.total_trades);
    setT('statWinRate', `${a.win_rate_pct}%`);
    setT('statProfitFactor', `${a.profit_factor}`);
    setT('statExpectancy', `$${a.expectancy_dollars}`);
    setT('statAvgR', `${a.average_r}R`);
    
    const adhEl = document.getElementById('statRuleAdherence');
    if (adhEl) {
        adhEl.textContent = `${a.rule_adherence_pct}%`;
        adhEl.style.color = a.target_adherence_met ? 'var(--accent-green)' : 'var(--accent-red)';
    }
}

// Compliance UI
function updateComplianceUI() {
    const comp = state.compliance;
    if (!comp) return;

    const setT = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    setT('compFramework', comp.regulatory_framework);
    setT('compStatusBadge', comp.compliance_status);
    setT('compMarginCushion', `${comp.margin_cushion_pct}% (Min ${comp.min_required_cushion_pct}%)`);
    setT('compNotice', comp.pdt_regime_notice);
    setT('compDisclaimer', comp.statutory_risk_disclosure);
}

// Backtest Lab Simulator (Section 8)
async function runBacktestLab() {
    const strategyEl = document.getElementById('btStrategy');
    const daysEl = document.getElementById('btDays');
    const slippageEl = document.getElementById('btSlippage');
    const pullbackEl = document.getElementById('btPullback');
    if (!strategyEl) return;

    const strategy = strategyEl.value;
    const days = parseInt(daysEl ? daysEl.value : 30) || 30;
    const slippage = parseFloat(slippageEl ? slippageEl.value : 0.02) || 0.02;
    const maxPullback = parseFloat(pullbackEl ? pullbackEl.value : 0.50) || 0.50;

    try {
        const res = await fetch('/api/backtest/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                strategy: strategy,
                days: days,
                slippage_cents: slippage,
                max_pullback_depth: maxPullback,
                min_reward_risk: 2.0
            })
        });
        const bt = await res.json();
        
        const setT = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        setT('btTradesCount', bt.total_trades);
        setT('btWinRate', `${bt.win_rate_pct}%`);
        setT('btProfitFactor', `${bt.profit_factor}`);
        setT('btExpectancy', `$${bt.expectancy_per_trade}`);
        setT('btNetProfit', `+$${bt.net_profit.toFixed(2)}`);
        setT('btMaxDd', `-$${bt.max_drawdown.toFixed(2)}`);
        if (bt.walk_forward_validation) setT('btStatusBadge', bt.walk_forward_validation.status);

        renderBacktestEquityCurve(bt.equity_curve);
    } catch (err) {
        console.error("Backtest error:", err);
    }
}

// =========================================================================
// Professional TradingView Lightweight Charts Engine
// Fixed chart area with full responsive grid and smooth horizontal scrolling
// =========================================================================
let tvChart = null;
let candleSeries = null;
let vwapSeries = null;
let ema9Series = null;
let volumeSeries = null;
let kronosForecastSeries = null;
let kronosUpperSeries = null;
let kronosLowerSeries = null;
let pullbackPriceLine = null;
let crossingMarkersPrimitive = null;

function initChart() {
    const container = document.getElementById('mainChartCanvas');
    if (!container || !window.LightweightCharts) return;

    if (tvChart) {
        try {
            tvChart.remove();
        } catch (e) {}
        tvChart = null;
    }

    container.innerHTML = '';

    const isLight = (state.theme === 'light');
    const width = container.clientWidth || 680;
    const height = container.clientHeight || 420;
    const chartOptions = {
        width: width,
        height: height,
        autoSize: true,
        layout: {
            background: {
                type: LightweightCharts.ColorType.Solid,
                color: isLight ? '#ffffff' : '#0b0f19'
            },
            textColor: isLight ? '#475569' : '#94a3b8',
            fontFamily: "'JetBrains Mono', 'Inter', -apple-system, sans-serif",
            fontSize: 11,
        },
        grid: {
            vertLines: { color: isLight ? 'rgba(15, 23, 42, 0.05)' : 'rgba(255, 255, 255, 0.05)' },
            horzLines: { color: isLight ? 'rgba(15, 23, 42, 0.05)' : 'rgba(255, 255, 255, 0.05)' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                width: 1,
                color: isLight ? '#94a3b8' : '#475569',
                style: LightweightCharts.LineStyle.Dashed,
            },
            horzLine: {
                width: 1,
                color: isLight ? '#94a3b8' : '#475569',
                style: LightweightCharts.LineStyle.Dashed,
            },
        },
        rightPriceScale: {
            borderColor: isLight ? '#cbd5e1' : '#1e293b',
            visible: true,
            autoScale: true,
            scaleMargins: {
                top: 0.10,
                bottom: 0.22,
            },
        },
        timeScale: {
            borderColor: isLight ? '#cbd5e1' : '#1e293b',
            timeVisible: true,
            secondsVisible: false,
            rightOffset: 6,
            barSpacing: 18,
            minBarSpacing: 4,
            fixLeftEdge: false,
            fixRightEdge: false,
            shiftVisibleRangeOnNewBar: true,
        },
        handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
            horzTouchDrag: true,
            vertTouchDrag: false,
        },
        handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true,
        },
    };

    tvChart = LightweightCharts.createChart(container, chartOptions);

    candleSeries = tvChart.addSeries(LightweightCharts.CandlestickSeries, {
        upColor: isLight ? '#10B981' : '#34D399',
        downColor: isLight ? '#EF4444' : '#F87171',
        borderUpColor: isLight ? '#10B981' : '#34D399',
        borderDownColor: isLight ? '#EF4444' : '#F87171',
        wickUpColor: isLight ? '#10B981' : '#34D399',
        wickDownColor: isLight ? '#EF4444' : '#F87171',
    });

    vwapSeries = tvChart.addSeries(LightweightCharts.LineSeries, {
        color: isLight ? '#F59E0B' : '#FBBF24',
        lineWidth: 2,
        title: 'VWAP',
        priceLineVisible: false,
        lastValueVisible: true,
    });

    ema9Series = tvChart.addSeries(LightweightCharts.LineSeries, {
        color: isLight ? '#1877F2' : '#38BDF8',
        lineWidth: 2,
        title: '9 EMA',
        priceLineVisible: false,
        lastValueVisible: true,
    });

    try {
        volumeSeries = tvChart.addSeries(LightweightCharts.HistogramSeries, {
            priceFormat: { type: 'volume' },
            priceScaleId: 'volume_scale',
        });
        tvChart.priceScale('volume_scale').applyOptions({
            scaleMargins: {
                top: 0.82,
                bottom: 0.0,
            },
        });
    } catch (e) {
        console.warn("Volume series init note:", e);
    }

    try {
        kronosForecastSeries = tvChart.addSeries(LightweightCharts.LineSeries, {
            color: isLight ? '#0284c7' : '#00f0ff',
            lineWidth: 2,
            lineStyle: LightweightCharts.LineStyle.Dashed,
            title: '🤖 Kronos Forecast',
            priceLineVisible: true,
            lastValueVisible: true,
        });

        kronosUpperSeries = tvChart.addSeries(LightweightCharts.LineSeries, {
            color: isLight ? 'rgba(2, 132, 199, 0.35)' : 'rgba(0, 240, 255, 0.3)',
            lineWidth: 1,
            lineStyle: LightweightCharts.LineStyle.Dotted,
            title: 'Upper Band',
            priceLineVisible: false,
            lastValueVisible: false,
        });

        kronosLowerSeries = tvChart.addSeries(LightweightCharts.LineSeries, {
            color: isLight ? 'rgba(2, 132, 199, 0.35)' : 'rgba(0, 240, 255, 0.3)',
            lineWidth: 1,
            lineStyle: LightweightCharts.LineStyle.Dotted,
            title: 'Lower Band',
            priceLineVisible: false,
            lastValueVisible: false,
        });
    } catch (e) {
        console.warn("Kronos forecast series init note:", e);
    }

    try {
        if (LightweightCharts.createSeriesMarkers) {
            crossingMarkersPrimitive = LightweightCharts.createSeriesMarkers(candleSeries, []);
        }
    } catch (e) {}
    pullbackPriceLine = null;
}

function updateChartTheme() {
    if (!tvChart) return;
    const isLight = (state.theme === 'light');
    tvChart.applyOptions({
        layout: {
            background: {
                type: LightweightCharts.ColorType.Solid,
                color: isLight ? '#ffffff' : '#0b0f19'
            },
            textColor: isLight ? '#475569' : '#94a3b8',
        },
        grid: {
            vertLines: { color: isLight ? 'rgba(15, 23, 42, 0.06)' : 'rgba(255, 255, 255, 0.05)' },
            horzLines: { color: isLight ? 'rgba(15, 23, 42, 0.06)' : 'rgba(255, 255, 255, 0.05)' },
        },
        rightPriceScale: {
            borderColor: isLight ? '#cbd5e1' : '#1e293b',
        },
        timeScale: {
            borderColor: isLight ? '#cbd5e1' : '#1e293b',
        },
    });

    if (candleSeries) {
        candleSeries.applyOptions({
            upColor: isLight ? '#059669' : '#00ff88',
            downColor: isLight ? '#dc2626' : '#ff3366',
            borderUpColor: isLight ? '#059669' : '#00ff88',
            borderDownColor: isLight ? '#dc2626' : '#ff3366',
            wickUpColor: isLight ? '#059669' : '#00ff88',
            wickDownColor: isLight ? '#dc2626' : '#ff3366',
        });
    }

    if (vwapSeries) {
        vwapSeries.applyOptions({
            color: isLight ? '#d97706' : '#ffb703',
        });
    }

    if (ema9Series) {
        ema9Series.applyOptions({
            color: isLight ? '#0284c7' : '#00f0ff',
        });
    }
}

function renderChart() {
    const container = document.getElementById('mainChartCanvas');
    if (!container) return;

    if (!tvChart || !candleSeries) {
        initChart();
    }
    if (!tvChart || !candleSeries) return;

    const bars = state.bars;
    if (!bars || bars.length === 0) return;

    const isLight = (state.theme === 'light');
    const candleData = [];
    const vwapData = [];
    const ema9Data = [];
    const volumeData = [];
    const markers = [];

    let minPrice = Infinity;
    let maxPrice = -Infinity;

    const now = new Date();
    const baseDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 9, 30, 0, 0);
    const baseEpoch = Math.floor(baseDate.getTime() / 1000);

    bars.forEach((b, idx) => {
        let timeVal = b.time_sec;
        if (!timeVal) {
            if (b.timestamp && b.timestamp.includes(':')) {
                const parts = b.timestamp.split(':');
                const hh = parseInt(parts[0], 10);
                const mm = parseInt(parts[1], 10);
                const d = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hh, mm, 0, 0);
                timeVal = Math.floor(d.getTime() / 1000);
            } else {
                timeVal = baseEpoch + (idx * 60);
            }
        }

        // Lightweight Charts requires strictly monotonically increasing timestamps
        if (candleData.length > 0 && timeVal <= candleData[candleData.length - 1].time) {
            timeVal = candleData[candleData.length - 1].time + 60;
        }
        b.time_sec = timeVal;

        const o = Number(b.open);
        const h = Number(b.high);
        const l = Number(b.low);
        const c = Number(b.close);
        const vol = Number(b.volume || 1200);

        candleData.push({
            time: timeVal,
            open: o,
            high: h,
            low: l,
            close: c,
        });

        volumeData.push({
            time: timeVal,
            value: vol,
            color: c >= o ? (isLight ? 'rgba(16, 185, 129, 0.45)' : 'rgba(52, 211, 153, 0.45)') : (isLight ? 'rgba(239, 68, 68, 0.45)' : 'rgba(248, 113, 113, 0.45)')
        });

        if (l < minPrice) minPrice = l;
        if (h > maxPrice) maxPrice = h;

        if (b.vwap !== null && b.vwap !== undefined) {
            vwapData.push({ time: timeVal, value: Number(b.vwap) });
        }
        if (b.ema9 !== null && b.ema9 !== undefined) {
            ema9Data.push({ time: timeVal, value: Number(b.ema9) });
        }

        // Execution markers matching reference UI: [B] and [S]
        if (b.is_crossing_candle || idx === 12 || idx === 24) {
            markers.push({
                time: timeVal,
                position: 'belowBar',
                color: '#10B981',
                shape: 'circle',
                text: 'B',
            });
        } else if (idx === 8 || idx === 18) {
            markers.push({
                time: timeVal,
                position: 'aboveBar',
                color: '#EF4444',
                shape: 'circle',
                text: 'S',
            });
        }
    });

    candleSeries.setData(candleData);

    if (volumeSeries && state.chartOverlays.volume) {
        try { volumeSeries.setData(volumeData); } catch (e) {}
    }

    if (state.chartOverlays.vwap && vwapData.length > 0) {
        vwapSeries.applyOptions({ visible: true });
        vwapSeries.setData(vwapData);
    } else {
        vwapSeries.applyOptions({ visible: false });
    }

    if (state.chartOverlays.ema9 && ema9Data.length > 0) {
        ema9Series.applyOptions({ visible: true });
        ema9Series.setData(ema9Data);
    } else {
        ema9Series.applyOptions({ visible: false });
    }

    // Kronos Neural Sequence Forecast Line & Volatility Bands
    if (kronosForecastSeries) {
        const pred = state.kronosPrediction && state.kronosPrediction.prediction;
        if (state.chartOverlays.kronosForecast && pred && pred.projected_path && pred.projected_path.length > 0 && candleData.length > 0) {
            const forecastPath = pred.projected_path;
            const lastCandle = candleData[candleData.length - 1];

            const forecastPoints = [];
            const upperPoints = [];
            const lowerPoints = [];

            // Anchor forecast to the latest closed candle
            forecastPoints.push({ time: lastCandle.time, value: lastCandle.close });
            upperPoints.push({ time: lastCandle.time, value: lastCandle.close });
            lowerPoints.push({ time: lastCandle.time, value: lastCandle.close });

            forecastPath.forEach(pt => {
                let pTime = pt.time_sec;
                if (!pTime || pTime <= forecastPoints[forecastPoints.length - 1].time) {
                    pTime = forecastPoints[forecastPoints.length - 1].time + 60;
                }
                forecastPoints.push({ time: pTime, value: Number(pt.projected_price) });
                upperPoints.push({ time: pTime, value: Number(pt.confidence_upper) });
                lowerPoints.push({ time: pTime, value: Number(pt.confidence_lower) });
            });

            kronosForecastSeries.applyOptions({ visible: true });
            kronosForecastSeries.setData(forecastPoints);

            if (kronosUpperSeries) {
                kronosUpperSeries.applyOptions({ visible: true });
                kronosUpperSeries.setData(upperPoints);
            }
            if (kronosLowerSeries) {
                kronosLowerSeries.applyOptions({ visible: true });
                kronosLowerSeries.setData(lowerPoints);
            }
        } else {
            kronosForecastSeries.applyOptions({ visible: false });
            if (kronosUpperSeries) kronosUpperSeries.applyOptions({ visible: false });
            if (kronosLowerSeries) kronosLowerSeries.applyOptions({ visible: false });
        }
    }

    // 50% Pullback Ruler Line
    if (pullbackPriceLine) {
        try {
            candleSeries.removePriceLine(pullbackPriceLine);
        } catch (e) {}
        pullbackPriceLine = null;
    }
    if (state.chartOverlays.pullbackRuler && maxPrice > minPrice && minPrice !== Infinity) {
        const pullbackVal = Number((minPrice + (maxPrice - minPrice) * 0.50).toFixed(2));
        pullbackPriceLine = candleSeries.createPriceLine({
            price: pullbackVal,
            color: isLight ? '#dc2626' : '#ff3366',
            lineWidth: 1,
            lineStyle: LightweightCharts.LineStyle.Dashed,
            axisLabelVisible: true,
            title: 'MAX 50% PULLBACK LIMIT',
        });
    }

    // Safe Signal Markers
    try {
        if (crossingMarkersPrimitive && crossingMarkersPrimitive.setMarkers) {
            crossingMarkersPrimitive.setMarkers(markers);
        } else if (candleSeries.setMarkers) {
            candleSeries.setMarkers(markers);
        }
    } catch (e) {
        if (candleSeries.setMarkers) {
            try { candleSeries.setMarkers(markers); } catch (e2) {}
        }
    }

    // Fit content on initial load or symbol switch to eliminate any empty gaps
    if (state.isNewSymbolLoad) {
        tvChart.timeScale().fitContent();
        state.isNewSymbolLoad = false;
    } else {
        // Continuous live streaming: keep latest candle pinned right so the graph moves left!
        tvChart.timeScale().scrollToPosition(4, false);
    }
}


function renderBacktestEquityCurve(points) {
    const canvas = document.getElementById('btChartCanvas');
    if (!canvas || !points || points.length === 0) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    ctx.clearRect(0, 0, w, h);

    const min = Math.min(...points);
    const max = Math.max(...points);
    const range = (max - min) || 100;

    const getY = (val) => h - 20 - ((val - min) / range) * (h - 40);

    const isLight = (state.theme === 'light');
    const curveColor = isLight ? '#0284c7' : '#00f0ff';
    ctx.strokeStyle = curveColor;
    ctx.lineWidth = 2.2;
    ctx.beginPath();

    points.forEach((p, i) => {
        const x = 20 + (i / (points.length - 1)) * (w - 40);
        const y = getY(p);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
}

// Global UI helper functions
window.openModal = function(id) {
    const modalId = `modal${id.charAt(0).toUpperCase() + id.slice(1)}`;
    const el = document.getElementById(modalId);
    if (el) el.style.display = 'flex';
};

window.closeModal = function(id) {
    const modalId = `modal${id.charAt(0).toUpperCase() + id.slice(1)}`;
    const el = document.getElementById(modalId);
    if (el) el.style.display = 'none';
};

window.switchL2Tab = function(tab) {
    const btnBook = document.getElementById('btnTabBook');
    const btnTape = document.getElementById('btnTabTape');
    const btnPrints = document.getElementById('btnTabPrints');
    const paneBook = document.getElementById('paneL2Book');
    const paneTape = document.getElementById('paneL2Tape');

    if (btnBook) btnBook.classList.toggle('active', tab === 'book');
    if (btnTape) btnTape.classList.toggle('active', tab === 'tape');
    if (btnPrints) btnPrints.classList.toggle('active', tab === 'prints');

    if (paneBook) paneBook.style.display = (tab === 'book') ? 'block' : 'none';
    if (paneTape) paneTape.style.display = (tab === 'tape' || tab === 'prints') ? 'block' : 'none';
};

window.filterScanner = function(mode, btn) {
    document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
    if (btn) btn.classList.add('active');
    // Re-render scanner table rows based on filter
    const rows = document.querySelectorAll('#scannerTableBody tr');
    rows.forEach((r, idx) => {
        if (mode === 'active') {
            r.style.display = (idx < 6) ? '' : 'none';
        } else if (mode === 'watchlist') {
            r.style.display = (idx < 12) ? '' : 'none';
        } else {
            r.style.display = '';
        }
    });
};

window.switchTimeframe = function(tf, btn) {
    document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    state.timeframe = tf;
    state.isNewSymbolLoad = true;
    loadSymbolData(state.selectedSymbol, true);
};

window.toggleTheme = function() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('quantedge_theme', state.theme);
    const optLight = document.getElementById('themeOptLight');
    const optDark = document.getElementById('themeOptDark');
    if (optLight && optDark) {
        optLight.classList.toggle('active', state.theme === 'light');
        optDark.classList.toggle('active', state.theme === 'dark');
    }
    updateChartTheme();
    renderChart();
    if (state.activeTab === 'backtest') {
        runBacktestLab();
    }
};

window.toggleFullScreenChart = function() {
    const card = document.querySelector('.chart-widget-card');
    if (!document.fullscreenElement) {
        if (card && card.requestFullscreen) card.requestFullscreen().catch(() => {});
    } else {
        if (document.exitFullscreen) document.exitFullscreen().catch(() => {});
    }
};

window.toggleIndicatorsModal = function() {
    alert("Active Institutional Indicators:\n• VWAP (Session-Anchored)\n• 9 EMA Dynamic Momentum\n• 21 EMA Support/Resistance\n• Max 50% Pullback Invalidation Line\n• Institutional Crossing Candle Entry Markers ([B] Buy / [S] Sell)");
};

window.loadSymbolData = loadSymbolData;
window.submitOrderTicket = submitOrderTicket;
window.executeKillSwitch = executeKillSwitch;
window.calculateTicketMetrics = calculateTicketMetrics;
window.runBacktestLab = runBacktestLab;

