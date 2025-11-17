"""
Scrapers Configuration Module

Loads configuration from environment variables for web scrapers.
"""

import os
from typing import Optional
from pathlib import Path


class ScrapersConfig:
    """Configuration for web scrapers loaded from environment variables."""

    def __init__(self):
        """Initialize configuration from environment variables."""

        # Selenium Configuration
        self.use_selenium = self._get_bool('SCRAPERS_USE_SELENIUM', True)
        self.headless = self._get_bool('SCRAPERS_HEADLESS', True)

        # Proxy Configuration
        self.use_proxy = self._get_bool('SCRAPERS_USE_PROXY', False)
        self.proxy_url = os.getenv('SCRAPERS_PROXY_URL', '').strip()

        # If proxy is enabled but no URL provided, try HTTP_PROXY env var
        if self.use_proxy and not self.proxy_url:
            self.proxy_url = (
                os.getenv('HTTP_PROXY') or
                os.getenv('http_proxy') or
                os.getenv('HTTPS_PROXY') or
                os.getenv('https_proxy') or
                ''
            )

        # Rate Limiting
        self.delay_between_requests = float(
            os.getenv('SCRAPERS_DELAY_BETWEEN_REQUESTS', '1.5')
        )

        # Output Configuration
        self.output_dir = os.getenv(
            'SCRAPERS_OUTPUT_DIR',
            'data/knowledge_base/genetec'
        )

        # Browser Configuration
        self.chrome_binary_path = os.getenv('SCRAPERS_CHROME_BINARY_PATH', '').strip()
        self.chromedriver_path = os.getenv('SCRAPERS_CHROMEDRIVER_PATH', '').strip()

    @staticmethod
    def _get_bool(key: str, default: bool = False) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, '').lower().strip()
        if not value:
            return default
        return value in ('true', '1', 'yes', 'on', 'enabled')

    def get_proxy_config(self) -> Optional[str]:
        """
        Get proxy configuration if enabled.

        Returns:
            Proxy URL string if proxy is enabled and configured, None otherwise.
        """
        if self.use_proxy and self.proxy_url:
            return self.proxy_url
        return None

    def get_selenium_options_dict(self) -> dict:
        """
        Get Selenium configuration as dictionary.

        Returns:
            Dictionary with Selenium options for use in scrapers.
        """
        return {
            'use_selenium': self.use_selenium,
            'headless': self.headless,
            'proxy_url': self.get_proxy_config(),
            'chrome_binary': self.chrome_binary_path or None,
            'chromedriver_path': self.chromedriver_path or None,
        }

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate delay
        if self.delay_between_requests < 0:
            errors.append("SCRAPERS_DELAY_BETWEEN_REQUESTS must be >= 0")

        # Validate proxy URL format if provided
        if self.use_proxy and self.proxy_url:
            if not (self.proxy_url.startswith('http://') or
                    self.proxy_url.startswith('https://')):
                errors.append(
                    f"SCRAPERS_PROXY_URL must start with http:// or https://, "
                    f"got: {self.proxy_url[:50]}"
                )

        # Validate Chrome paths if provided
        if self.chrome_binary_path:
            if not Path(self.chrome_binary_path).exists():
                errors.append(
                    f"SCRAPERS_CHROME_BINARY_PATH does not exist: "
                    f"{self.chrome_binary_path}"
                )

        if self.chromedriver_path:
            if not Path(self.chromedriver_path).exists():
                errors.append(
                    f"SCRAPERS_CHROMEDRIVER_PATH does not exist: "
                    f"{self.chromedriver_path}"
                )

        return len(errors) == 0, errors

    def print_config(self):
        """Print current configuration (useful for debugging)."""
        print("=" * 70)
        print("SCRAPERS CONFIGURATION")
        print("=" * 70)
        print(f"Selenium:")
        print(f"  Use Selenium: {self.use_selenium}")
        print(f"  Headless: {self.headless}")
        print(f"  Chrome Binary: {self.chrome_binary_path or '(auto-detect)'}")
        print(f"  ChromeDriver: {self.chromedriver_path or '(auto-detect)'}")
        print()
        print(f"Proxy:")
        print(f"  Use Proxy: {self.use_proxy}")
        if self.use_proxy:
            if self.proxy_url:
                # Mask sensitive parts of proxy URL
                masked_url = self.proxy_url[:50] + "..." if len(self.proxy_url) > 50 else self.proxy_url
                print(f"  Proxy URL: {masked_url}")
            else:
                print(f"  Proxy URL: (not configured)")
        print()
        print(f"Rate Limiting:")
        print(f"  Delay Between Requests: {self.delay_between_requests}s")
        print()
        print(f"Output:")
        print(f"  Output Directory: {self.output_dir}")
        print("=" * 70)


# Global instance for easy import
_config_instance: Optional[ScrapersConfig] = None


def get_config() -> ScrapersConfig:
    """
    Get global configuration instance (singleton pattern).

    Returns:
        ScrapersConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ScrapersConfig()
    return _config_instance


def reload_config():
    """Reload configuration from environment (useful for testing)."""
    global _config_instance
    _config_instance = ScrapersConfig()
    return _config_instance
