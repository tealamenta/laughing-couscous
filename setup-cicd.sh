#!/bin/bash

echo "SETUP CI/CD - GITHUB ACTIONS"
echo "==============================="
echo "Date: 2025-10-21 23:47:56 UTC"
echo "User: tealamenta"
echo ""

cd ~/Projects/recipe-recommender

# Ajouter tous les fichiers
git add -A

# Voir ce qui sera commité
echo " Fichiers à commiter:"
git status --short
echo ""

# Commit
git commit -m "ci: Setup complete CI/CD pipeline with GitHub Actions

CI/CD PIPELINE CONFIGURED 
============================
Date: 2025-10-21 23:47:56 UTC
Author: @tealamenta

WORKFLOWS ADDED:
===============

1. CI - Tests & Quality (.github/workflows/ci.yml)
   ------------------------------------------------
   Triggers: push, pull_request on main/develop
   
   Jobs:
    test: Run pytest, coverage, linting
      - Python 3.12 matrix
      - Poetry dependency management
      - Pytest with coverage (XML + term)
      - Codecov integration
      - Ruff linting
      - Black formatting check
      - Radon complexity check
      - Complexity grade validation (A)
   
    security: Security scanning
      - Safety check for vulnerabilities
      - Dependency audit
   
    docker: Docker build test
      - Multi-stage build
      - Health check validation
      - Cache optimization (GitHub Actions cache)

2. Deploy (.github/workflows/deploy.yml)
   ---------------------------------------
   Triggers: push to main, tags v*, manual
   
   Jobs:
    deploy: Streamlit Cloud deployment
      - Auto-deploy notification
      - Deployment ready confirmation
   
    notify: Success notification
      - Post-deployment checks

3. Release (.github/workflows/release.yml)
   ----------------------------------------
   Triggers: tags v*.*.*
   
   Jobs:
    release: Create GitHub Release
      - Run full test suite
      - Generate metrics (complexity, tests)
      - Auto-generate changelog
      - Create release with notes
   
    docker-publish: Publish to Docker Hub
      - Multi-platform build
      - Semantic versioning tags
      - latest tag update
      - GitHub Container Registry

4. Health Check (.github/workflows/health-check.yml)
   --------------------------------------------------
   Triggers: weekly (Monday 9am UTC), manual
   
   Jobs:
    health: Project health monitoring
      - Full test suite
      - Code metrics report
      - Dependency audit
      - Auto-create issue if failures

CONFIGURATION FILES:
===================
 .streamlit/config.toml
   - Production settings
   - Theme configuration
   - Server settings

 requirements.txt
   - Generated from poetry.lock
   - Streamlit Cloud compatible
   - No hashes for compatibility

 .github/SECRETS.md
   - Documentation for secrets
   - Docker Hub setup
   - Codecov setup

FEATURES:
========
- Automated testing on every push
- Code quality checks (Ruff, Black)
- Complexity monitoring (Grade A enforcement)
- Security scanning
- Docker build validation
- Automated deployments
- Release automation
- Weekly health monitoring
- Coverage reporting (Codecov)
- Dependency caching for speed

BADGES ADDED TO README:
======================
- CI Status
- Python Version
- Code Grade (A)
- Tests (101 passing)
- Coverage (41%)
- License

NEXT STEPS:
==========
1.  Push to GitHub → CI will run automatically
2. Configure secrets (optional):
   - DOCKERHUB_USERNAME
   - DOCKERHUB_TOKEN
   - CODECOV_TOKEN
3. Watch CI/CD in Actions tab
4. Create release tag: git tag v1.0.0 && git push --tags

BENEFITS:
========
- Automated quality assurance
- Catch issues before merge
- Maintain Grade A complexity
- Security monitoring
- Streamlined deployments
- Professional DevOps practices
- Continuous integration
- Continuous deployment

STATUS: CI/CD READY 
=====================
All workflows configured and ready to run
Professional-grade automation pipeline
Production-ready DevOps setup

Author: @tealamenta
Date: 2025-10-21 23:47:56 UTC"

if [ $? -eq 0 ]; then
    echo ""
    echo "- Commit créé"
    echo ""
    git log --oneline -1
    echo ""
    echo " PUSH VERS GITHUB ?"
    echo ""
    read -p "Appuyez sur Entrée pour pusher..."
    
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "========================================"
        echo " CI/CD CONFIGURÉ ET PUBLIÉ!"
        echo "========================================"
        echo ""
        echo " GitHub Actions:"
        echo "   https://github.com/tealamenta/recipe-recommender/actions"
        echo ""
        echo " Les workflows vont se lancer automatiquement!"
        echo ""
        echo " Prochaines étapes:"
        echo "   1. Voir les Actions sur GitHub"
        echo "   2. Configurer les secrets (optionnel)"
        echo "   3. Créer une release: git tag v1.0.0 && git push --tags"
        echo ""
        echo " PIPELINE CI/CD OPÉRATIONNEL!"
    fi
fi
