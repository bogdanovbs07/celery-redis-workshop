from core.celery_app import celery_app
from core.database import SessionLocal
from repositories.job_repository import JobRepository
from models.job import JobStatus, JobType
from core.exceptions import PermanentJobError
from tasks.handlers.word_stats import (
    fetch_and_parse_url,
    get_word_stats,
    validate_word_stats_payload
)
from tasks.handlers.word_stats_compare import (
    validate_word_stats_compare_payload,
    compare_word_stats
)


@celery_app.task(name="execute_word_stats", bind=True, max_retries=3)
def execute_word_stats(self, job_id: str):
    """Выполняет задачу WORD_STATS"""
    db = SessionLocal()
    repo = JobRepository(db)
    
    try:
        # Получаем задачу
        job = repo.get_job(job_id)
        if not job:
            raise PermanentJobError(f"Job {job_id} not found")
        
        # Обновляем статус на STARTED
        repo.update_job_status(job_id, JobStatus.STARTED)
        
        # Валидируем payload
        url = validate_word_stats_payload(job.payload)
        
        # Загружаем и анализируем страницу
        text = fetch_and_parse_url(url)
        top_words = get_word_stats(text)
        
        # Сохраняем результат
        result = {
            "url": url,
            "top_words": top_words
        }
        repo.update_job_status(job_id, JobStatus.DONE, result=result)
        
    except PermanentJobError as e:
        repo.update_job_status(job_id, JobStatus.FAILED, error=str(e))
    except Exception as e:
        repo.update_job_status(job_id, JobStatus.FAILED, error=str(e))
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()


@celery_app.task(name="execute_word_stats_compare", bind=True, max_retries=3)
def execute_word_stats_compare(self, job_id: str):
    """Выполняет задачу WORD_STATS_COMPARE"""
    db = SessionLocal()
    repo = JobRepository(db)
    
    try:
        # Получаем задачу
        job = repo.get_job(job_id)
        if not job:
            raise PermanentJobError(f"Job {job_id} not found")
        
        # Обновляем статус на STARTED
        repo.update_job_status(job_id, JobStatus.STARTED)
        
        # Валидируем payload
        left_job_id, right_job_id = validate_word_stats_compare_payload(job.payload)
        
        # Загружаем обе задачи из БД
        left_job = repo.get_job(left_job_id)
        if not left_job:
            raise PermanentJobError("Left source job not found")
        
        right_job = repo.get_job(right_job_id)
        if not right_job:
            raise PermanentJobError("Right source job not found")
        
        # Проверяем тип задач
        if left_job.type != JobType.WORD_STATS:
            raise PermanentJobError("Left source job is not WORD_STATS type")
        
        if right_job.type != JobType.WORD_STATS:
            raise PermanentJobError("Right source job is not WORD_STATS type")
        
        # Проверяем статус задач
        if left_job.status != JobStatus.DONE:
            raise PermanentJobError("Left source job is not completed")
        
        if right_job.status != JobStatus.DONE:
            raise PermanentJobError("Right source job is not completed")
        
        # Проверяем наличие результата
        if not isinstance(left_job.result, dict):
            raise PermanentJobError("Left source job result is not a dictionary")
        
        if not isinstance(right_job.result, dict):
            raise PermanentJobError("Right source job result is not a dictionary")
        
        # Проверяем наличие top_words
        if "top_words" not in left_job.result or not isinstance(left_job.result["top_words"], dict):
            raise PermanentJobError("Left source job result does not contain top_words dictionary")
        
        if "top_words" not in right_job.result or not isinstance(right_job.result["top_words"], dict):
            raise PermanentJobError("Right source job result does not contain top_words dictionary")
        
        # Сравниваем слова
        comparison = compare_word_stats(
            left_job.result["top_words"],
            right_job.result["top_words"]
        )
        
        # Формируем результат
        result = {
            "left_job_id": left_job_id,
            "right_job_id": right_job_id,
            "left_url": left_job.result.get("url", ""),
            "right_url": right_job.result.get("url", ""),
            "common_words": comparison["common_words"],
            "left_only": comparison["left_only"],
            "right_only": comparison["right_only"]
        }
        
        repo.update_job_status(job_id, JobStatus.DONE, result=result)
        
    except PermanentJobError as e:
        repo.update_job_status(job_id, JobStatus.FAILED, error=str(e))
    except Exception as e:
        repo.update_job_status(job_id, JobStatus.FAILED, error=str(e))
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()
