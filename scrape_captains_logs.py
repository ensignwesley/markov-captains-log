#!/usr/bin/env python3
"""
Star Trek Captain's Log Scraper
Scrapes transcripts from chakoteya.net and extracts captain's log entries.
"""

import re
import time
import requests
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    """Simple HTML tag stripper"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, d):
        self.text.append(d)
    
    def get_data(self):
        return ''.join(self.text)

def strip_tags(html):
    """Remove HTML tags from text"""
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def scrape_episode(episode_num, series="NextGen"):
    """Scrape a single episode and extract captain's log entries"""
    url = f"http://www.chakoteya.net/{series}/{episode_num}.htm"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        
        content = response.text
        
        # Find all captain's log entries
        # Pattern: "Captain's log" followed by text until next paragraph/section
        pattern = r"Captain's log[^<]*(?:<[^>]*>[^<]*)*?(?=<(?:p|table|hr|h\d)|\Z)"
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        
        logs = []
        for match in matches:
            # Strip HTML and clean up
            clean = strip_tags(match)
            clean = re.sub(r'\s+', ' ', clean).strip()
            
            # Skip if too short (likely a fragment)
            if len(clean) > 50:
                logs.append(clean)
        
        return logs
    
    except Exception as e:
        print(f"Error scraping episode {episode_num}: {e}")
        return []

def scrape_tng_logs(max_episodes=50, delay=0.5):
    """Scrape captain's logs from TNG episodes"""
    all_logs = []
    
    # TNG episodes: 101-176 (season 1-7)
    # Start with first 50 to avoid hammering the server
    episode_numbers = [str(i) for i in range(101, 101 + max_episodes)]
    
    print(f"Scraping {len(episode_numbers)} TNG episodes...")
    
    for i, ep_num in enumerate(episode_numbers):
        print(f"[{i+1}/{len(episode_numbers)}] Episode {ep_num}...", end=" ")
        
        logs = scrape_episode(ep_num)
        all_logs.extend(logs)
        
        print(f"{len(logs)} logs found")
        
        # Be polite to the server
        if i < len(episode_numbers) - 1:
            time.sleep(delay)
    
    return all_logs

if __name__ == "__main__":
    logs = scrape_tng_logs()
    
    print(f"\nTotal logs extracted: {len(logs)}")
    print(f"\nSample logs:")
    for i, log in enumerate(logs[:3]):
        print(f"\n--- Log {i+1} ---")
        print(log[:200] + "..." if len(log) > 200 else log)
    
    # Save to file
    with open('captains_logs_raw.txt', 'w') as f:
        for log in logs:
            f.write(log + "\n\n")
    
    print(f"\nLogs saved to captains_logs_raw.txt")
