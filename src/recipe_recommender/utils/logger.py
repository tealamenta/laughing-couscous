"""
Module de configuration du logger pour l'application.

Fournit des fonctions pour initialiser et configurer les loggers
avec différents niveaux de verbosité et handlers.
"""

import logging
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str, log_file: Optional[str] = None, level: str = "INFO"
) -> logging.Logger:
    """
    Configure et retourne un logger.

    Args:
        name: Nom du logger.
        log_file: Chemin optionnel vers le fichier de log.
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        logging.Logger: Logger configuré.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Éviter les doublons de handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))

    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optionnel)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Récupère ou crée un logger simple.

    Args:
        name: Nom du logger (généralement __name__).

    Returns:
        logging.Logger: Logger configuré.
    """
    # Utiliser le logger root s'il existe
    if logging.getLogger().handlers:
        return logging.getLogger(name)

    # Sinon créer un logger basique
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
