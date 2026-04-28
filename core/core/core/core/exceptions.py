class PermanentJobError(Exception):
    """Ошибка, которая не требует повторных попыток выполнения задачи"""
    pass


class TemporaryJobError(Exception):
    """Ошибка, требующая повторной попытки выполнения задачи"""
    pass
