from typing import Dict, List
from uuid import UUID


def validate_word_stats_compare_payload(payload: dict) -> tuple:
    """Валидирует payload для задачи WORD_STATS_COMPARE"""
    if not payload:
        raise ValueError("WORD_STATS_COMPARE requires payload")
    
    if "left_job_id" not in payload:
        raise ValueError("WORD_STATS_COMPARE requires left_job_id")
    
    if "right_job_id" not in payload:
        raise ValueError("WORD_STATS_COMPARE requires right_job_id")
    
    left_job_id = payload["left_job_id"]
    right_job_id = payload["right_job_id"]
    
    # Проверяем, что ID являются валидными UUID
    try:
        UUID(str(left_job_id))
    except (ValueError, AttributeError):
        raise ValueError("left_job_id must be a valid UUID")
    
    try:
        UUID(str(right_job_id))
    except (ValueError, AttributeError):
        raise ValueError("right_job_id must be a valid UUID")
    
    # Проверяем, что ID различаются
    if left_job_id == right_job_id:
        raise ValueError("left_job_id and right_job_id must be different")
    
    return left_job_id, right_job_id


def compare_word_stats(left_words: Dict[str, int], right_words: Dict[str, int]) -> Dict:
    """Сравнивает результаты двух задач WORD_STATS"""
    left_set = set(left_words.keys())
    right_set = set(right_words.keys())
    
    common_words = sorted(list(left_set & right_set))
    left_only = sorted(list(left_set - right_set))
    right_only = sorted(list(right_set - left_set))
    
    return {
        "common_words": common_words,
        "left_only": left_only,
        "right_only": right_only
    }
