import json
import os
from pathlib import Path
from threading import Lock

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
    except Exception:
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
        try:
            return value.format(**kwargs)
        except KeyError:
            return value

    return value


def translate_content_list(items, key_prefix):
    return [t(f"{key_prefix}.{item}") for item in items]
from pathlib import Path

_i18n_cache = {}


def _load_translations(lang):
    if lang in _i18n_cache:
        return _i18n_cache[lang]

    i18n_dir = Path(__file__).resolve().parent.parent / "i18n"
    file_path = i18n_dir / f"{lang}.json"

    if not file_path.exists():
        file_path = i18n_dir / "en.json"
        lang = "en"

    with open(file_path, "r", encoding="utf-8") as f:
        translations = json.load(f)

    _i18n_cache[lang] = translations
    return translations


def _load_en():
    if "en" not in _i18n_cache:
        _i18n_cache["en"] = _load_translations("en")
    return _i18n_cache["en"]


def init_i18n(lang="en"):
    import streamlit as st
    current = st.session_state.get("language")
    translations = st.session_state.get("translations")
    if current != lang or translations is None:
        st.session_state["translations"] = _load_translations(lang)
        st.session_state["language"] = lang


def t(key, **kwargs):
    import streamlit as st
    translations = st.session_state.get("translations")
    if translations is None:
        translations = _load_translations("en")
    value = translations.get(key)
    if value is None:
        en = _load_en()
        value = en.get(key, key)
    if kwargs:
        value = value.format(**kwargs)
    return value


def available_languages():
    i18n_dir = Path(__file__).resolve().parent.parent / "i18n"
    files = list(i18n_dir.glob("*.json"))
    langs = []
    for f in sorted(files):
        code = f.stem
        names = {"en": "English", "hi": "हिन्दी", "te": "తెలుగు"}
        langs.append({"code": code, "name": names.get(code, code)})
    return langs
