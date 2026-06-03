import os
import time
import requests
import pandas as pd

# List of schemes to fetch from mfapi.in
SCHEMES = {
    125497: "HDFC Top 100",
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip",
    120841: "Kotak Bluechip"
}

def fetch_and_save_nav(scheme_code, scheme_name, max_retries=5, backoff_factor=3):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for attempt in range(1, max_retries + 1):
        print(f"Fetching NAV data for {scheme_name} (Code: {scheme_code}), Attempt {attempt}/{max_retries}...")
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data_json = response.json()
            
            if 'data' not in data_json or not data_json['data']:
                print(f"Warning: No data returned for scheme {scheme_code}")
                return False
            
            # Convert data list of dicts to DataFrame
            df = pd.DataFrame(data_json['data'])
            
            # Add metadata fields to the DataFrame
            df['scheme_code'] = scheme_code
            df['scheme_name'] = data_json.get('meta', {}).get('scheme_name', scheme_name)
            
            # Reorder columns for clean layout
            df = df[['scheme_code', 'scheme_name', 'date', 'nav']]
            
            # Save to csv inside data/raw (absolute path resolution relative to script)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, "data", "raw")
            output_path = os.path.join(output_dir, f"{scheme_code}_raw.csv")
            df.to_csv(output_path, index=False)
            print(f"Successfully saved {len(df)} records to {output_path}")
            return True
            
        except requests.exceptions.HTTPError as he:
            status_code = he.response.status_code if he.response is not None else None
            print(f"HTTP error {status_code} occurred for scheme {scheme_code}: {he}")
            # If server error or gateway error, wait and retry
            if status_code in [500, 502, 503, 504] and attempt < max_retries:
                sleep_time = backoff_factor * attempt
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                break
        except Exception as e:
            print(f"Error fetching data for scheme {scheme_code}: {e}")
            if attempt < max_retries:
                sleep_time = backoff_factor * attempt
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                break
                
    return False

def main():
    # Ensure directory exists relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    for code, name in SCHEMES.items():
        # Add a short delay between schemes to avoid overwhelming the server
        if success_count > 0:
            time.sleep(2)
        if fetch_and_save_nav(code, name):
            success_count += 1
            
    print(f"\nFetch completed: {success_count}/{len(SCHEMES)} schemes successfully fetched and saved to data/raw/")

if __name__ == "__main__":
    main()
