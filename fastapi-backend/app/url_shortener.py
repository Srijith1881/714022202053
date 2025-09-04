from typing import Dict, Optional
import os
import json
import secrets
import string
from urllib.parse import urlparse
from pathlib import Path
from threading import RLock


DEFAULT_STORE_PATH = os.getenv("URL_STORE_PATH", "./data/url_store.json")


class InMemoryUrlStore:
    def __init__(self, store_path: str = DEFAULT_STORE_PATH) -> None:
        self.code_to_url: Dict[str, str] = {}
        self.url_to_code: Dict[str, str] = {}
        self._store_path = Path(store_path)
        self._lock = RLock()
        self._ensure_parent_dir()
        self._load_from_disk()

    def _ensure_parent_dir(self) -> None:
        self._store_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_from_disk(self) -> None:
        if not self._store_path.exists():
            return
        try:
            with self._store_path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, dict) and "code_to_url" in data:
                    self.code_to_url = dict(data.get("code_to_url", {}))
                    # rebuild reverse index
                    self.url_to_code = {v: k for k, v in self.code_to_url.items()}
        except Exception:
            # Corrupt or unreadable file: ignore and start fresh in-memory
            self.code_to_url = {}
            self.url_to_code = {}

    def _save_to_disk(self) -> None:
        tmp_path = self._store_path.with_suffix(".json.tmp")
        content = {
            "code_to_url": self.code_to_url,
        }
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(content, fh, ensure_ascii=False, indent=2)
        tmp_path.replace(self._store_path)

    def get_url(self, code: str) -> Optional[str]:
        with self._lock:
            return self.code_to_url.get(code)

    def get_or_create_code(self, url: str, code_len: int = 7) -> str:
        with self._lock:
            if url in self.url_to_code:
                return self.url_to_code[url]
            code = self._generate_code(code_len)
            while code in self.code_to_url:
                code = self._generate_code(code_len)
            self.code_to_url[code] = url
            self.url_to_code[url] = code
            self._save_to_disk()
            return code

    def _generate_code(self, length: int) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))


store = InMemoryUrlStore()


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False 