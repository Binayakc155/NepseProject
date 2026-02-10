# 🔧 Troubleshooting Guide

Complete reference for diagnosing and fixing NEPSE prediction system issues.

---

## 🆘 Symptoms & Solutions

### Issue: "ModuleNotFoundError: No module named 'tensorflow'"

**Symptom:**
```
Traceback (most recent call last):
  File "lstm_predict.py", line 1, in <module>
    import tensorflow
ModuleNotFoundError: No module named 'tensorflow'
```

**Solution:**
```powershell
pip install tensorflow scikit-learn
```

**Prevention:**
Ensure you ran:
```powershell
pip install -r requirements.txt
```

---

### Issue: "File not found: scripts/data/NABIL.csv"

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'scripts/data/NABIL.csv'
```

**Root Cause:** Haven't downloaded stock data yet

**Solution:**
```powershell
cd scripts
python scrape_stock.py
```

**Wait Time:** 10-15 minutes to download ~14 years of data for 20 stocks

---

### Issue: Web dashboard shows old/no data

**Symptom:**
- Website loads but shows last month's prices
- "No stocks to display" message
- Dashboard is blank

**Solution:**

**Step 1: Check if predictions exist**
```powershell
cd scripts
python status_check.py
```

**Step 2: Generate fresh predictions**
```powershell
python export_predictions_v2.py
```

**Step 3: Clear browser cache**
- Press `Ctrl + Shift + Delete` in browser
- Clear "Cached images and files"

**Step 4: Hard refresh website**
- Press `Ctrl + Shift + R` (or `Cmd + Shift + R` on Mac)

**Step 5: Check file timestamp**
```powershell
Get-Item web/data/predictions.json | % LastWriteTime
```
Should be recent (within last hour or today)

---

### Issue: Auto-update not running

**Symptom:**
- Scheduled time passes (3:10 PM) but nothing happens
- No new data appears in CSV files
- `auto_update.log` not created

**Debug:**
```powershell
cd scripts
echo "Checking auto_update..."
$time = Get-Date
Write-Host "Current time: $time"
Write-Host "Scheduled time: 3:10 PM weekdays"
```

**Common Causes:**

#### ① Terminal not open
**Fix:** Keep terminal open 24/7 where `auto_update.py` is running

#### ② Script crashed
**Check log:**
```powershell
tail -f scripts/auto_update.log
```

**Restart:**
```powershell
cd scripts
python auto_update.py
```

#### ③ Wrong time zone
**Check:**
```powershell
Get-Date
```
Should show your local time

**Set correct time:** Windows Settings → Date & Time

#### ④ Running on weekend
**Note:** Script only runs Monday-Friday
Check which day it is:
```powershell
Get-Date -Format "dddd"
```

#### ⑤ System time off by hours
**Fix:**
```powershell
# Force time sync
w32tm /resync
```

---

### Issue: "Scraped data is empty (0 rows)"

**Symptom:**
```
CSV file created but has no data rows
Only headers: date,open,high,low,close,volume
```

**Root Cause:** Cloudflare challenge or bot detection

**Solution:**

**Step 1: Check network**
```powershell
# Verify internet connection
ping google.com
```

**Step 2: Try manual scrape with debugging**
```powershell
cd scripts
python scrape_stock.py
```
Wait 5-10 minutes and watch for errors

**Step 3: Check website accessibility**
Open in browser: `https://nepsealpha.com`
If blocked, website may be down

**Step 4: Verify Playwright installation**
```powershell
pip install --upgrade playwright
python -m playwright install chromium
```

**Step 5: Check script directly**
Edit `scrape_stock.py`, change one stock to debug:
```python
STOCKS = ['NABIL']  # Just one stock to test
```

---

### Issue: Models training very slowly

**Symptom:**
- LSTM training takes >30 minutes
- XGBoost training takes >15 minutes
- System feels frozen

**Causes & Solutions:**

#### ① Not using GPU (using CPU instead)
**Check:**
```powershell
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

**If empty (using CPU):**
- CPU training IS slow - this is normal
- LSTM on CPU: 8-15 min for 20 stocks
- XGBoost on CPU: 3-5 min for 20 stocks
- This is expected behavior

#### ② Disk I/O bottleneck
**Check:** Are you using SSD or HDD?
- SSD: Normal
- HDD: Will be very slow

#### ③ Too many stocks
**Solution:** Test with just 3 stocks first:
```python
STOCKS = ['NABIL', 'NICA', 'NEPSE']
```

---

### Issue: Out of memory error (OOM)

**Symptom:**
```
MemoryError: Unable to allocate 2.5 GB
CUDA out of memory: tried to allocate 2.00 GB
```

**Root Cause:** Trying to train on too much data

**Solutions:**

**Option 1: Reduce data size**
In `lstm_predict.py`, change window size:
```python
WINDOW_SIZE = 30  # Was 60, reduce to 30
```

**Option 2: Reduce batch size**
```python
model.fit(X_train, y_train, batch_size=8, ...)  # Was 16, reduce to 8
```

**Option 3: Use fewer stocks** (for testing)
```python
STOCKS = ['NABIL', 'NICA', 'NEPSE']  # Just 3 stocks
```

**Option 4: Check available memory**
```powershell
Get-WmiObject Win32_OperatingSystem | select @{Name="Available Memory (GB)"; Expression={[math]::Round($_.FreePhysicalMemory/1mb,2)}}
```

---

### Issue: Export to JSON fails

**Symptom:**
```
Error: File 'predictions.json' not found in web
KeyError: 'predicted_open'
```

**Debug:**
```powershell
cd scripts
python export_predictions_v2.py
```

**Check outputs:**
```powershell
ls predictions/
```
Should show: `lstm_predictions.csv`, `xgboost_predictions.csv`

**If csv files missing:**
```powershell
python lstm_predict.py
python xgboost_predict.py
python export_predictions_v2.py
```

---

### Issue: "Connection timeout" during scraping

**Symptom:**
```
urllib.error.URLError: <urlopen error timed out>
Timeout waiting for response
```

**Cause:** Website taking too long or internet connection slow

**Solution:**

**Option 1: Increase timeout**
In `scrape_stock.py`, change:
```python
page.wait_for_timeout(60000)  # 60 seconds instead of 30
```

**Option 2: Check internet speed**
```powershell
ping 8.8.8.8 -n 10
```
Should show <50ms response time

**Option 3: Check website status**
Open in browser: `https://nepsealpha.com`
If slow/down, try again later

**Option 4: Use VPN** (might help if blocked)
- If website blocks your region
- Use a VPN to change location

---

### Issue: Predictions are always wrong/not changing

**Symptom:**
- Same prices predicted every day
- Predictions don't match actual movement
- All stocks show "neutral" signal

**Causes & Solutions:**

#### ① Data not updating
**Check:**
```powershell
cd scripts
tail -1 data/NABIL.csv
```
Should show today's date

**Fix:**
```powershell
python scrape_stock.py
python lstm_predict.py
python xgboost_predict.py
```

#### ② Models not retraining
**Check:**
```powershell
python status_check.py
```
Look for "Models last trained" time

**Fix:** Retrain today:
```powershell
python update_now.py
```

#### ③ Bad hyperparameters
**Test which model is better:**
```powershell
python backtest_comparison.py
```

If one model consistently wins:
- Use Ensemble to average both
- Or switch to better model

---

### Issue: Data duplication/prices changing unexpectedly

**Symptom:**
- Same date appears twice in CSV
- Historical prices changed from yesterday
- File size unexpectedly doubled

**Root Cause:** Scraper saved same data twice

**Solution:**

**Step 1: Verify duplicates**
```powershell
cd scripts
$csv = Import-Csv data/NABIL.csv
$csv | Group-Object date | Where {$_.Count -gt 1}
```

**Step 2: Clean up** (automatic in current version)
Script already handles deduplication:
```python
df.drop_duplicates(subset=['date'], keep='last', inplace=True)
```

**Step 3: Restart pipeline**
```powershell
python update_now.py
```

---

### Issue: Playwright/browser errors

**Symptom:**
```
Error: Cannot find Chrome/Chromium binary
TimeoutError: waiting for navigation
BrowserContext is closed
```

**Solution:**

**Step 1: Reinstall Playwright**
```powershell
pip install --upgrade playwright
python -m playwright install
python -m playwright install-deps
```

**Step 2: Check if browser installed**
```powershell
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('✅ Playwright OK')"
```

**Step 3: Use headless mode**
In `scrape_stock.py`:
```python
browser = p.chromium.launch(headless=True)  # Add headless=True
```

---

### Issue: Port 8000 already in use (web server)

**Symptom:**
```
OSError: [Errno 10048] Only one usage of each socket address
Address already in use
```

**Solution:**

**Option 1: Use different port**
```powershell
cd web
python -m http.server 8001  # Use 8001 instead
# Open: http://localhost:8001
```

**Option 2: Kill existing process**
```powershell
Get-Process python | Where {$_.CommandLine -like '*http.server*'} | Stop-Process
```

**Option 3: Check what's using port**
```powershell
netstat -ano | findstr :8000
```

---

## 🔍 Diagnostic Commands

Quick commands to diagnose issues:

```powershell
# Check system info
systeminfo | findstr /B "OS Computer"

# Check Python version
python --version

# Check installed packages
pip list | grep -E "tensorflow|xgboost|pandas|playwright"

# Check disk space
Get-Volume | where {$_.Size -gt 1GB} | select DriveLetter, Size, SizeRemaining

# Check memory usage
Get-Process | Measure-Object -Property WorkingSet -Sum | select @{N="Memory (GB)";E={[math]::round($_.sum/1gb,2)}}

# Check network
ping nepsealpha.com

# List all CSV files and sizes
dir scripts/data/*.csv -Size

# Show latest scrape timestamp
Get-Item scripts/data/NABIL.csv | select LastWriteTime

# Show available models
ls scripts/predictions/
```

---

## 📊 Checking System Health (Full Diagnostic)

```powershell
cd scripts
python status_check.py
```

Output will show:
- ✅ Stock data age
- ✅ Prediction files status
- ✅ Web interface readiness
- ✅ Auto-update status
- 💡 Recommended actions

---

## 🛠️ Common Fixes (Copy-Paste)

### Fix 1: Complete Reset
```powershell
cd scripts
Remove-Item predictions -Recurse -Force
Remove-Item ..\web\data\predictions.json -Force
python run_all.py
```

### Fix 2: Quick Retrain
```powershell
cd scripts
python lstm_predict.py
python xgboost_predict.py
python export_predictions_v2.py
```

### Fix 3: Rebuild Everything
```powershell
cd scripts
# WARNING: Downloads 14+ years again (~15 min)
Remove-Item data -Recurse -Force
python scrape_stock.py
python run_all.py
```

### Fix 4: Update Dependencies
```powershell
pip install --upgrade tensorflow xgboost scikit-learn pandas playwright
python -m playwright install
```

---

## 📋 Pre-Troubleshooting Checklist

Before reporting an issue, verify:

- [ ] Python 3.9+ installed: `python --version`
- [ ] Requirements installed: `pip show tensorflow`
- [ ] Internet connected: `ping 8.8.8.8`
- [ ] Sufficient disk space: `Get-Volume`
- [ ] Sufficient RAM: Task Manager → Performance
- [ ] Stock data exists: `ls scripts/data/`
- [ ] Prediction files exist: `ls scripts/predictions/`

---

## 📞 When Nothing Works

### Step 1: Collect diagnostic info
```powershell
cd scripts
python status_check.py > diagnostic_report.txt
Get-Process | Sort CPU -Descending | select Name, CPU, Memory -First 5 >> diagnostic_report.txt
systeminfo >> diagnostic_report.txt
```

### Step 2: Check logs
```powershell
cat auto_update.log
cat export_predictions.log
cat scrape_stock.log (if exists)
```

### Step 3: Try minimal test
```powershell
# Test with just 1 stock
python -c "
STOCKS = ['NABIL']
from lstm_predict import train_and_predict
train_and_predict()
"
```

### Step 4: Restart everything
```powershell
# Kill all Python processes
Get-Process python | Stop-Process -Force

# Clear temp files
Remove-Item __pycache__ -Recurse -Force -ErrorAction SilentlyContinue

# Reinstall
pip install --upgrade --force-reinstall tensorflow xgboost

# Try again
python update_now.py
```

---

## 🆘 Still Stuck?

Provide:
1. Output from `python status_check.py`
2. Error message (if any)
3. Last 10 lines of `auto_update.log` or `export_predictions.log`
4. OS version: `systeminfo`
5. Python version: `python --version`

---

**Last Updated:** February 11, 2026
**Status Page:** See README_USAGE.md
**Quick Guide:** See QUICKSTART.md
