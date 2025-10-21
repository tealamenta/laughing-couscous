"""Tests pour le module logger."""
import logging


def test_get_logger():
    """Test création logger."""
    from recipe_recommender.utils.logger import get_logger

    logger = get_logger("test_module")
    assert logger is not None
    assert isinstance(logger, logging.Logger)


def test_get_logger_different_names():
    """Test plusieurs loggers."""
    from recipe_recommender.utils.logger import get_logger

    logger1 = get_logger("module1")
    logger2 = get_logger("module2")

    assert logger1.name == "module1"
    assert logger2.name == "module2"


def test_logger_methods():
    """Test méthodes du logger."""
    from recipe_recommender.utils.logger import get_logger

    logger = get_logger("test_methods")

    # Ces appels ne doivent pas lever d'erreur
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
