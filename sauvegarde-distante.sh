#!/bin/sh
# Copie hors du serveur des sauvegardes chiffrées de MSI Gestion, à planifier chaque nuit (voir MISE-EN-LIGNE.md).
# Prérequis : rclone installé et configuré avec un stockage nommé « msi-distant » (rclone config).
set -e
cd "$(dirname "$0")"
rclone copy donnees/sauvegardes msi-distant:msi-sauvegardes --min-age 1m --transfers 2
echo "$(date -Iseconds) copie distante terminée" >> donnees/sauvegarde-distante.log
