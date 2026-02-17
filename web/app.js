const state = {
  data: null,
  history: null,
  backtestHistory: null,
  model: "LSTM",
  symbol: null,
  chart: null,
  timeframeDays: 60,
  theme: localStorage.getItem('theme') || 'dark',
  favorites: JSON.parse(localStorage.getItem('favorites') || '[]'),
  allSymbols: [],
  autoRefreshInterval: null,
};

const elements = {
  select: document.getElementById("symbol-select"),
  toggles: document.querySelectorAll(".toggle"),
  timeframeBtns: document.querySelectorAll(".timeframe-btn"),
  themeToggle: document.getElementById("theme-toggle"),
  stockSearch: document.getElementById("stock-search"),
  favoriteBtn: document.getElementById("favorite-btn"),
  favoritesList: document.getElementById("favorites-list"),
  refreshBtn: document.getElementById("refresh-btn"),
  exportBtn: document.getElementById("export-btn"),
  autoRefreshCheckbox: document.getElementById("auto-refresh"),
  totalStocks: document.getElementById("total-stocks"),
  bullishCount: document.getElementById("bullish-count"),
  bearishCount: document.getElementById("bearish-count"),
  marketStatus: document.getElementById("market-status"),
  marketTime: document.getElementById("market-time"),
  avgAccuracy: document.getElementById("avg-accuracy"),
  topGainer: document.getElementById("top-gainer"),
  topGainerChange: document.getElementById("top-gainer-change"),
  topLoser: document.getElementById("top-loser"),
  topLoserChange: document.getElementById("top-loser-change"),
  topGainersList: document.getElementById("top-gainers-list"),
  topLosersList: document.getElementById("top-losers-list"),
  predOpen: document.getElementById("pred-open"),
  predHigh: document.getElementById("pred-high"),
  predLow: document.getElementById("pred-low"),
  predClose: document.getElementById("pred-close"),
  predClose2: document.getElementById("pred-close-2"),
  predChange: document.getElementById("pred-change"),
  predDate: document.getElementById("pred-date"),
  predModel: document.getElementById("pred-model"),
  signalText: document.getElementById("signal-text"),
  signalDesc: document.getElementById("signal-desc"),
  signalBadge: document.getElementById("signal-badge"),
  signalIcon: document.getElementById("signal-icon"),
  trendIndicator: document.getElementById("trend-indicator"),
  chartCanvas: document.getElementById("price-chart"),
  chartTitle: document.getElementById("chart-title"),
  chartSubtitle: document.getElementById("chart-subtitle"),
  chartStatus: document.getElementById("chart-status"),
  chartLoader: document.getElementById("chart-loader"),
  modelAccuracy: document.getElementById("model-accuracy"),
  modelMae: document.getElementById("model-mae"),
  modelConfidence: document.getElementById("model-confidence"),
  updatedTime: document.getElementById("updated-time"),
  dataStatus: document.getElementById("data-status"),
  lastUpdated: document.getElementById("last-updated"),
};

function formatValue(value) {
  if (value === null || Number.isNaN(value)) {
    return "--";
  }
  return value.toFixed(2);
}

function formatPct(value) {
  if (value === null || Number.isNaN(value)) {
    return "--";
  }
  return `${value.toFixed(2)}%`;
}

function getSignal(changePct) {
  if (changePct === null || Number.isNaN(changePct)) {
    return { text: "No signal", desc: "Prediction data unavailable.", type: "neutral" };
  }
  if (changePct > 0.2) {
    return { text: "Bullish", desc: "Strong upward movement expected.", type: "bullish" };
  }
  if (changePct < -0.2) {
    return { text: "Bearish", desc: "Downward movement expected.", type: "bearish" };
  }
  return { text: "Neutral", desc: "Sideways movement expected.", type: "neutral" };
}

function updateUI() {
  if (!state.data || !state.symbol) {
    return;
  }

  const item = getPredictionItem(state.model, state.symbol);

  if (!item) {
    elements.predOpen.textContent = "--";
    elements.predHigh.textContent = "--";
    elements.predLow.textContent = "--";
    elements.predClose.textContent = "--";
    elements.predClose2.textContent = "--";
    elements.predChange.textContent = "--";
    elements.predDate.textContent = "--";
    elements.predModel.textContent = `${state.model} model`;
    elements.signalText.textContent = "No data";
    elements.signalDesc.textContent = "No prediction found for this stock.";
    elements.signalBadge.className = "signal-badge";
    elements.trendIndicator.textContent = "";
    
    // Update global stats even when current stock has no data
    updateQuickStats();
    updateMarketOverview();
    updateTopStocks();
    return;
  }

  const changePct = item.change_pct;
  const signal = getSignal(changePct);

  // Update prediction values
  elements.predOpen.textContent = formatValue(item.predicted_open);
  elements.predHigh.textContent = formatValue(item.predicted_high);
  elements.predLow.textContent = formatValue(item.predicted_low);
  elements.predClose.textContent = formatValue(item.predicted_close);
  elements.predClose2.textContent = formatValue(item.predicted_close);
  elements.predChange.textContent = `Change: ${formatValue(item.change)} (${formatPct(changePct)})`;
  
  // Update date
  const forecastDate = item.date ? new Date(item.date + "T00:00:00") : null;
  if (forecastDate && !Number.isNaN(forecastDate.getTime())) {
    forecastDate.setDate(forecastDate.getDate() + 1);
    elements.predDate.textContent = forecastDate.toISOString().slice(0, 10);
  } else {
    elements.predDate.textContent = item.date || "--";
  }
  elements.predModel.textContent = `${state.model} model`;
  
  // Update signal with visual indicators
  elements.signalText.textContent = signal.text;
  elements.signalDesc.textContent = signal.desc;
  elements.signalBadge.className = `signal-badge ${signal.type}`;
  
  // Update trend indicator
  if (changePct > 0) {
    elements.trendIndicator.textContent = "\u2191";
    elements.trendIndicator.className = "trend-indicator up";
  } else if (changePct < 0) {
    elements.trendIndicator.textContent = "\u2193";
    elements.trendIndicator.className = "trend-indicator down";
  } else {
    elements.trendIndicator.textContent = "";
    elements.trendIndicator.className = "trend-indicator";
  }
  
  // Update performance metrics
  updatePerformanceMetrics(item);
  
  // Update model button badges to show recommended model
  updateModelBadges(item);
  
  // Update quick stats and overview
  updateQuickStats();
  updateMarketOverview();
  updateTopStocks();

  updateChart(item);
}

function getPredictionItem(model, symbol) {
  if (!state.data) {
    return null;
  }

  if (state.data.models && state.data.models[model]) {
    return state.data.models[model][symbol] || null;
  }

  if (state.data.stocks && state.data.stocks[symbol]) {
    const stock = state.data.stocks[symbol];
    const prediction = stock.predictions ? stock.predictions[model] : null;
    if (!prediction) {
      return null;
    }

    const predictedClose = prediction.close;
    const todayClose = stock.today_close;
    const change = (predictedClose !== null && todayClose !== null)
      ? predictedClose - todayClose
      : null;
    const changePct = (change !== null && todayClose)
      ? (change / todayClose) * 100
      : null;

    return {
      date: stock.date,
      today_close: todayClose,
      predicted_open: prediction.open,
      predicted_high: prediction.high,
      predicted_low: prediction.low,
      predicted_close: predictedClose,
      change: change,
      change_pct: changePct,
      recommended_model: stock.recommended_model,
      lstm_mae: stock.lstm_mae,
      xgboost_mae: stock.xgboost_mae,
    };
  }

  return null;
}

function getHistoryForSymbol(symbol) {
  if (state.backtestHistory && state.backtestHistory.symbols && state.backtestHistory.symbols[symbol]) {
    return { data: state.backtestHistory.symbols[symbol], source: "backtest" };
  }
  if (!state.history || !state.history.symbols) {
    return null;
  }
  if (!state.history.symbols[symbol]) {
    return null;
  }
  return { data: state.history.symbols[symbol], source: "history" };
}

function normalizeSeries(series, length) {
  if (!Array.isArray(series)) {
    return new Array(length).fill(null);
  }
  const normalized = series.slice(0, length);
  while (normalized.length < length) {
    normalized.push(null);
  }
  return normalized;
}

function updateChart(item) {
  const historyPayload = getHistoryForSymbol(state.symbol);
  const history = historyPayload ? historyPayload.data : null;
  
  if (!history || !history.dates || !history.close || history.close.length === 0) {
    elements.chartTitle.textContent = `${state.symbol} price`;
    elements.chartSubtitle.textContent = `${state.model} trend`;
    elements.chartStatus.textContent = "History data not available yet.";
    if (state.chart) {
      state.chart.destroy();
      state.chart = null;
    }
    return;
  }

  // Show loader
  elements.chartLoader.classList.add('active');
  
  // Apply timeframe filter
  const allLabels = history.dates.slice();
  const allActual = history.close.slice();
  const allPredicted = history.predicted ? history.predicted[state.model] : null;
  
  const startIndex = Math.max(0, allLabels.length - state.timeframeDays);
  const labels = allLabels.slice(startIndex);
  const actualSeries = normalizeSeries(allActual.slice(startIndex), labels.length);
  const predictedHistory = allPredicted ? allPredicted.slice(startIndex) : null;
  const predictedSeries = normalizeSeries(predictedHistory, labels.length);
  const hasPredictedHistory = predictedSeries.some((value) => value !== null);

  const sourceLabel = historyPayload && historyPayload.source === "backtest"
    ? "Backtest"
    : "Historical";
  elements.chartTitle.textContent = `${state.symbol} Close Price`;
  elements.chartSubtitle.textContent = `${sourceLabel} (${state.timeframeDays}D)`;
  
  if (!predictedHistory) {
    elements.chartStatus.textContent = "Predicted history not available yet.";
  } else if (!hasPredictedHistory) {
    elements.chartStatus.textContent = "No predicted history for this model.";
  } else {
    elements.chartStatus.textContent = "";
  }

  const config = {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Actual Close",
          data: actualSeries,
          borderColor: state.theme === 'dark' ? "#4ee0c7" : "#20c997",
          backgroundColor: state.theme === 'dark' ? "rgba(78, 224, 199, 0.15)" : "rgba(32, 201, 151, 0.15)",
          borderWidth: 2.5,
          pointRadius: 0,
          pointHoverRadius: 6,
          tension: 0.3,
          fill: true,
        },
        {
          label: `${state.model} Predicted`,
          data: predictedSeries,
          borderColor: state.theme === 'dark' ? "#f4a340" : "#fd7e14",
          backgroundColor: state.theme === 'dark' ? "rgba(244, 163, 64, 0.15)" : "rgba(253, 126, 20, 0.15)",
          borderWidth: 2.5,
          pointRadius: 2,
          pointHoverRadius: 6,
          borderDash: [6, 4],
          tension: 0.25,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          labels: {
            color: state.theme === 'dark' ? "#f4f2ec" : "#212529",
            usePointStyle: true,
            pointStyle: "circle",
            padding: 15,
            font: {
              size: 12,
              weight: '500'
            }
          },
        },
        tooltip: {
          mode: "index",
          intersect: false,
          backgroundColor: state.theme === 'dark' ? 'rgba(25, 43, 41, 0.95)' : 'rgba(255, 255, 255, 0.95)',
          titleColor: state.theme === 'dark' ? '#4ee0c7' : '#20c997',
          bodyColor: state.theme === 'dark' ? '#f4f2ec' : '#212529',
          borderColor: state.theme === 'dark' ? '#4ee0c7' : '#20c997',
          borderWidth: 1,
          padding: 12,
          displayColors: true,
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) {
                label += ': Rs ';
              }
              if (context.parsed.y !== null) {
                label += context.parsed.y.toFixed(2);
              }
              return label;
            }
          }
        },
      },
      scales: {
        x: {
          ticks: {
            color: state.theme === 'dark' ? "#b4b3ad" : "#6c757d",
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 8,
          },
          grid: {
            color: state.theme === 'dark' ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)",
            drawBorder: false,
          },
        },
        y: {
          ticks: {
            color: state.theme === 'dark' ? "#b4b3ad" : "#6c757d",
            callback: function(value) {
              return 'Rs ' + value.toFixed(0);
            }
          },
          grid: {
            color: state.theme === 'dark' ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)",
            drawBorder: false,
          },
        },
      },
      animation: {
        duration: 750,
        easing: 'easeInOutQuart',
      },
    },
  };

  setTimeout(() => {
    if (state.chart) {
      // Update dataset labels explicitly to ensure legend updates
      state.chart.data.labels = config.data.labels;
      state.chart.data.datasets[0].data = config.data.datasets[0].data;
      state.chart.data.datasets[0].label = config.data.datasets[0].label;
      state.chart.data.datasets[1].data = config.data.datasets[1].data;
      state.chart.data.datasets[1].label = config.data.datasets[1].label;
      state.chart.options = config.options;
      state.chart.update('active');
    } else if (elements.chartCanvas) {
      state.chart = new Chart(elements.chartCanvas, config);
    }
    elements.chartLoader.classList.remove('active');
  }, 300);
}

function updateModelBadges(item) {
  const recommended = item.recommended_model;
  const lstmMae = item.lstm_mae;
  const xgboostMae = item.xgboost_mae;
  
  elements.toggles.forEach((btn) => {
    const modelName = btn.dataset.model;
    
    // Remove existing badges
    const existingBadge = btn.querySelector('.recommend-badge');
    if (existingBadge) {
      existingBadge.remove();
    }
    
    // Add badge to recommended model (not for Ensemble)
    if (recommended && modelName === recommended && modelName !== 'Ensemble') {
      const badge = document.createElement('span');
      badge.className = 'recommend-badge';
      badge.textContent = ' \u2b50';
      
      // Add tooltip with accuracy info
      let title = `Best for ${state.symbol}`;
      if (lstmMae !== null && xgboostMae !== null) {
        const mae = modelName === 'LSTM' ? lstmMae : xgboostMae;
        title += ` (MAE: \u00b1${mae.toFixed(2)} Rs)`;
      }
      badge.title = title;
      btn.appendChild(badge);
    }
  });
}

function updatePerformanceMetrics(item) {
  const mae = state.model === 'LSTM' ? item.lstm_mae : item.xgboost_mae;
  
  // Calculate accuracy based on MAE (lower MAE = higher accuracy)
  let accuracy = "--";
  if (mae !== null && item.today_close) {
    const accuracyPct = Math.max(0, Math.min(100, 100 - (mae / item.today_close * 100)));
    accuracy = accuracyPct.toFixed(1) + "%";
  }
  
  // Calculate confidence (inverse of MAE percentage)
  let confidence = "--";
  if (mae !== null && item.today_close) {
    const errorPct = (mae / item.today_close * 100);
    if (errorPct < 2) confidence = "High";
    else if (errorPct < 5) confidence = "Medium";
    else confidence = "Low";
  }
  
  elements.modelAccuracy.textContent = accuracy;
  elements.modelMae.textContent = mae !== null ? `\u00b1Rs ${mae.toFixed(2)}` : "--";
  elements.modelConfidence.textContent = confidence;
  
  // Update timestamp
  if (item.date) {
    const date = new Date(item.date);
    elements.updatedTime.textContent = `Updated: ${date.toLocaleDateString()}`;
  }
}

function setModel(model) {
  state.model = model;
  elements.toggles.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.model === model);
  });
  updateUI();
  updateMarketOverview();
  updateTopStocks();
}

function setSymbol(symbol) {
  state.symbol = symbol;
  if (elements.select) {
    elements.select.value = symbol;
  }
  updateFavoriteButton();
  updateUI();
}

function filterStocks(searchTerm) {
  const filtered = state.allSymbols.filter(symbol => 
    symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  elements.select.innerHTML = "";
  filtered.forEach((symbol) => {
    const option = document.createElement("option");
    option.value = symbol;
    option.textContent = symbol;
    elements.select.appendChild(option);
  });
  
  if (filtered.length > 0 && !filtered.includes(state.symbol)) {
    setSymbol(filtered[0]);
  }
}

function toggleFavorite() {
  if (!state.symbol) return;
  
  const index = state.favorites.indexOf(state.symbol);
  if (index > -1) {
    state.favorites.splice(index, 1);
  } else {
    state.favorites.push(state.symbol);
  }
  
  localStorage.setItem('favorites', JSON.stringify(state.favorites));
  updateFavoriteButton();
  renderFavorites();
}

function updateFavoriteButton() {
  if (!elements.favoriteBtn || !state.symbol) return;
  
  const isFavorite = state.favorites.includes(state.symbol);
  elements.favoriteBtn.classList.toggle('active', isFavorite);
  elements.favoriteBtn.title = isFavorite ? 'Remove from favorites' : 'Add to favorites';
}

function renderFavorites() {
  if (!elements.favoritesList) return;
  
  elements.favoritesList.innerHTML = '';
  
  state.favorites.forEach(symbol => {
    const chip = document.createElement('div');
    chip.className = 'favorite-chip';
    chip.innerHTML = `
      <span>${symbol}</span>
      <span class="remove" data-symbol="${symbol}">×</span>
    `;
    
    chip.querySelector('span:first-child').addEventListener('click', () => {
      setSymbol(symbol);
    });
    
    chip.querySelector('.remove').addEventListener('click', (e) => {
      e.stopPropagation();
      const sym = e.target.dataset.symbol;
      state.favorites = state.favorites.filter(f => f !== sym);
      localStorage.setItem('favorites', JSON.stringify(state.favorites));
      renderFavorites();
      updateFavoriteButton();
    });
    
    elements.favoritesList.appendChild(chip);
  });
}

function updateQuickStats() {
  if (!state.data) return;
  
  const symbols = state.data.symbols || Object.keys(state.data.stocks || {});
  elements.totalStocks.textContent = symbols.length;
  
  let bullish = 0;
  let bearish = 0;
  
  symbols.forEach(symbol => {
    const item = getPredictionItem(state.model, symbol);
    if (item && item.change_pct !== null) {
      if (item.change_pct > 0.2) bullish++;
      else if (item.change_pct < -0.2) bearish++;
    }
  });
  
  elements.bullishCount.textContent = bullish;
  elements.bearishCount.textContent = bearish;
}

function updateMarketOverview() {
  if (!state.data) return;
  
  // Market status (simplified - you can enhance with actual market hours)
  const now = new Date();
  const hour = now.getHours();
  const day = now.getDay();
  
  if (day === 0 || day === 6) {
    elements.marketStatus.textContent = "CLOSED";
    elements.marketStatus.style.color = "var(--muted)";
    elements.marketTime.textContent = "Next: SUNDAY 11:00 AM";
  } else if (hour >= 11 && hour < 15) {
    elements.marketStatus.textContent = "OPEN";
    elements.marketStatus.style.color = "var(--success)";
    elements.marketTime.textContent = "Closes at 3:00 PM";
  } else {
    elements.marketStatus.textContent = "CLOSED";
    elements.marketStatus.style.color = "var(--muted)";
    elements.marketTime.textContent = "Next: Tomorrow 11:00 AM";
  }
  
  // Calculate average accuracy
  const symbols = state.data.symbols || Object.keys(state.data.stocks || {});
  let totalAccuracy = 0;
  let count = 0;
  
  symbols.forEach(symbol => {
    const item = getPredictionItem(state.model, symbol);
    if (item && item.lstm_mae !== null && item.xgboost_mae !== null && item.today_close) {
      const mae = state.model === 'LSTM' ? item.lstm_mae : item.xgboost_mae;
      const accuracyPct = Math.max(0, Math.min(100, 100 - (mae / item.today_close * 100)));
      totalAccuracy += accuracyPct;
      count++;
    }
  });
  
  if (count > 0) {
    elements.avgAccuracy.textContent = (totalAccuracy / count).toFixed(1) + "%";
  }
  
  // Find top gainer and loser
  let maxChange = -Infinity;
  let minChange = Infinity;
  let topGainerSym = "--";
  let topLoserSym = "--";
  let topGainerVal = 0;
  let topLoserVal = 0;
  
  symbols.forEach(symbol => {
    // Skip NEPSE from top gainer/loser calculations
    if (symbol === 'NEPSE') return;
    
    const item = getPredictionItem(state.model, symbol);
    if (item && item.change_pct !== null && !isNaN(item.change_pct)) {
      if (item.change_pct > maxChange) {
        maxChange = item.change_pct;
        topGainerSym = symbol;
        topGainerVal = item.change_pct;
      }
      if (item.change_pct < minChange) {
        minChange = item.change_pct;
        topLoserSym = symbol;
        topLoserVal = item.change_pct;
      }
    }
  });
  
  elements.topGainer.textContent = topGainerSym;
  elements.topGainerChange.textContent = topGainerVal > 0 ? `+${topGainerVal.toFixed(2)}%` : "--";
  elements.topGainerChange.style.color = "var(--success)";
  
  elements.topLoser.textContent = topLoserSym;
  elements.topLoserChange.textContent = topLoserVal < 0 ? `${topLoserVal.toFixed(2)}%` : "--";
  elements.topLoserChange.style.color = "var(--danger)";
}

function updateTopStocks() {
  if (!state.data) return;
  
  const symbols = state.data.symbols || Object.keys(state.data.stocks || {});
  const stocksWithChanges = [];
  
  symbols.forEach(symbol => {
    // Skip NEPSE from top stocks list
    if (symbol === 'NEPSE') return;
    
    const item = getPredictionItem(state.model, symbol);
    if (item && item.change_pct !== null && !isNaN(item.change_pct)) {
      stocksWithChanges.push({
        symbol,
        changePct: item.change_pct,
        predictedClose: item.predicted_close,
        model: state.model,
      });
    }
  });
  
  // Sort and get top 5 gainers and losers
  const gainers = stocksWithChanges
    .filter(s => s.changePct > 0)
    .sort((a, b) => b.changePct - a.changePct)
    .slice(0, 5);
  
  const losers = stocksWithChanges
    .filter(s => s.changePct < 0)
    .sort((a, b) => a.changePct - b.changePct)
    .slice(0, 5);
  
  // Render gainers
  elements.topGainersList.innerHTML = '';
  gainers.forEach((stock, index) => {
    const item = document.createElement('div');
    item.className = 'stock-item';
    item.innerHTML = `
      <div class="stock-item-left">
        <div class="stock-rank">${index + 1}</div>
        <div>
          <div class="stock-symbol">${stock.symbol}</div>
          <div class="stock-model">${stock.model}</div>
        </div>
      </div>
      <div class="stock-item-right">
        <div class="stock-change positive">+${stock.changePct.toFixed(2)}%</div>
        <div class="stock-price">Rs ${stock.predictedClose.toFixed(2)}</div>
      </div>
    `;
    item.addEventListener('click', () => setSymbol(stock.symbol));
    elements.topGainersList.appendChild(item);
  });
  
  if (gainers.length === 0) {
    elements.topGainersList.innerHTML = '<div class="muted" style="padding: 20px; text-align: center;">No gainers predicted</div>';
  }
  
  // Render losers
  elements.topLosersList.innerHTML = '';
  losers.forEach((stock, index) => {
    const item = document.createElement('div');
    item.className = 'stock-item';
    item.innerHTML = `
      <div class="stock-item-left">
        <div class="stock-rank" style="background: rgba(242, 109, 109, 0.2); color: var(--danger);">${index + 1}</div>
        <div>
          <div class="stock-symbol">${stock.symbol}</div>
          <div class="stock-model">${stock.model}</div>
        </div>
      </div>
      <div class="stock-item-right">
        <div class="stock-change negative">${stock.changePct.toFixed(2)}%</div>
        <div class="stock-price">Rs ${stock.predictedClose.toFixed(2)}</div>
      </div>
    `;
    item.addEventListener('click', () => setSymbol(stock.symbol));
    elements.topLosersList.appendChild(item);
  });
  
  if (losers.length === 0) {
    elements.topLosersList.innerHTML = '<div class="muted" style="padding: 20px; text-align: center;">No losers predicted</div>';
  }
}

function exportPredictions() {
  if (!state.data) {
    alert('No data to export');
    return;
  }
  
  const symbols = state.data.symbols || Object.keys(state.data.stocks || {});
  let csv = 'Symbol,Model,Date,Predicted Open,Predicted High,Predicted Low,Predicted Close,Change,Change %,Signal\n';
  
  symbols.forEach(symbol => {
    ['LSTM', 'XGBoost', 'Ensemble'].forEach(model => {
      const item = getPredictionItem(model, symbol);
      if (item) {
        const signal = getSignal(item.change_pct);
        csv += `${symbol},${model},${item.date || ''},${formatValue(item.predicted_open)},${formatValue(item.predicted_high)},${formatValue(item.predicted_low)},${formatValue(item.predicted_close)},${formatValue(item.change)},${formatPct(item.change_pct)},${signal.text}\n`;
      }
    });
  });
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `nepse_predictions_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  window.URL.revokeObjectURL(url);
}

function toggleAutoRefresh() {
  if (elements.autoRefreshCheckbox.checked) {
    // Refresh every 5 minutes
    state.autoRefreshInterval = setInterval(() => {
      loadData();
    }, 5 * 60 * 1000);
  } else {
    if (state.autoRefreshInterval) {
      clearInterval(state.autoRefreshInterval);
      state.autoRefreshInterval = null;
    }
  }
}

function setTimeframe(days) {
  state.timeframeDays = days;
  elements.timeframeBtns.forEach((btn) => {
    btn.classList.toggle("active", parseInt(btn.dataset.days) === days);
  });
  if (state.data && state.symbol) {
    const item = getPredictionItem(state.model, state.symbol);
    if (item) updateChart(item);
  }
}

function toggleTheme() {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', state.theme);
  localStorage.setItem('theme', state.theme);
  
  // Update theme icon
  const icon = elements.themeToggle.querySelector('.theme-icon');
  icon.textContent = state.theme === 'dark' ? '\ud83c\udf19' : '\u2600\ufe0f';
  
  // Recreate chart with new theme
  if (state.chart && state.data && state.symbol) {
    const item = getPredictionItem(state.model, state.symbol);
    if (item) updateChart(item);
  }
}

function populateSymbols(symbols) {
  const sortedSymbols = symbols.slice().sort((a, b) => {
    if (a === "NEPSE") return -1;
    if (b === "NEPSE") return 1;
    return a.localeCompare(b);
  });

  state.allSymbols = sortedSymbols;
  elements.select.innerHTML = "";
  sortedSymbols.forEach((symbol) => {
    const option = document.createElement("option");
    option.value = symbol;
    option.textContent = symbol;
    elements.select.appendChild(option);
  });
  if (sortedSymbols.length) {
    setSymbol(sortedSymbols[0]);
  }
  renderFavorites();
  updateQuickStats();
  updateMarketOverview();
  updateTopStocks();
}

async function loadData() {
  try {
    const [predictionsResponse, historyResponse] = await Promise.all([
      fetch("data/predictions.json", { cache: "no-store" }),
      fetch("data/history.json", { cache: "no-store" }),
    ]);
    state.data = await predictionsResponse.json();
    state.history = historyResponse.ok ? await historyResponse.json() : null;
    const backtestResponse = await fetch("data/backtest_history.json", { cache: "no-store" });
    state.backtestHistory = backtestResponse.ok ? await backtestResponse.json() : null;
    const symbols = state.data.symbols || Object.keys(state.data.stocks || {});
    populateSymbols(symbols || []);
    
    // Update last updated time
    const now = new Date();
    elements.lastUpdated.textContent = now.toLocaleTimeString();
  } catch (error) {
    elements.signalText.textContent = "Data missing";
    elements.signalDesc.textContent = "Run export_predictions.py to generate data.";
    elements.dataStatus.style.color = 'var(--danger)';
  }
}

// Initialize theme
document.documentElement.setAttribute('data-theme', state.theme);
if (elements.themeToggle) {
  const icon = elements.themeToggle.querySelector('.theme-icon');
  icon.textContent = state.theme === 'dark' ? '\ud83c\udf19' : '\u2600\ufe0f';
}

// Event listeners
elements.toggles.forEach((btn) => {
  btn.addEventListener("click", () => setModel(btn.dataset.model));
});

elements.select.addEventListener("change", (event) => setSymbol(event.target.value));

elements.timeframeBtns.forEach((btn) => {
  btn.addEventListener("click", () => setTimeframe(parseInt(btn.dataset.days)));
});

if (elements.themeToggle) {
  elements.themeToggle.addEventListener("click", toggleTheme);
}

if (elements.stockSearch) {
  elements.stockSearch.addEventListener('input', (e) => {
    filterStocks(e.target.value);
  });
}

if (elements.favoriteBtn) {
  elements.favoriteBtn.addEventListener('click', toggleFavorite);
}

if (elements.refreshBtn) {
  elements.refreshBtn.addEventListener('click', () => {
    loadData();
  });
}

if (elements.exportBtn) {
  elements.exportBtn.addEventListener('click', exportPredictions);
}

if (elements.autoRefreshCheckbox) {
  elements.autoRefreshCheckbox.addEventListener('change', toggleAutoRefresh);
}

loadData();
