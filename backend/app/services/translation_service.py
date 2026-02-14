import json
import re
from urllib import error, parse, request


class TranslationService:
    GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
    _EN_LAYOUT = "`qwertyuiop[]asdfghjkl;'zxcvbnm,./"
    _RU_LAYOUT = "ёйцукенгшщзхъфывапролджэячсмитьбю."
    _EN_TO_RU_LAYOUT_MAP = str.maketrans(_EN_LAYOUT + _EN_LAYOUT.upper(), _RU_LAYOUT + _RU_LAYOUT.upper())
    _RU_TO_EN_LAYOUT_MAP = str.maketrans(_RU_LAYOUT + _RU_LAYOUT.upper(), _EN_LAYOUT + _EN_LAYOUT.upper())

    @staticmethod
    def _contains_cyrillic(text: str) -> bool:
        return bool(re.search(r"[\u0400-\u04FF]", text or ""))

    @staticmethod
    def _contains_latin(text: str) -> bool:
        return bool(re.search(r"[A-Za-z]", text or ""))

    @classmethod
    def _keyboard_layout_fallback(cls, text: str, *, to_ru: bool) -> str:
        value = (text or "").strip()
        if not value:
            return value
        mapped = value.translate(cls._EN_TO_RU_LAYOUT_MAP if to_ru else cls._RU_TO_EN_LAYOUT_MAP)
        return mapped.strip() or value

    @classmethod
    def translate_text(cls, text: str, target_lang: str, source_lang: str = "auto") -> str:
        source = (source_lang or "auto").strip() or "auto"
        target = (target_lang or "").strip().lower()
        content = (text or "").strip()

        if not content or not target:
            return content
        if source == target:
            return content

        query = parse.urlencode(
            {
                "client": "gtx",
                "sl": source,
                "tl": target,
                "dt": "t",
                "q": content,
            }
        )
        url = f"{cls.GOOGLE_TRANSLATE_URL}?{query}"

        try:
            with request.urlopen(url, timeout=8) as response:
                body = response.read().decode("utf-8")
                payload = json.loads(body)
        except (error.URLError, error.HTTPError, TimeoutError, ValueError):
            return content

        try:
            chunks = payload[0]
            translated = "".join(chunk[0] for chunk in chunks if isinstance(chunk, list) and chunk and chunk[0])
            return translated.strip() or content
        except (TypeError, IndexError, KeyError):
            return content

    @classmethod
    def build_ru_en(cls, text: str | None) -> tuple[str | None, str | None]:
        value = (text or "").strip()
        if not value:
            return None, None

        if cls._contains_cyrillic(value):
            ru = value
            en = cls.translate_text(value, target_lang="en", source_lang="ru")
            if (en or "").strip().lower() == value.lower():
                en = cls._keyboard_layout_fallback(value, to_ru=False)
            return ru or value, en or value

        en = value
        ru = cls.translate_text(value, target_lang="ru", source_lang="en")
        if cls._contains_latin(value) and (ru or "").strip().lower() == value.lower():
            ru = cls._keyboard_layout_fallback(value, to_ru=True)
        return ru or value, en or value

