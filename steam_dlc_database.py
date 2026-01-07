#!/usr/bin/env python3
"""
Rocksmith 2014 Steam DLC Database
Fetches and caches Steam DLC information for better Content ID mapping

Steam DLC List: https://steamdb.info/app/221680/dlc/
"""

import json
import re
import requests
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

class SteamDLCDatabase:
    """Manages Steam DLC information for Rocksmith 2014"""
    
    ROCKSMITH_APP_ID = 221680
    STEAM_API_URL = "https://store.steampowered.com/api/appdetails"
    CACHE_FILE = "steam_dlc_cache.json"
    
    def __init__(self, cache_dir: Path = Path(".")):
        self.cache_dir = cache_dir
        self.cache_path = cache_dir / self.CACHE_FILE
        self.dlc_data = {}
        self.load_cache()
    
    def load_cache(self) -> bool:
        """Load cached DLC data"""
        try:
            if self.cache_path.exists():
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    self.dlc_data = cache.get('dlc', {})
                    print(f"✓ Loaded {len(self.dlc_data)} DLC entries from cache")
                    return True
        except Exception as e:
            print(f"⚠ Could not load cache: {e}")
        return False
    
    def save_cache(self):
        """Save DLC data to cache"""
        try:
            cache = {
                'last_updated': datetime.now().isoformat(),
                'dlc': self.dlc_data
            }
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(self.dlc_data)} DLC entries to cache")
        except Exception as e:
            print(f"⚠ Could not save cache: {e}")
    
    def fetch_dlc_info(self, app_id: int) -> Optional[Dict]:
        """Fetch DLC information from Steam API"""
        try:
            params = {
                'appids': app_id,
                'cc': 'us',
                'l': 'english'
            }
            
            response = requests.get(self.STEAM_API_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if str(app_id) in data and data[str(app_id)].get('success'):
                return data[str(app_id)]['data']
            
            return None
            
        except Exception as e:
            print(f"⚠ Could not fetch DLC {app_id}: {e}")
            return None
    
    def parse_dlc_name(self, name: str) -> Dict[str, str]:
        """
        Parse DLC name to extract artist and song
        
        Common formats:
        - "Rocksmith® 2014 Edition – Remastered – Artist - Song"
        - "Rocksmith® 2014 – Artist - Song Pack"
        - "Artist Song Pack"
        """
        # Remove Rocksmith branding
        clean_name = re.sub(r'Rocksmith[®™]?\s*2014\s*(Edition)?\s*[–-]\s*(Remastered\s*[–-]\s*)?', '', name)
        
        # Try to extract artist and song
        patterns = [
            r'^(.+?)\s*-\s*(.+?)(?:\s+Pack)?$',  # Artist - Song
            r'^(.+?)\s+Song\s+Pack\s*(?:I+)?$',   # Artist Song Pack
            r'^(.+)$',                             # Just name
        ]
        
        for pattern in patterns:
            match = re.match(pattern, clean_name)
            if match:
                if len(match.groups()) == 2:
                    return {
                        'artist': match.group(1).strip(),
                        'song': match.group(2).strip(),
                        'raw_name': clean_name.strip()
                    }
                else:
                    return {
                        'artist': '',
                        'song': match.group(1).strip(),
                        'raw_name': clean_name.strip()
                    }
        
        return {
            'artist': '',
            'song': clean_name.strip(),
            'raw_name': clean_name.strip()
        }
    
    def add_dlc(self, app_id: int, force_fetch: bool = False):
        """Add DLC to database"""
        app_id_str = str(app_id)
        
        if app_id_str in self.dlc_data and not force_fetch:
            print(f"  DLC {app_id} already in cache")
            return
        
        print(f"  Fetching DLC {app_id}...")
        
        dlc_info = self.fetch_dlc_info(app_id)
        if dlc_info:
            parsed = self.parse_dlc_name(dlc_info.get('name', ''))
            
            self.dlc_data[app_id_str] = {
                'app_id': app_id,
                'name': dlc_info.get('name', ''),
                'artist': parsed['artist'],
                'song': parsed['song'],
                'raw_name': parsed['raw_name'],
                'release_date': dlc_info.get('release_date', {}).get('date', ''),
                'price': dlc_info.get('price_overview', {}).get('final_formatted', ''),
            }
            
            print(f"  ✓ Added: {parsed['artist']} - {parsed['song']}")
        else:
            print(f"  ✗ Failed to fetch DLC {app_id}")
    
    def bulk_add_dlc(self, app_ids: List[int], delay: float = 1.0):
        """Add multiple DLC entries with delay between requests"""
        import time
        
        print(f"\nFetching {len(app_ids)} DLC entries...")
        
        for i, app_id in enumerate(app_ids, 1):
            print(f"[{i}/{len(app_ids)}]", end=" ")
            self.add_dlc(app_id)
            
            if i < len(app_ids):
                time.sleep(delay)  # Be nice to Steam API
        
        self.save_cache()
    
    def find_by_name(self, search: str) -> List[Dict]:
        """Search DLC by artist or song name"""
        search_lower = search.lower()
        results = []
        
        for app_id, dlc in self.dlc_data.items():
            if (search_lower in dlc.get('artist', '').lower() or
                search_lower in dlc.get('song', '').lower() or
                search_lower in dlc.get('name', '').lower()):
                results.append(dlc)
        
        return results
    
    def find_by_app_id(self, app_id: int) -> Optional[Dict]:
        """Get DLC by Steam App ID"""
        return self.dlc_data.get(str(app_id))
    
    def generate_content_id(self, dlc_info: Dict, region: str = "EP0001", 
                           title_id: str = "CUSA00745") -> str:
        """
        Generate PS4 Content ID from Steam DLC info
        
        Format: REGION-TITLEID_00-APPID00000000000
        Where APPID is padded to 16 characters
        """
        app_id = str(dlc_info.get('app_id', '0'))
        
        # Pad app_id to 16 characters
        suffix = f"APPID{app_id}".ljust(16, '0')[:16]
        
        content_id = f"{region}-{title_id}_00-{suffix}"
        
        return content_id
    
    def get_known_dlc_list(self) -> List[int]:
        """
        Return list of known Rocksmith 2014 DLC App IDs
        
        This is a curated list of common DLC.
        For complete list, check: https://steamdb.info/app/221680/dlc/
        """
        # Sample of known DLC (you can expand this)
        return [
            222120,  # Alice Cooper - Poison
            222121,  # The Black Keys - Gold on the Ceiling
            222122,  # Bob Dylan - Knockin' on Heaven's Door
            222123,  # Boston - Peace of Mind
            # Add more as needed
        ]
    
    def search_by_filename(self, filename: str) -> Optional[Dict]:
        """
        Search for DLC by filename (song code)
        
        Attempts fuzzy matching on artist and song names
        Returns first match or None
        """
        filename_lower = filename.lower().replace('_', ' ').replace('-', ' ')
        
        for app_id, dlc in self.dlc_data.items():
            # Try to match artist and song name
            artist = dlc.get('artist', '').lower()
            song = dlc.get('song', '').lower()
            name = dlc.get('name', '').lower()
            
            # Check if filename contains artist and/or song
            if (artist and artist in filename_lower) or (song and song in filename_lower):
                return {
                    'app_id': int(app_id),
                    'title': dlc.get('name', 'Unknown'),
                    'artist': dlc.get('artist', 'Unknown'),
                    'song': dlc.get('song', 'Unknown'),
                    'release_date': dlc.get('release_date'),
                    'price': dlc.get('price')
                }
            
            # Check if filename matches any part of the full name
            if name and name in filename_lower:
                return {
                    'app_id': int(app_id),
                    'title': dlc.get('name', 'Unknown'),
                    'artist': dlc.get('artist', 'Unknown'),
                    'song': dlc.get('song', 'Unknown'),
                    'release_date': dlc.get('release_date'),
                    'price': dlc.get('price')
                }
        
        return None
    
    def export_to_json(self, output_path: Path):
        """Export database to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.dlc_data, f, indent=2, ensure_ascii=False)
            print(f"✓ Exported {len(self.dlc_data)} entries to {output_path}")
        except Exception as e:
            print(f"✗ Export failed: {e}")
    
    def import_from_json(self, input_path: Path):
        """Import database from JSON file"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                self.dlc_data = json.load(f)
            print(f"✓ Imported {len(self.dlc_data)} entries from {input_path}")
            self.save_cache()
        except Exception as e:
            print(f"✗ Import failed: {e}")

def main():
    """Command-line interface for Steam DLC database"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rocksmith 2014 Steam DLC Database')
    parser.add_argument('--fetch', type=int, nargs='+', help='Fetch DLC by App ID(s)')
    parser.add_argument('--fetch-known', action='store_true', help='Fetch known DLC list')
    parser.add_argument('--search', type=str, help='Search DLC by name')
    parser.add_argument('--export', type=str, help='Export database to JSON')
    parser.add_argument('--import', type=str, dest='import_file', help='Import database from JSON')
    parser.add_argument('--list', action='store_true', help='List all cached DLC')
    
    args = parser.parse_args()
    
    db = SteamDLCDatabase()
    
    if args.fetch:
        db.bulk_add_dlc(args.fetch)
    
    if args.fetch_known:
        print("Fetching known DLC list...")
        db.bulk_add_dlc(db.get_known_dlc_list())
    
    if args.search:
        results = db.find_by_name(args.search)
        print(f"\nFound {len(results)} results for '{args.search}':")
        for dlc in results:
            print(f"  App ID {dlc['app_id']}: {dlc['artist']} - {dlc['song']}")
            print(f"    Content ID: {db.generate_content_id(dlc)}")
    
    if args.list:
        print(f"\nCached DLC ({len(db.dlc_data)} entries):")
        for app_id, dlc in sorted(db.dlc_data.items(), key=lambda x: x[1].get('name', '')):
            print(f"  {app_id}: {dlc.get('artist', 'Unknown')} - {dlc.get('song', 'Unknown')}")
    
    if args.export:
        db.export_to_json(Path(args.export))
    
    if args.import_file:
        db.import_from_json(Path(args.import_file))

if __name__ == '__main__':
    main()
