import logging
from src.recipe_recommender.utils import logger as logger_module


def test_get_logger_returns_logger_instance(caplog):
    """Vérifie que get_logger retourne bien un objet logger et logge un message."""
    log = logger_module.get_logger("test_logger")
    assert isinstance(log, logging.Logger)
    assert log.name == "test_logger"

    with caplog.at_level(logging.INFO):
        log.info("message test get_logger")
    assert "message test get_logger" in caplog.text


def test_get_logger_does_not_duplicate_handlers():
    """Vérifie que get_logger ne duplique pas les handlers."""
    log1 = logger_module.get_logger("duplicate_test")
    initial = len(log1.handlers)
    log2 = logger_module.get_logger("duplicate_test")
    assert len(log2.handlers) == initial
    assert log1 is log2


def test_setup_logger_creates_console_handler():
    """Vérifie que setup_logger ajoute un StreamHandler."""
    log = logger_module.setup_logger("console_logger", level="DEBUG")
    handler_types = [type(h) for h in log.handlers]
    assert logging.StreamHandler in handler_types
    assert log.level == logging.DEBUG


def test_setup_logger_creates_file_handler(tmp_path):
    """Vérifie que setup_logger crée un fichier log quand log_file est fourni."""
    log_file = tmp_path / "test.log"
    log = logger_module.setup_logger(
        "file_logger", log_file=str(log_file), level="INFO"
    )
    handler_types = [type(h) for h in log.handlers]
    assert logging.FileHandler in handler_types
    assert log_file.exists()

    # Écrire un message et vérifier dans le fichier
    log.info("Message dans le fichier")
    log.handlers[1].flush()  # s'assurer que l'écriture est faite
    content = log_file.read_text()
    assert "Message dans le fichier" in content


def test_setup_logger_returns_same_instance_on_reuse(tmp_path):
    """Vérifie qu'appeler setup_logger deux fois ne double pas les handlers."""
    log_file = tmp_path / "reuse.log"
    log1 = logger_module.setup_logger("reuse_logger", log_file=str(log_file))
    handlers_before = len(log1.handlers)
    log2 = logger_module.setup_logger("reuse_logger", log_file=str(log_file))
    assert len(log2.handlers) == handlers_before
    assert log1 is log2
