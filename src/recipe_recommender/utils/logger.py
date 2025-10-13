"""
Module de configuration du logging pour l'application Recipe Recommender.

Ce module configure deux loggers:
- debug.log : Tous les messages (DEBUG et supérieur)
- error.log : Uniquement les erreurs (ERROR et CRITICAL)
"""

import logging
import os
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "recipe_recommender",
    log_dir: str = "./logs",
    debug_level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Configure et retourne un logger avec deux handlers (debug et error).

    Cette fonction crée deux fichiers de log:
    - debug.log : Enregistre tous les événements (DEBUG et supérieur)
    - error.log : Enregistre uniquement les erreurs (ERROR et CRITICAL)

    Args:
        name: Nom du logger. Par défaut "recipe_recommender".
        log_dir: Répertoire où stocker les fichiers de log. Par défaut "./logs".
        debug_level: Niveau de logging pour le fichier debug. Par défaut logging.DEBUG.

    Returns:
        logging.Logger: Logger configuré avec les deux handlers.

    Example:
        >>> logger = setup_logger()
        >>> logger.info("Application démarrée")
        >>> logger.error("Erreur lors du chargement des données")

    Note:
        Les fichiers de log sont créés automatiquement si le répertoire n'existe pas.
    """
    # Créer le répertoire de logs s'il n'existe pas
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Créer le logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Éviter les doublons de handlers si le logger existe déjà
    if logger.handlers:
        return logger

    # Format des messages de log
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler pour debug.log (tous les messages)
    debug_handler = logging.FileHandler(log_path / "debug.log", encoding="utf-8")
    debug_handler.setLevel(debug_level)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    # Handler pour error.log (erreurs uniquement)
    error_handler = logging.FileHandler(log_path / "error.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # Handler pour la console (optionnel, pour le développement)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        fmt="%(levelname)s - %(message)s",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.debug(f"Logger '{name}' configuré avec succès")
    logger.debug(f"Fichiers de log créés dans: {log_path.absolute()}")

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Récupère un logger existant ou en crée un nouveau.

    Args:
        name: Nom du logger. Si None, utilise "recipe_recommender".

    Returns:
        logging.Logger: Instance du logger.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Message d'information")
    """
    if name is None:
        name = "recipe_recommender"

    logger = logging.getLogger(name)

    # Si le logger n'a pas de handlers, le configurer
    if not logger.handlers:
        return setup_logger(name)

    return logger
