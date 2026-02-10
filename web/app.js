const state = {
  data: null,
  model: "LSTM",
  symbol: null,
};

const elements = {
  select: document.getElementById("symbol-select"),
  toggles: document.querySelectorAll(".toggle"),
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
    return { text: "No signal", desc: "Prediction data unavailable." };
  }
  if (changePct > 0.2) {
    return { text: "Bullish", desc: "Model expects upward movement." };
  }
  if (changePct < -0.2) {
    return { text: "Bearish", desc: "Model expects downward movement." };
  }
  return { text: "Neutral", desc: "Model expects sideways movement." };
}

function updateUI() {
  if (!state.data || !state.symbol) {
    return;
  }

  const modelData = state.data.models[state.model] || {};
  const item = modelData[state.symbol];

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
    return;
  }

  const changePct = item.change_pct;
  const signal = getSignal(changePct);

  elements.predOpen.textContent = formatValue(item.predicted_open);
  elements.predHigh.textContent = formatValue(item.predicted_high);
  elements.predLow.textContent = formatValue(item.predicted_low);
  elements.predClose.textContent = formatValue(item.predicted_close);
  elements.predClose2.textContent = formatValue(item.predicted_close);
  elements.predChange.textContent = `Change: ${formatValue(item.change)} (${formatPct(changePct)})`;
  elements.predDate.textContent = item.date || "--";
  elements.predModel.textContent = `${state.model} model`;
  elements.signalText.textContent = signal.text;
  elements.signalDesc.textContent = signal.desc;
  
  // Update model button badges to show recommended model
  updateModelBadges(item);
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
      badge.textContent = ' ⭐';
      
      // Add tooltip with accuracy info
      let title = `Best for ${state.symbol}`;
      if (lstmMae !== null && xgboostMae !== null) {
        const mae = modelName === 'LSTM' ? lstmMae : xgboostMae;
        title += ` (MAE: ±${mae} Rs)`;
      }
      badge.title = title;
      btn.appendChild(badge);
    }
  });
}

function setModel(model) {
  state.model = model;
  elements.toggles.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.model === model);
  });
  updateUI();
}

function setSymbol(symbol) {
  state.symbol = symbol;
  updateUI();
}

function populateSymbols(symbols) {
  elements.select.innerHTML = "";
  symbols.forEach((symbol) => {
    const option = document.createElement("option");
    option.value = symbol;
    option.textContent = symbol;
    elements.select.appendChild(option);
  });
  if (symbols.length) {
    setSymbol(symbols[0]);
  }
}

async function loadData() {
  try {
    const response = await fetch("data/predictions.json", { cache: "no-store" });
    state.data = await response.json();
    populateSymbols(state.data.symbols || []);
  } catch (error) {
    elements.signalText.textContent = "Data missing";
    elements.signalDesc.textContent = "Run export_predictions.py to generate data.";
  }
}

elements.toggles.forEach((btn) => {
  btn.addEventListener("click", () => setModel(btn.dataset.model));
});

elements.select.addEventListener("change", (event) => setSymbol(event.target.value));

loadData();
