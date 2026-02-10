from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os

def scrape_stock(symbol):
    """
    Scrape OHLC + volume for a single stock and save to data/{symbol}.csv
    """
    data_rows = []
    import json as json_module

    with sync_playwright() as p:
        # Launch with more realistic browser settings
        browser = p.chromium.launch(
            headless=True,  # Run in headless mode (faster, no browser window)
            args=[
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        # Create context with realistic settings
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
        )
        
        page = context.new_page()
        
        # Add script to hide automation flags
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        url = f"https://nepsealpha.com/trading/chart?symbol={symbol}"
        page.goto(url, wait_until='networkidle')

        print(f"  Waiting for page to load and Cloudflare to resolve...")
        time.sleep(15)  # Give more time for Cloudflare challenge

        # Use wait_for_response to capture the API call
        try:
            with page.expect_response(lambda response: "/trading/1/history" in response.url and response.status == 200) as response_info:
                page.reload()
                # Wait for response with timeout
                response = response_info.value
                print(f"  ✓ Found history API")
                
                # Read the response body while page is still open
                body_text = response.text()
                print(f"  Response length: {len(body_text)} bytes")
                
                # Try to parse
                json_data = json_module.loads(body_text)
                print(f"  Response type: {type(json_data)}")
                
                if isinstance(json_data, dict):
                    print(f"  Response keys: {list(json_data.keys())}")
                    
                    # TradingView format: separate arrays for each field
                    t = json_data.get('t', [])  # time
                    o = json_data.get('o', [])  # open
                    h = json_data.get('h', [])  # high
                    l = json_data.get('l', [])  # low
                    c = json_data.get('c', [])  # close
                    v = json_data.get('v', [])  # volume
                    
                    print(f"  Found {len(t)} timestamps")
                    
                    # Zip arrays together row by row
                    for i in range(len(t)):
                        data_rows.append({
                            "date": t[i],
                            "open": o[i] if i < len(o) else None,
                            "high": h[i] if i < len(h) else None,
                            "low": l[i] if i < len(l) else None,
                            "close": c[i] if i < len(c) else None,
                            "volume": v[i] if i < len(v) else None
                        })
                    
                    print(f"  Parsed {len(data_rows)} rows")
                    
                elif isinstance(json_data, list):
                    print(f"  Response is list with {len(json_data)} items")
                    # Handle list format
                    data = json_data
        except Exception as e:
            print(f"  Error capturing response: {type(e).__name__}: {e}")
        
        context.close()
        browser.close()

    # Save CSV (append new rows, drop duplicates)
    print(f"  Total rows collected: {len(data_rows)}")
    os.makedirs("data", exist_ok=True)
    df_new = pd.DataFrame(data_rows)
    csv_path = f"data/{symbol}.csv"

    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    if not df_combined.empty:
        df_combined = df_combined.dropna(subset=["date"])
        df_combined = df_combined.drop_duplicates(subset=["date"], keep="last")
        df_combined = df_combined.sort_values("date").reset_index(drop=True)

    df_combined.to_csv(csv_path, index=False)
    print(f"Saved {symbol}.csv with {len(df_combined)} rows")

if __name__ == "__main__":
    # Diverse stocks from different sectors
    symbols = [
        # Index
        "NEPSE",
        # Commercial Banks
        "NABIL", "NICA", "SBI", "EBL", "KBL", "ADBL",
        # Hydro Power
        "CHCL", "UPPER", "NHPC", "API", "SHPC",
        # Finance Companies
        "GUFL", "GFCL",
        # Insurance
        "NLIC", "SICL", "HGI",
        # Hotels
        "OHL", "SHL",
        # Manufacturing
        "UNL"
    ]
    
    print(f"\n{'='*60}")
    print(f"📊 Scraping {len(symbols)} stocks from different sectors")
    print(f"{'='*60}\n")
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Scraping {symbol}...")
        try:
            scrape_stock(symbol)
        except Exception as e:
            print(f"❌ Error scraping {symbol}: {e}")
