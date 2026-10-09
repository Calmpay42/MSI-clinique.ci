#!/bin/sh
# Installation de MSI Gestion en ligne sur un serveur Ubuntu neuf (22.04 ou 24.04).
# À lancer en administrateur depuis le dossier « deploiement » : sudo ./installer-serveur.sh
set -e
cd "$(dirname "$0")"
[ "$(id -u)" = 0 ] || { echo "À lancer en administrateur : sudo ./installer-serveur.sh"; exit 1; }
if [ ! -f .env ]; then cp .env.exemple .env; echo "Fichier .env créé : indiquez DOMAINE et EMAIL_ADMIN, puis relancez."; exit 1; fi
. ./.env
echo "1/5  Mises à jour de sécurité automatiques"
apt-get update -y && apt-get install -y unattended-upgrades ufw curl
echo "2/5  Pare-feu : seuls SSH, HTTP et HTTPS restent ouverts"
ufw allow OpenSSH && ufw allow 80/tcp && ufw allow 443/tcp && ufw --force enable
echo "3/5  Docker"
command -v docker >/dev/null 2>&1 || curl -fsSL https://get.docker.com | sh
echo "4/5  Dossier des données de la clinique (accès restreint)"
mkdir -p donnees && chown 1000:1000 donnees && chmod 700 donnees
echo "5/5  Construction et démarrage"
docker compose up -d --build
sleep 10
docker compose logs msi | sed -n '/Comptes créés/,/Démarrage/p'
echo ""
echo "MSI Gestion est en ligne : https://$DOMAINE (le certificat HTTPS peut demander une minute au premier accès)."
echo "IMPORTANT : copiez donnees/cle-sauvegarde.key en lieu sûr (clé USB rangée au coffre) ; sans elle, les sauvegardes sont illisibles."
