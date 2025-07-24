import requests, json, re
from bs4 import BeautifulSoup
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
        platform_name = platform.upper()
        status_icon = f"{Fore.GREEN}✓" if found else f"{Fore.RED}✗"
        status_text = f"{status_icon} {Fore.RESET}{platform_name}"
        
        # Format URL for display
        display_url = url.replace("tiktok.com@", "tiktok.com/@") if "tiktok.com@" in url else url
        
        # Header with timestamp and status
        header = f"{Fore.LIGHTBLACK_EX}{self.start_time} {status_text}"
        
        # Username line
        username_line = f"{Fore.CYAN}@{self.input}"
        
        # URL line
        url_line = f"{Fore.LIGHTBLUE_EX}{display_url}"
        
        # Box drawing
        print(f"{Fore.LIGHTBLACK_EX}┌{'─' * 72}┐")
        print(f"{Fore.LIGHTBLACK_EX}│ {header:<86}{Fore.LIGHTBLACK_EX}│")
        print(f"{Fore.LIGHTBLACK_EX}├{'─' * 72}┤")
        print(f"{Fore.LIGHTBLACK_EX}│ {username_line:<76}{Fore.LIGHTBLACK_EX}│")
        print(f"{Fore.LIGHTBLACK_EX}│ {url_line:<76}{Fore.LIGHTBLACK_EX}│")
        
        # Stats section if available
        if found and stats:
            print(f"{Fore.LIGHTBLACK_EX}├{'─' * 72}┤")
            
            max_key_length = max(len(str(key)) for key in stats.keys())
            
            for key, value in stats.items():
                key_part = f"{Fore.LIGHTWHITE_EX}{key}:"
                value_part = f"{Fore.LIGHTGREEN_EX}{value}"
                stat_line = f"  {key_part:<{max_key_length + 2}}{value_part}"
                print(f"{Fore.LIGHTBLACK_EX}│ {stat_line:<81}{Fore.LIGHTBLACK_EX}│")
        
        print(f"{Fore.LIGHTBLACK_EX}└{'─' * 72}┘{Style.RESET_ALL}")
        print(".++" + "═" * 80 + "++.")

    def _save_result(self, data):
        if self.output:
            with open(self.output, 'a', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                f.write("\n")

# =============================================================== [INSTAGRAM] =============================================================== #

    def instagram_checker(self):
        if not self.input:
            self.logger.error("No input specified")
            return

        try:
            profile_url = f"https://www.instagram.com/{self.input}"
            response = self.session.get(profile_url, headers=instagram_headers)

            soup = BeautifulSoup(response.text, 'html.parser')
            og_desc = soup.find("meta", {"property": "og:description"})

            if og_desc:
                og_content = og_desc.get("content", "").strip()

                # Check if it matches this profile
                if f"@{self.input}" in og_content or f"&#064;{self.input}" in og_content:
                    import re
                    match = re.search(r"([\d,\.]+)\s+Followers,\s+([\d,\.]+)\s+Following,\s+([\d,\.]+)\s+Posts", og_content)
                    if match:
                        followers, following, posts = match.groups()
                    else:
                        followers = following = posts = "0"

                    stats = {
                        "Followers": followers,
                        "Following": following,
                        "Posts": posts
                    }

                    data = {
                        "platform": "instagram",
                        "username": self.input,
                        "found": True,
                        "url": profile_url,
                        "stats": stats
                    }
                    self._print_result_box("instagram", True, profile_url, stats)
                    self._save_result(data)
                    return  # Done, early return

            # fallback to old title-based check
            title_start = response.text.find('<title>')
            title_end = response.text.find('</title>')

            if title_start == -1 or title_end == -1:
                data = {
                    "platform": "instagram",
                    "username": self.input,
                    "found": False,
                    "url": profile_url
                }
                self._print_result_box("instagram", False, profile_url)
            else:
                title = response.text[title_start + 7:title_end].strip()
                if (f"@{self.input})" in title or f"&#064;{self.input})" in title) and "Instagram photos and videos" in title:
                    data = {
                        "platform": "instagram",
                        "username": self.input,
                        "found": True,
                        "url": profile_url
                    }
                    self._print_result_box("instagram", True, profile_url)
                else:
                    data = {
                        "platform": "instagram",
                        "username": self.input,
                        "found": False,
                        "url": profile_url
                    }
                    self._print_result_box("instagram", False, profile_url)

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

    def x_checker(self):
        if not self.input:
            self.logger.error("No input specified")
            return

        try:
            params = {
                'variables': '{"screen_name":"hwnzri"}',
                'features': '{"responsive_web_grok_bio_auto_translation_is_enabled":false,"hidden_profile_subscriptions_enabled":true,"payments_enabled":false,"profile_label_improvements_pcf_label_in_post_enabled":true,"rweb_tipjar_consumption_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_is_identity_verified_enabled":true,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"responsive_web_twitter_article_notes_tab_enabled":true,"subscriptions_feature_can_gift_premium":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}',
                'fieldToggles': '{"withAuxiliaryUserLabels":true}',
            }
            response = self.session.get('https://api.x.com/graphql/x3RLKWW1Tl7JgU7YtGxuzw/UserByScreenName',params=params,headers=x_headers)
            if response.status_code == 200:
                data = response.json()
                username = data["data"]["user"]["result"]["core"]["screen_name"]
                name = data["data"]["user"]["result"]["core"]["name"]
                following = data["data"]["user"]["result"]["legacy"]["friends_count"]
                follower = data["data"]["user"]["result"]["legacy"]["followers_count"]
                
                stats = {
                    "Username": username + " (" + name + ")",
                    "Followers": follower,
                    "Following": following,
                }

                data = {
                    "platform": "X",
                    "username": self.input,
                    "found": True,
                    "url": f"https://x.com/{self.input}",
                    "stats": stats
                }
                self._print_result_box("X", True, data['url'], stats)
            else:
                data = {
                    "platform": "X",
                    "username": self.input,
                    "found": False,
                    "url": f"https://x.com/{self.input}"
                }
                self._print_result_box("X", False, data['url'])
            self._save_result(data)

        except Exception as e:
            self.logger.error(f"Error checking X: {str(e)}")
            print(f"{Fore.RED}ERROR: {Fore.WHITE}Failed to check X account: @{self.input}")
            
# =============================================================== [TELEGRAM] =============================================================== #

    def telegram_checker(self):
        if not self.input:
            self.logger.error("No input specified")
            return

        try:
            response = self.session.get(f'https://telegram.me/{self.input}', headers=telegram_headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            og_title_tag = soup.find('meta', {'property': 'og:title'})
            og_description_tag = soup.find('meta', {'property': 'og:description'})
            twitter_image_tag = soup.find('meta', {'property': 'twitter:image'})

            og_title = og_title_tag['content'] if og_title_tag and 'content' in og_title_tag.attrs else None
            og_description = og_description_tag['content'] if og_description_tag and 'content' in og_description_tag.attrs else None
            twitter_image = twitter_image_tag['content'] if twitter_image_tag and 'content' in twitter_image_tag.attrs else None

            if og_title and og_description and twitter_image:
                stats = {
                    "Name": og_title,
                    "Desc": og_description,
                    "Image": twitter_image
                }
                data = {
                    "platform": "Telegram",
                    "username": self.input,
                    "found": True,
                    "url": f"https://t.me/{self.input}",
                    "stats": stats
                }
                self._print_result_box("Telegram", True, data['url'], stats)
            else:
                data = {
                    "platform": "Telegram",
                    "username": self.input,
                    "found": False,
                    "url": f"https://t.me/{self.input}"
                }
                self._print_result_box("Telegram", False, data['url'])

            self._save_result(data)

        except Exception as e:
            self.logger.error(f"Error checking Telegram: {str(e)}")
            print(f"{Fore.RED}ERROR: {Fore.WHITE}Failed to check Telegram account: @{self.input}")
            
# =============================================================== [LEMON8] =============================================================== #

    def lemon8_checker(self):
        if not self.input:
            self.logger.error("No input specified")
            return

        try:
            response = self.session.get(
                f"https://www.lemon8-app.com/@{self.input}",
                headers=lemon8_headers,
                allow_redirects=False
            )

            soup = BeautifulSoup(response.text, 'html.parser')
            profile_container = soup.find('div', class_='user-desc-main')

            if response.status_code == 200 and profile_container:
                display_name_tag = soup.find('h1', class_='user-desc-base-name')
                display_name = display_name_tag.get_text(strip=True) if display_name_tag else "Unknown"

                following = followers = likes_saves = "0"
                stats_items = soup.find_all('a', class_='user-desc-main-info-item')

                for item in stats_items:
                    spans = item.find_all('span')
                    if len(spans) >= 2:
                        value = spans[0].get_text(strip=True)
                        label = spans[1].get_text(strip=True).lower()

                        if 'mengikuti' in label or 'following' in label:
                            following = value
                        elif 'pengikut' in label or 'followers' in label:
                            followers = value
                        elif 'suka dan simpanan' in label or 'likes and saves' in label:
                            likes_saves = value

                stats = {
                    "Name": display_name,
                    "Following": following,
                    "Followers": followers,
                    "Likes/Saves": likes_saves
                }

                data = {
                    "platform": "lemon8",
                    "username": self.input,
                    "found": True,
                    "url": f"https://www.lemon8-app.com/@{self.input}",
                    "stats": stats
                }

                self._print_result_box("lemon8", True, data['url'], stats)
            else:
                data = {
                    "platform": "lemon8",
                    "username": self.input,
                    "found": False,
                    "url": f"https://www.lemon8-app.com/@{self.input}"
                }
                self._print_result_box("lemon8", False, data['url'])

            self._save_result(data)

        except Exception as e:
            self.logger.error(f"Error checking Lemon8: {str(e)}")
            print(f"{Fore.RED}ERROR: {Fore.WHITE}Failed to check Lemon8 account: @{self.input}")
            
            
    def threads_checker(self):
        if not self.input:
            self.logger.error("No input specified")
            return

        url = f"https://www.threads.com/@{self.input}"
        try:
            resp = self.session.get(url, headers=threads_headers, allow_redirects=False)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            profile = soup.find('div', class_='user-desc-main')
            if profile:
                title_tag = profile.find('h1', class_='user-desc-base-name')
                title     = title_tag.get_text(strip=True) if title_tag else self.input
                followers = (
                    profile.find('span', attrs={'title': re.compile(r'^\d')})
                    .get('title', '0')
                )
            else:
                # twitter:description meta fallback
                meta = soup.find('meta', attrs={'name': 'twitter:description'})
                if meta and meta.has_attr('content'):
                    desc = meta['content']
                    m = re.search(r'(?P<followers>\d+)\s+Followers', desc, re.IGNORECASE)
                    followers = m.group('followers') if m else "0"
                else:
                    span = soup.find('span', title=re.compile(r'^\d+'))
                    sib  = span.find_next_sibling(string=re.compile(r'followers?', re.IGNORECASE)) if span else None
                    if span and sib:
                        followers = span['title']
                    else:
                        raise ValueError("Could not find followers count")

                # page-title fallback
                page_title = soup.find('title').get_text(strip=True)
                title = re.split(r'\s*\(@', page_title, 1)[0]

            # **STRIP ANY “ • …” SUFFIX FROM TITLE**
            title = re.sub(r'\s*•.*$', '', title)

            stats = {
                "Title": title,
                "Followers": followers,
            }
            data = {
                "platform": "threads",
                "username": self.input,
                "found": True,
                "url": url,
                "stats": stats
            }

            self._print_result_box("threads", True, url, stats)
            self._save_result(data)

        except Exception as e:
            self.logger.error(f"Error checking threads: {e}")
            print(f"{Fore.RED}ERROR: {Fore.WHITE}Failed to check threads account: @{self.input}")