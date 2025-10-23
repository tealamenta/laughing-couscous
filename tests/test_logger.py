from src.recipe_recommender.utils.logger import get_logger


def test_get_logger_returns_logger():
    logger = get_logger("testlogger")
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")


def test_logger_info_and_error():
    logger = get_logger("testlogger")
    logger.info("Test info message")
    logger.error("Test error message")
    # Vérification simple : ne lève pas d'exception
