# MSI Gestion en ligne : guide de mise en ligne (version 2.2.1)

Maison de Santé Innov'Care, Bingerville. Ce guide installe MSI Gestion sur un serveur Internet : le personnel se connecte depuis n'importe où, par le lien de la clinique, et chacun retrouve son espace.

> **Sans serveur à administrer :** si vous ne voulez pas gérer un serveur vous-même, suivez plutôt `RENDER.md` (mise en ligne en un clic, entièrement depuis le navigateur). Le présent guide concerne un serveur que vous louez et administrez.

## 1. Principe

```
Personnel (clinique, domicile, téléphone, tablette)
        │  HTTPS (chiffré)
        ▼
https://gestion.innovcare.ci  ──►  Relais HTTPS (Caddy, certificat automatique)
                                        │
                                        ▼
                               Serveur MSI Gestion  ──►  Base de données + sauvegardes chiffrées
```

- **Un seul serveur, une seule base** : toutes les données sont au même endroit, à jour en temps réel pour tous les postes.
- **Chacun son espace** : les profils (accueil, caisse, infirmier, médecin, pharmacie, laboratoire, RH, facturiste, direction…) ne changent pas. Chacun ne voit que ce qui le concerne.
- **Toujours chiffré** : une connexion non chiffrée est redirigée vers `https://`, ou refusée.

## 2. Ce qu'il vous faut

| Élément | Recommandation |
|---|---|
| **Serveur** | Serveur privé virtuel (VPS) sous Ubuntu 24.04 : 2 processeurs, 4 Go de mémoire, 80 Go de disque SSD, sauvegarde du fournisseur activée |
| **Nom de domaine** | Par exemple `gestion.innovcare.ci`, avec un enregistrement DNS de type A qui pointe vers l'adresse IP du serveur |
| **Adresse e-mail** | Pour les avis concernant le certificat HTTPS |
| **Stockage distant** | Pour la copie nocturne des sauvegardes : espace de stockage en ligne de la clinique, autre fournisseur, ou second serveur |
| **Internet à la clinique** | Une connexion principale (fibre) et une **box 4G de secours** |

Le serveur se paie au mois et le nom de domaine à l'année : demandez des devis à deux ou trois hébergeurs.

## 3. Où héberger : la question des données de santé

MSI Gestion contient des **données de santé**, la catégorie la plus protégée par la loi ivoirienne sur la protection des données personnelles, sous le contrôle de l'ARTCI :

1. **Autorisation de l'ARTCI** pour le traitement des données de santé : c'est déjà une formalité en cours dans votre projet.
2. **Hébergement hors de Côte d'Ivoire** : le transfert de données à l'étranger demande en principe une autorisation supplémentaire. Un hébergeur installé en Côte d'Ivoire simplifie la démarche.
3. **Contrat avec l'hébergeur** : confidentialité, lieu de stockage, sauvegardes, restitution des données en fin de contrat.

Je ne suis pas juriste : faites valider le choix de l'hébergeur par votre conseil avant de mettre de vraies données en ligne.

## 4. Installation pas à pas (environ une heure)

1. **Commander le serveur** (Ubuntu 24.04) et noter son adresse IP.
2. **Créer l'enregistrement DNS** de type A : `gestion` vers l'adresse IP du serveur. Attendez qu'il soit actif (de quelques minutes à quelques heures).
3. **Copier MSI Gestion sur le serveur** :
   ```
   scp msi-gestion-v2.2.1.zip root@ADRESSE_IP:/opt/
   ssh root@ADRESSE_IP
   cd /opt && apt-get install -y unzip && unzip msi-gestion-v2.2.1.zip && cd msi-gestion/deploiement
   ```
4. **Renseigner les deux réglages** : `cp .env.exemple .env`, puis `nano .env` pour indiquer `DOMAINE` et `EMAIL_ADMIN`.
5. **Installer et démarrer** : `sudo ./installer-serveur.sh`. Le script :
   - active les mises à jour de sécurité automatiques ;
   - ferme le pare-feu sauf SSH, HTTP et HTTPS ;
   - installe Docker ;
   - crée la base et démarre le tout.

   Il affiche le **mot de passe provisoire de l'administrateur** : notez-le.
6. **Première connexion** : ouvrez `https://gestion.innovcare.ci`, connectez-vous avec `admin` et le mot de passe provisoire, puis choisissez un nouveau mot de passe (le changement est imposé).
7. **Mettre la clé de sauvegarde au coffre** : depuis votre ordinateur, lancez `scp root@ADRESSE_IP:/opt/msi-gestion/deploiement/donnees/cle-sauvegarde.key .`, puis rangez-la sur une clé USB au coffre. Sans elle, les sauvegardes chiffrées sont illisibles.
8. **Paramétrer la clinique** (notice, §8 et suivants) :
   - créer les comptes du personnel ;
   - vérifier les tarifs ;
   - importer le catalogue de la pharmacie ;
   - créer les chambres ;
   - confirmer les paramètres de paie.

## 5. Connexion du personnel

| Appareil | Comment |
|---|---|
| **Ordinateur** | Navigateur (Chrome, Edge ou Firefox), puis le lien de la clinique |
| **Téléphone ou tablette** | Le lien dans le navigateur, puis « Ajouter à l'écran d'accueil » ; ou l'application Android : « Se connecter au serveur de la clinique », puis saisir le lien |

Chaque personne a **son propre identifiant**. Un compte partagé rend le journal d'audit inutile.

## 6. Sécurité

**Déjà en place :**
- HTTPS obligatoire, certificat obtenu et renouvelé automatiquement ;
- connexions non chiffrées refusées ;
- cookie de session protégé (chiffré uniquement, inaccessible aux scripts, refusé aux autres sites) ;
- blocage d'un compte après plusieurs échecs, et limitation des tentatives par adresse Internet ;
- en-têtes de sécurité ;
- pare-feu (ports 22, 80 et 443 seulement) ;
- mises à jour de sécurité automatiques du système ;
- journal d'audit de toutes les actions.

**À faire par la clinique :**
- des mots de passe robustes, jamais communiqués ;
- quand un employé part : archiver sa fiche dans les ressources humaines et désactiver son compte dans le Paramétrage, **le jour même** ;
- un accès SSH au serveur par clé uniquement, réservé au prestataire informatique ;
- une surveillance de l'adresse `https://gestion.innovcare.ci/api/sante` par un service de surveillance, avec alerte par SMS ou e-mail si le serveur ne répond plus ;
- l'installation de chaque nouvelle version de MSI Gestion.

## 7. Sauvegardes

| Niveau | Fonctionnement |
|---|---|
| **Sur le serveur** | Automatique toutes les 15 minutes, chiffrée, dans `deploiement/donnees/sauvegardes` |
| **Hors du serveur** | Chaque nuit, par `sauvegarde-distante.sh`. Installez rclone (`apt-get install -y rclone`), créez avec `rclone config` un stockage nommé `msi-distant`, puis planifiez avec `crontab -e` la ligne : `30 2 * * * /opt/msi-gestion/deploiement/sauvegarde-distante.sh` |
| **Sauvegarde du fournisseur** | À activer chez l'hébergeur, en complément |

**Chaque mois, testez une restauration** sur un poste de test (notice, §12). Une sauvegarde jamais restaurée n'est pas une sauvegarde.

## 8. Mettre à jour MSI Gestion

Remplacez les fichiers du logiciel, **sauf** `deploiement/donnees` (les données) et `deploiement/.env` (vos réglages), puis lancez `docker compose up -d --build` dans le dossier `deploiement`. La base est conservée et mise à jour automatiquement.

## 9. Continuité de service

En ligne, **la clinique dépend d'Internet** :
- une **box 4G de secours** prend le relais en cas de coupure de la fibre ;
- en cas de panne totale, appliquez une **procédure papier** (fiches d'admission, reçus manuels numérotés), puis ressaisissez au retour de la connexion ;
- l'édition locale (fichier HTML) n'est **pas synchronisée** avec le serveur en ligne : ne l'utilisez pas en parallèle pour de vraies données.

## 10. Commandes utiles (dans le dossier `deploiement`)

| Besoin | Commande |
|---|---|
| État des services | `docker compose ps` |
| Journal du serveur | `docker compose logs -f msi` |
| Redémarrer | `docker compose restart` |
| Arrêter | `docker compose down` |
| Santé du serveur | `curl https://gestion.innovcare.ci/api/sante` |
