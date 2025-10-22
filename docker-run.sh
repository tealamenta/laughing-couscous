#!/bin/bash

echo "🚀 T PE DER (ER)"
echo "="
echo ""

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi

# Arrêter les conteneurs existants
echo "🛑 Arrêt des conteneurs existants..."
docker-compose down

# Lancer
echo ""
echo "🚀 Démarrage du conteneur..."
docker-compose up -d

echo ""
echo "✅ Application lancée!"
echo ""
echo "🌐  http://localhost1"
echo ""
echo "📋 Commandes utiles:"
echo "   docker-compose logs -f           # Voir les logs"
echo "   docker-compose ps                # État du conteneur"
echo "   docker-compose down              # Arrêter"
echo "   docker-compose restart           # Redémarrer"
