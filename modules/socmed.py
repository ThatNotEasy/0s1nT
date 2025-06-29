import requests, json, re
from modules.logging import setup_logging
from modules.headers import *
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

class SOCMED:
    def __init__(self, logger=None):
        self.input = None
        self.output = None
        self.session = requests.Session()
        self.logger = logger or setup_logging("SOCMED")
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.colors = {
            'border': Fore.YELLOW,
            'title': Fore.CYAN,
            'text': Fore.WHITE,
            'url': Fore.LIGHTBLUE_EX,
            'found': Fore.GREEN,
            'not_found': Fore.RED,
            'stats_key': Fore.LIGHTWHITE_EX,
            'stats_value': Fore.LIGHTGREEN_EX,
            'error': Fore.LIGHTRED_EX
        }

    def _print_result_box(self, platform, found, url, stats=None):
        # Fix header typo and ensure consistent capitalization
        platform_name = platform.upper()
        if platform_name == "TIKIOK":  # Fix typo in platform name
            platform_name = "TIKTOK"
            
        print(f"\n{self.colors['border']}╔{'═'*46}╗")
        print(f"║{self.colors['title']}{'SOCIAL MEDIA CHECKER':^46}{self.colors['border']}║")  # Fixed "SQLTAL" typo
        print(f"║{self.colors['text']}{f'Platform: {platform_name}':^46}{self.colors['border']}║")
        print(f"║{self.colors['text']}{f'Username: {self.input}':^46}{self.colors['border']}║")
        print(f"║{self.colors['text']}{f'Started: {self.start_time}':^46}{self.colors['border']}║")
        print(f"║{' '*46}║")
        
        # Fix URL formatting (TikTok was missing / after domain)
        display_url = url.replace("tiktok.com@", "tiktok.com/@") if "tiktok.com@" in url else url
        display_url = display_url if len(display_url) <= 40 else display_url[:37] + "..."
        print(f"║ {self.colors['text']}URL: {self.colors['url']}{display_url.ljust(39)} {self.colors['border']}║")
        
        # Status line with consistent spacing
        status_color = self.colors['found'] if found else self.colors['not_found']
        status_text = "FOUND" if found else "NOT FOUND"
        print(f"║ {self.colors['text']}Status: {status_color}{status_text.ljust(36)} {self.colors['border']}║")
        
        # Stats section with fixed alignment
        if found and stats:
            print(f"║{' '*46}║")
            for key, value in stats.items():
                # Fixed extra space in "Username :" and aligned properly
                print(f"║ {self.colors['stats_key']}{key.title():<10}: "
                      f"{self.colors['stats_value']}{str(value).ljust(32)} {self.colors['border']}║")
        
        print(f"╚{'═'*46}╝{Style.RESET_ALL}\n")

    def _save_result(self, data):
        if self.output:
            with open(self.output, 'a') as f:
                json.dump(data, f, indent=2)
                f.write("\n")

# =============================================================== [INSTAGRAM] =============================================================== #

    def instagram_checker(self):
        if not self.input:
            self.logger.error("No input specified")
            return

        try:
            response = self.session.get(
                f"https://www.instagram.com/{self.input}",
                headers=instagram_headers
            )
            
            title_start = response.text.find('<title>')
            title_end = response.text.find('</title>')
            
            if title_start == -1 or title_end == -1:
                data = {"platform": "instagram", "username": self.input, "found": False, "url": f"https://www.instagram.com/{self.input}"}
                self._print_result_box("instagram", False, data['url'])
            else:
                title = response.text[title_start+7:title_end].strip()
                
                if (f"&#064;{self.input})" in title and "Instagram photos and videos" in title):
                    data = {
                        "platform": "instagram",
                        "username": self.input,
                        "found": True,
                        "url": f"https://www.instagram.com/{self.input}"
                    }
                    self._print_result_box("instagram", True, data['url'])
                else:
                    data = {"platform": "instagram", "username": self.input, "found": False, "url": f"https://www.instagram.com/{self.input}"}
                    self._print_result_box("instagram", False, data['url'])

            self._save_result(data)

        except Exception as e:
            self.logger.error(f"Error checking Instagram: {str(e)}")
            print(f"{Fore.RED}ERROR: {Fore.WHITE}Failed to check Instagram account: @{self.input}")

# =============================================================== [FACEBOOK] =============================================================== #

    def facebook_checker(self):
        if not self.input:
            self.logger.error("No input specified")
            return

        try:
            response = self.session.get(
                f"https://www.facebook.com/{self.input}", 
                headers=facebook_headers,
                allow_redirects=False
            )
            
            if response.status_code == 200 and "userVanity" in response.text:
                name_match = re.search(r'"name":"([^"]+)"', response.text)
                profile_name = name_match.group(1) if name_match else "Unknown"
                
                data = {
                    "platform": "facebook",
                    "username": self.input,
                    "found": True,
                    "url": f"https://www.facebook.com/{self.input}",
                    "stats": {
                        "name": profile_name,
                        "vanity": "Available"
                    }
                }
                self._print_result_box("facebook", True, data['url'], {
                    "Profile Name": profile_name,
                    "Vanity URL": "✔️ Available"
                })
                
            elif response.status_code == 200 and "content=\"profile\"" in response.text:
                data = {
                    "platform": "facebook",
                    "username": self.input,
                    "found": True,
                    "url": f"https://www.facebook.com/{self.input}"
                }
                self._print_result_box("facebook", True, data['url'])
                
            else:
                data = {
                    "platform": "facebook",
                    "username": self.input,
                    "found": False,
                    "url": f"https://www.facebook.com/{self.input}"
                }
                self._print_result_box("facebook", False, data['url'])

            self._save_result(data)

        except Exception as e:
            self.logger.error(f"Error checking Facebook: {str(e)}")
            print(f"{Fore.RED}ERROR: {Fore.WHITE}Failed to check Facebook account: {self.input}")

# =============================================================== [TIKTOK] =============================================================== #

    def tiktok_checker(self):
        if not self.input:
            self.logger.error("No input specified")
            return

        try:
            response = self.session.get(f"https://www.tiktok.com/@{self.input}", headers=tiktok_headers)
            pattern = r'"shareMeta":\s*\{\s*"title":\s*"([^"]+)",\s*"desc":\s*"([^"]+)"\s*\}'
            match = re.search(pattern, response.text)

            if match:
                desc = match.group(2)
                
                username_match = re.search(r'@([^\s]+)', desc)
                followers_match = re.search(r'([\d.]+[kKmM]?)\sFollowers', desc)
                following_match = re.search(r'([\d.]+[kKmM]?)\sFollowing', desc)
                likes_match = re.search(r'([\d.]+[kKmM]?)\sLikes', desc)

                stats = {
                    "Username": username_match.group(0) if username_match else "@UNKNOWN",
                    "Followers": followers_match.group(1) if followers_match else "0",
                    "Following": following_match.group(1) if following_match else "0",
                    "Likes": likes_match.group(1) if likes_match else "0"
                }
                
                data = {
                    "platform": "tiktok",
                    "username": self.input,
                    "found": True,
                    "url": f"https://www.tiktok.com/@{self.input}",
                    "stats": stats
                }
                
                self._print_result_box("tiktok", True, data['url'], stats)
            else:
                data = {
                    "platform": "tiktok",
                    "username": self.input,
                    "found": False,
                    "url": f"https://www.tiktok.com/@{self.input}"
                }
                self._print_result_box("tiktok", False, data['url'])

            self._save_result(data)

        except Exception as e:
            self.logger.error(f"Error checking TikTok: {str(e)}")
            print(f"{Fore.RED}ERROR: {Fore.WHITE}Failed to check TikTok account: @{self.input}")

# =============================================================== [TWITTER/X] =============================================================== #

    def twitter_checker(self):
        if not self.input:
            self.logger.error("No input specified")
            return

        try:
            response = self.session.get(
                f"https://twitter.com/{self.input}",
                headers=tiktok_headers
            )
            
            if response.status_code == 200 and "data-screenname" in response.text:
                name_match = re.search(r'data-screenname="([^"]+)"', response.text)
                display_name_match = re.search(r'data-name="([^"]+)"', response.text)
                
                stats = {
                    "Handle": f"@{name_match.group(1)}" if name_match else "@UNKNOWN",
                    "Name": display_name_match.group(1) if display_name_match else "Unknown"
                }
                
                data = {
                    "platform": "twitter",
                    "username": self.input,
                    "found": True,
                    "url": f"https://twitter.com/{self.input}",
                    "stats": stats
                }
                self._print_result_box("twitter", True, data['url'], stats)
            else:
                data = {
                    "platform": "twitter",
                    "username": self.input,
                    "found": False,
                    "url": f"https://twitter.com/{self.input}"
                }
                self._print_result_box("twitter", False, data['url'])

            self._save_result(data)

        except Exception as e:
            self.logger.error(f"Error checking Twitter: {str(e)}")
            print(f"{Fore.RED}ERROR: {Fore.WHITE}Failed to check Twitter account: @{self.input}")