import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib3
import time
from datetime import datetime

# --- CONFIGURATION ---
# 1. Disable SSL Warnings (Crucial for State Govt sites)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. Browser Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# 3. The "Mega List" of Target URLs
TARGET_PORTALS = {
    "ICMR (Central)": "https://www.icmr.gov.in/employment-opportunities",
    "NHSRC (Central)": "https://nhsrcindia.org/career",
    "NCDC (Central)": "https://ncdc.mohfw.gov.in/vacancies/",
    "NHM Maharashtra": "https://nhm.maharashtra.gov.in/en/notice-category/recruitments/",
    "NHM Kerala": "https://arogyakeralam.gov.in/category/careers/",
    "NHM Odisha": "https://nhmodisha.gov.in/vacancies/",
    "NHM Haryana": "https://haryanahealth.gov.in/notice-category/recruitments/",
    "NHM Assam": "https://nhm.assam.gov.in/portlets/recruitment",
    "TISS Projects": "https://tiss.edu/project-positions/",
    "BECIL (Outsourcing)": "https://www.becil.com/vacancies"
}

# 4. Keywords to Flag (Case Insensitive)
KEYWORDS = [
    "MPH", "Public Health", "Epidemiologist", "Consultant", 
    "Program Manager", "Community", "Research", "Health", "Officer"
]

def scrape_portal(name, url):
    print(f"🌍 Scanning {name}...")
    found_links = []
    
    try:
        # verify=False prevents SSL errors on govt sites
        response = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Grab all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            text = link.get_text(" ", strip=True)
            href = link['href']
            
            # Cleaning: Many sites have empty links or just "Click Here"
            if len(text) < 5: 
                continue

            # Check for Keyword Matches
            if any(k.lower() in text.lower() for k in KEYWORDS):
                
                # Fix Relative URLs
                if not href.startswith("http"):
                    # Handle different relative path styles
                    base_url = "/".join(url.split('/')[:3]) # Get domain root
                    if href.startswith("/"):
                        href = base_url + href
                    else:
                        href = url.rstrip('/') + "/" + href

                found_links.append({
                    "Organization": name,
                    "Notification Text": text[:150], # Trim long titles
                    "Link": href,
                    "Date Scraped": datetime.now().strftime("%Y-%m-%d")
                })
                
    except Exception as e:
        print(f"❌ Error on {name}: {e}")

    return found_links

# --- MAIN RUNNER ---
if __name__ == "__main__":
    print(f"🚀 Starting Scan of {len(TARGET_PORTALS)} Government Portals...\n")
    
    master_list = []
    
    for name, url in TARGET_PORTALS.items():
        jobs = scrape_portal(name, url)
        if jobs:
            print(f"   ✅ Found {len(jobs)} potential leads.")
            master_list.extend(jobs)
        else:
            print("   ⚠️ No text matches found.")
        time.sleep(1) # Be polite to their servers

    # Save Results
    if master_list:
        df = pd.DataFrame(master_list)
        # Remove duplicates
        df = df.drop_duplicates(subset=['Link'])
        
        filename = f"Govt_MPH_Jobs_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"\n🎉 Done! Saved {len(df)} jobs to '{filename}'")
        print(df.head())
    else:
        print("\n😔 No jobs found today.")
