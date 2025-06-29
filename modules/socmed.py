import requests
import json
from modules.logging import setup_logging
from modules.headers import instagram_headers
from colorama import Fore, init

init(autoreset=True)

class SOCMED:
    def __init__(self, logger=None):
        self.input = None
        self.output = None
        self.session = requests.Session()
        self.logger = logger or setup_logging("SOCMED")
    
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
                result = f"{Fore.RED}[+] {Fore.WHITE}https://www.instagram.com/{self.input} {Fore.RED}- {Fore.YELLOW}TITLE NOT FOUND!"
                data = {"username": self.input, "found": False, "url": f"https://www.instagram.com/{self.input}"}
            else:
                title = response.text[title_start+7:title_end].strip()
                
                if (f"&#064;{self.input})" in title and 
                    "Instagram photos and videos" in title):
                    result = f"{Fore.RED}[+] {Fore.WHITE}https://www.instagram.com/{self.input} {Fore.RED}- {Fore.GREEN}FOUND!{Fore.RESET}"
                    data = {"username": self.input, "found": True, "url": f"https://www.instagram.com/{self.input}"}
                elif title == "Instagram":
                    result = f"{Fore.RED}[+] {Fore.WHITE}https://www.instagram.com/{self.input} {Fore.RED}- {Fore.RED}NOT FOUND!{Fore.RESET}"
                    data = {"username": self.input, "found": False, "url": f"https://www.instagram.com/{self.input}"}
                else:
                    pass

            print(result)
            if self.output:
                with open(self.output, 'w') as f:
                    json.dump([data], f, indent=2)

        except Exception as e:
            self.logger.error(f"Error checking Instagram: {str(e)}")
            print(f"{Fore.RED}Error checking account: {self.input}")
            
    def facebook_checker(self):
        if not self.input:
            self.logger.error("No input specified")
            return

        try:
            response = self.session.get(f"https://www.facebook.com/{self.input}", headers=instagram_headers)
            if response.status_code == 200 and "userVanity" in response.text:
                result = f"{Fore.GREEN}[+] {Fore.WHITE}https://www.facebook.com/{self.input} {Fore.GREEN}- FOUND!{Fore.RESET}"
                data = {"username": self.input, "found": True, "url": f"https://www.facebook.com/{self.input}"}
            elif "userVanity" not in response.text:
                result = f"{Fore.RED}[+] {Fore.WHITE}https://www.facebook.com/{self.input} {Fore.RED}- NOT FOUND!{Fore.RESET}"
                data = {"username": self.input, "found": False, "url": f"https://www.facebook.com/{self.input}"}
            else:
                pass

            print(result)
            if self.output:
                with open(self.output, 'w') as f:
                    json.dump([data], f, indent=2)

        except Exception as e:
            self.logger.error(f"Error checking Facebook: {str(e)}")
            print(f"{Fore.RED}Error checking account: {self.input}")