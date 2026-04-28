import httpx
from bs4 import BeautifulSoup
from collections import Counter
import re
from typing import Dict, List


def fetch_and_parse_url(url: str) -> str:
    """Загружает страницу и извлекает текст"""
    try:
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Удаляем скрипты и стили
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        return text
    except Exception as e:
        raise Exception(f"Failed to fetch URL {url}: {str(e)}")


def get_word_stats(text: str, top_n: int = 10) -> Dict[str, int]:
    """Анализирует текст и возвращает топ-N слов"""
    # Приводим к нижнему регистру и извлекаем слова
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Исключаем короткие слова и считаем частоту
    word_counts = Counter(word for word in words if len(word) > 1)
    
    # Возвращаем топ-N слов
    return dict(word_counts.most_common(top_n))


def validate_word_stats_payload(payload: dict) -> str:
    """Валидирует payload для задачи WORD_STATS"""
    if not payload:
        raise ValueError("WORD_STATS requires payload")
    
    if "url" not in payload:
        raise ValueError("WORD_STATS requires url in payload")
    
    url = payload["url"]
    if not url or not isinstance(url, str):
        raise ValueError("WORD_STATS requires valid url")
    
    return url
