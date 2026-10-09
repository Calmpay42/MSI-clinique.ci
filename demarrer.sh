#!/bin/sh
# Démarrage du serveur MSI Gestion en ligne. Au tout premier démarrage, la base de production est créée :
# les comptes initiaux s'affichent UNE SEULE FOIS dans le journal (docker compose logs msi), mot de passe à changer à la première connexion.
set -e
cd "$(dirname "$0")"
# Lancé en administrateur système (conteneur) : le dossier des données est confié à l'utilisateur restreint « node »,
# puis le script se relance sous cet utilisateur. Le serveur ne tourne jamais avec les droits d'administrateur.
if [ "$(id -u)" = "0" ] && id node >/dev/null 2>&1; then
  mkdir -p donnees && chown -R node:node donnees
  exec setpriv --reuid=node --regid=node --init-groups "$0" "$@"
fi
if [ ! -f donnees/msi.db ]; then
  echo "=== Premier démarrage : création de la base de production ==="
  node scripts/initialiser.js
  echo "=== Notez le mot de passe administrateur ci-dessus, puis copiez donnees/cle-sauvegarde.key en lieu sûr. ==="
fi
exec node serveur/index.js
