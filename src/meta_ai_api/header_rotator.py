import random
from typing import Dict


class HeaderRotator:
    """
    A class to dynamically rotate HTTP headers to bypass rate limiting and avoid detection.
    Provides randomized user agents, referers, and other headers to prevent rate limiting.
    """

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    ]

    ACCEPT_LANGUAGES = [
        "en-US,en;q=0.9",
        "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7",
        "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7",
        "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7",
        "en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7",
        "en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7",
        "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
    ]

    ACCEPT_ENCODINGS = [
        "gzip, deflate, br",
        "gzip, deflate",
        "gzip",
    ]

    SEC_CH_UA_PLATFORMS = [
        '"Windows"',
        '"macOS"',
        '"Linux"',
    ]

    def __init__(self):
        """Initialize the HeaderRotator."""
        self.rotation_index = 0

    def get_headers(self) -> Dict[str, str]:
        """
        Generate randomized headers for HTTP requests.

        Returns:
            Dict[str, str]: A dictionary of HTTP headers with randomized values.
        """
        user_agent = random.choice(self.USER_AGENTS)
        accept_language = random.choice(self.ACCEPT_LANGUAGES)
        accept_encoding = random.choice(self.ACCEPT_ENCODINGS)
        sec_ch_ua_platform = random.choice(self.SEC_CH_UA_PLATFORMS)

        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": accept_language,
            "Accept-Encoding": accept_encoding,
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua-Platform": sec_ch_ua_platform,
            "Sec-Ch-Ua-Mobile": "?0",
            "Pragma": "no-cache",
        }

        return headers

    def get_mobile_headers(self) -> Dict[str, str]:
        """
        Generate randomized headers for mobile HTTP requests.

        Returns:
            Dict[str, str]: A dictionary of mobile HTTP headers.
        """
        mobile_user_agents = [
            "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
        ]

        user_agent = random.choice(mobile_user_agents)
        accept_language = random.choice(self.ACCEPT_LANGUAGES)

        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": accept_language,
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }

        return headers