#!/bin/bash

echo " D ER E"
echo "="
echo ""

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo " Docker n'est pas installé"
    exit 1
fi

echo " Building image recipe-recommender:latest..."
docker-compose build --no-cache

echo ""
echo " Build terminé!"
echo ""
echo " Taille de l'image:"
docker images recipe-recommender:latest

echo ""
echo " Pour lancer: ./docker-run.sh"
