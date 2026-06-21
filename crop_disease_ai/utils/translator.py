import json
import re
from pathlib import Path
from threading import Lock

_float_re = re.compile(r"(?<!\{)\{([^{}]+):(\.\d+[fFeEgGxXoO])\}(?!\})")


def _decimal_format(value, fmt):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return format(number, fmt)


_i18n_dir = Path(__file__).resolve().parent.parent / "i18n"
_translations = {}
_current_lang = "en"
_lock = Lock()
_supported_languages = ["en", "hi", "te"]


def get_supported_languages():
    return _supported_languages.copy()


def load_translations(lang):
    global _translations, _current_lang
    lang = lang if lang in _supported_languages else "en"
    file_path = _i18n_dir / f"{lang}.json"
    try:
        with open(str(file_path), "r", encoding="utf-8") as f:
            with _lock:
                _translations = json.load(f)
                _current_lang = lang
    except (FileNotFoundError, json.JSONDecodeError):
        en_path = _i18n_dir / "en.json"
        try:
            with open(str(en_path), "r", encoding="utf-8") as f:
                with _lock:
                    _translations = json.load(f)
                    _current_lang = "en"
        except (FileNotFoundError, json.JSONDecodeError):
            with _lock:
                _translations = {}
                _current_lang = "en"


def _ensure_loaded():
    if not _translations:
        load_translations("en")


def t(key, **kwargs):
    _ensure_loaded()
    try:
        import streamlit as st

        lang = st.session_state.get("language", "en")
        if lang != _current_lang:
            load_translations(lang)
    except Exception:  # nosec
        pass

    with _lock:
        value = _translations.get(key)

    if value is None:
        en_path = _i18n_dir / "en.json"
        try:
            with open(str(en_path), "r", encoding="utf-8") as f:
                en_translations = json.load(f)
            value = en_translations.get(key, key)
        except Exception:
            value = key

    if kwargs and isinstance(value, str):

        def replace_match(m):
            key = m.group(1)
            if key in kwargs:
                return _decimal_format(kwargs[key], m.group(2))
            return m.group(0)

        processed = _float_re.sub(replace_match, value)
        try:
            return processed.format(**kwargs)
        except (KeyError, ValueError):
            return processed

    return value


def translate_content_list(items, key_prefix):
    return [t(f"{key_prefix}.{item}") for item in items]


def available_languages():
    file_paths = list(_i18n_dir.glob("*.json"))
    langs = []
    for f in sorted(file_paths):
        code = f.stem
        names = {"en": "English", "hi": "हिन्दी", "te": "తెలుగు"}
        langs.append({"code": code, "name": names.get(code, code)})
    return langs


def _load_translations(lang):
    if lang not in _supported_languages:
        lang = "en"
    file_path = _i18n_dir / f"{lang}.json"
    if not file_path.exists():
        file_path = _i18n_dir / "en.json"
        lang = "en"
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def init_i18n(lang="en"):
    import streamlit as st

    current = st.session_state.get("language")
    translations = st.session_state.get("translations")
    if current != lang or translations is None:
        st.session_state["translations"] = _load_translations(lang)
        st.session_state["language"] = lang
