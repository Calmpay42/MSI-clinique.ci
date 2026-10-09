# MSI Gestion en ligne avec Render (sans ligne de commande)

**Pourquoi ce guide.** Le fichier `MSI-Gestion.html` (édition autonome) enregistre les données **dans chaque appareil séparément**. Mis sur un site comme Netlify, il ne partage rien : un compte créé sur votre ordinateur n’existe pas sur le téléphone d’un collègue. Pour travailler à plusieurs avec un seul lien, il faut **l’édition serveur**, qui tourne sur un hébergeur et garde **une base unique**. Render est un hébergeur qui s’utilise entièrement depuis le navigateur.

**Coût indicatif :** offre « Starter » et disque de 5 Go, soit quelques dollars par mois. Vérifiez le tarif sur render.com avant de vous engager ; une carte bancaire est demandée.

**Données de santé :** le serveur est à Francfort (Union européenne). L’hébergement de données de santé hors de Côte d’Ivoire relève d’une autorisation de l’ARTCI (voir `MISE-EN-LIGNE.md`, §3).

## 1. Déposer le logiciel sur GitHub (10 minutes)

1. Créez un compte gratuit sur **github.com**.
2. Cliquez **New repository**, nommez-le `msi-gestion`, choisissez **Private**, puis **Create repository**.
3. Sur votre ordinateur, décompressez `msi-gestion-v2.2.1.zip`, puis ouvrez le dossier `msi-gestion`.
4. Sur la page du dépôt, cliquez **uploading an existing file**. Glissez-y **tout le contenu** du dossier `msi-gestion` (dossiers `serveur`, `public`, `scripts`, `deploiement`, et les fichiers `package.json`, `render.yaml`…), puis **Commit changes**.

## 2. Mettre en ligne sur Render (10 minutes)

1. Créez un compte sur **render.com** (bouton **Sign in with GitHub**).
2. Cliquez **New**, puis **Blueprint**, autorisez l’accès au dépôt `msi-gestion`, choisissez-le. Render lit le fichier `render.yaml` : un service web `msi-gestion` et un disque de 5 Go.
3. Cliquez **Apply** et ajoutez la carte bancaire demandée. Le premier déploiement prend de 5 à 10 minutes.
4. Ouvrez le service `msi-gestion`, puis l’onglet **Logs**. Au premier démarrage, une ligne « Comptes créés » donne le **mot de passe provisoire de l’administrateur** : notez-le.
5. En haut de la page du service figure son adresse, par exemple `https://msi-gestion-ab12.onrender.com` : c’est **le lien de la clinique**.

## 3. Premier accès

1. Ouvrez le lien, connectez-vous avec `admin` et le mot de passe provisoire, puis choisissez votre mot de passe (le changement est imposé).
2. **Clé de sauvegarde :** dans Render, onglet **Shell** du service, tapez `cat donnees/cle-sauvegarde.key`, copiez le texte et rangez-le en lieu sûr (clé USB au coffre).
3. Créez les comptes du personnel (Paramétrage, Utilisateurs), puis envoyez-leur **le lien**, leur identifiant et leur mot de passe provisoire. Chacun pourra se connecter depuis n’importe quel téléphone ou ordinateur.

Les comptes créés dans l’édition autonome (sur Netlify ou dans l’application) restent sur l’appareil où ils ont été créés : recréez-les sur le serveur.

## 4. Garder votre lien Netlify

Pour que `maisondesanteinnocare.netlify.app` mène au vrai serveur :
1. Dans le dossier `deploiement/netlify-redirection`, remplacez `ADRESSE-DU-SERVEUR`, dans les fichiers `_redirects` et `index.html`, par l’adresse donnée par Render (sans `https://` dans `_redirects`).
2. Sur netlify.com, ouvrez votre site, onglet **Deploys**, et glissez le dossier `netlify-redirection` dans la zone de dépôt.

## 5. Téléphones

- **Navigateur :** ouvrez le lien, puis « Ajouter à l’écran d’accueil ».
- **Application Android :** sur le premier écran, rubrique « Serveur de la clinique », saisissez l’adresse du serveur. L’application travaille alors sur la base commune.

## 6. Mises à jour

Déposez les fichiers de la nouvelle version sur GitHub, en remplaçant les anciens. Render redéploie seul ; la base, sur le disque, est conservée.
