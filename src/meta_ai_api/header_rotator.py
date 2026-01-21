import random
import time
from typing import Dict, List
from datetime import datetime
import hashlib
import string


class HeaderRotator:
    """
    Generates dynamic, untraceable HTTP headers that rotate to avoid detection.
    Mimics realistic browser behavior with varying patterns.
    """

    # Real browser user agents with version variations
    USER_AGENTS = [
        # Chrome variants
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Firefox variants
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0",
        
        # Safari variants
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        
        # Edge variants
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    ]

    ACCEPT_LANGUAGES = [
        "en-US,en;q=0.9",
        "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7",
        "en;q=0.9,en-US;q=0.8",
        "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7",
        "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7",
    ]

    SEC_CH_UA_PLATFORMS = [
        '"Windows"',
        '"macOS"',
        '"Linux"',
    ]

    def __init__(self):
        self.request_count = 0
        self.last_ua = None
        self.ua_change_interval = random.randint(3, 15)  # Change UA every 3-15 requests

    def _get_random_ua(self) -> str:
        """Get a random user agent, avoiding consecutive duplicates."""
        ua = random.choice(self.USER_AGENTS)
        # Ensure we don't get the same UA twice in a row
        while ua == self.last_ua and len(self.USER_AGENTS) > 1:
            ua = random.choice(self.USER_AGENTS)
        self.last_ua = ua
        return ua

    def _extract_platform_from_ua(self, ua: str) -> str:
        """Extract platform from user agent string."""
        if "Windows" in ua:
            return '"Windows"'
        elif "Macintosh" in ua or "iPhone" in ua or "iPad" in ua:
            return '"macOS"'
        else:
            return '"Linux"'

    def _generate_sec_ch_ua(self, ua: str) -> str:
        """Generate sec-ch-ua header based on user agent."""
        if "Chrome" in ua and "Edg" not in ua:
            return '"Not_A Brand";v="8", "Chromium";v="122", "Google Chrome";v="122"'
        elif "Edg" in ua:
            return '"Not_A Brand";v="8", "Chromium";v="122", "Microsoft Edge";v="122"'
        elif "Firefox" in ua:
            return '"";v="122"'
        else:
            return '"Not_A Brand";v="8"'

    def _generate_fingerprint(self) -> Dict[str, str]:
        """Generate browser fingerprint components."""
        return {
            "dpr": str(random.choice([1, 1.5, 2, 2.5])),
            "viewport_width": str(random.choice([1920, 1440, 1366, 1280, 1024])),
            "viewport_height": str(random.choice([1080, 900, 768, 720, 600])),
            "timezone": random.choice(["UTC", "EST", "CST", "PST", "GMT"]),
        }

    def _add_timing_variance(self) -> Dict[str, str]:
        """Add realistic timing information to headers."""
        return {
            "request_id": self._generate_request_id(),
            "timestamp": str(int(time.time() * 1000)),  # milliseconds
        }

    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        timestamp_part = hex(int(time.time() * 1000))[2:]
        return f"{timestamp_part}-{random_part}"

    def get_headers(self, base_headers: Dict[str, str] = None) -> Dict[str, str]:
        """
        Generate a complete set of dynamic, untraceable headers.
        
        Args:
            base_headers (Dict): Optional base headers to merge with generated ones
            
        Returns:
            Dict: Complete header set with rotation
        """
        self.request_count += 1

        # Rotate user agent periodically
        if self.request_count % self.ua_change_interval == 0:
            self.ua_change_interval = random.randint(3, 15)

        ua = self._get_random_ua()
        platform = self._extract_platform_from_ua(ua)
        fingerprint = self._generate_fingerprint()
        timing = self._add_timing_variance()

        # Build header set
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": random.choice(self.ACCEPT_LANGUAGES),
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": self._generate_sec_ch_ua(ua),
            "Sec-Ch-Ua-Mobile": "?0" if "Mobile" not in ua else "?1",
            "Sec-Ch-Ua-Platform": platform,
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "DNT": random.choice(["1", "null"]),
            "Sec-Gpc": random.choice(["1", "null"]),
        }

        # Add fingerprint-based headers
        headers["X-Client-Version"] = f"v{random.randint(1, 10)}.{random.randint(0, 99)}"
        headers["X-Device-Memory"] = str(random.choice([4, 8, 16, 32]))
        headers["X-Dpr"] = fingerprint["dpr"]

        # Merge with base headers if provided
        if base_headers:
            headers.update(base_headers)

        return headers

    def get_dynamic_cookie_string(self, existing_cookies: Dict[str, str] = None) -> str:
        """
        Generate dynamic cookie header with realistic patterns.
        
        Args:
            existing_cookies (Dict): Existing cookies to preserve
            
        Returns:
            str: Cookie header string
        """
        cookies = existing_cookies or {}

        # Add dynamic tracking cookies
        cookies.update({
            "_gid": self._generate_request_id(),
            "_ga": f"GA1.2.{random.randint(100000000, 999999999)}.{int(time.time())}",
        })

        return "; ".join([f"{k}={v}" for k, v in cookies.items()])

    def rotate_headers_gradually(self, current_headers: Dict[str, str]) -> Dict[str, str]:
        """
        Gradually rotate some header values to appear more natural.
        Useful for long-lived sessions.
        
        Args:
            current_headers (Dict): Current headers to update
            
        Returns:
            Dict: Updated headers with some values rotated
        """
        updated = current_headers.copy()

        # Occasionally rotate certain headers
        if random.random() < 0.3:  # 30% chance
            updated["Accept-Language"] = random.choice(self.ACCEPT_LANGUAGES)
        
        if random.random() < 0.2:  # 20% chance
            updated["Sec-Fetch-Site"] = random.choice([
                "none", "same-origin", "cross-site", "same-site"
            ])

        return updated


# Global header rotator instance
_header_rotator = HeaderRotator()


def get_header_rotator() -> HeaderRotator:
    """Get the global header rotator instance."""
    return _header_rotator