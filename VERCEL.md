# MSI Gestion sur Vercel, avec la base Turso (version 2.3.0)

**Principe.** Vercel héberge le serveur de MSI Gestion, dont le code métier reste inchangé ; **Turso** garde la base de données de la clinique, unique et partagée par tous les appareils. Un pont relie les deux ; il a été vérifié par les 95 scénarios automatiques du logiciel.

**Conditions.**
- **Vercel Pro** : l’offre gratuite Hobby est réservée à l’usage personnel non commercial. Un essai gratuit de l’offre Pro existe.
- **Région** : serveur et base à Francfort (`fra1`). L’hébergement de données de santé hors de Côte d’Ivoire relève de l’autorisation de l’ARTCI.

## 1. Vercel Pro
Sur vercel.com, ouvrez **Settings**, puis **Billing**, et passez l’équipe en **Pro** (ou démarrez l’essai Pro).

## 2. Relier GitHub à Vercel
Sur vercel.com, ouvrez **Add New**, puis **Project**, puis **Continue with GitHub**. Autorisez l’application Vercel sur le compte GitHub qui porte le dépôt `MSI-gestion-`, au moins pour ce dépôt.

## 3. Mettre le code dans le dépôt GitHub
1. Si le dépôt ne contient pas encore `.github/workflows/decompresser.yml`, créez-le (**Add file**, puis **Create new file**) avec le contenu fourni.
2. **Add file**, puis **Upload files** : envoyez `msi-gestion-v2.3.0-pour-github.zip`, puis **Commit changes**.
3. Onglet **Actions** : attendez la coche verte. À la racine du dépôt apparaissent `vercel.json`, `api`, `serveur`, `public`…

## 4. Créer le projet Vercel
Importez le dépôt `MSI-gestion-` (**Add New**, puis **Project**), sans modifier les réglages : `vercel.json` les fournit.

## 5. Ajouter la base Turso
Dans le projet, onglet **Storage**, ouvrez **Create Database**, choisissez **Turso**, région **Frankfurt**, puis **Connect** au projet pour tous les environnements. Les variables `TURSO_DATABASE_URL` et `TURSO_AUTH_TOKEN` sont ajoutées automatiquement.

## 6. Choisir le mot de passe provisoire de l’administrateur
Dans **Settings**, puis **Environment Variables**, ajoutez `MSI_MDP_ADMIN_INITIAL` : 10 caractères au moins, connu de vous seul. Il ne sert qu’au premier démarrage, et son changement est imposé à la première connexion. Ne le communiquez à personne, pas même dans une conversation.

## 7. Déployer, puis se connecter
Onglet **Deployments** : **Redeploy**. Ouvrez l’adresse du projet (par exemple `https://msi-gestion.vercel.app`), connectez-vous avec `admin` et le mot de passe provisoire, choisissez votre mot de passe, puis créez les comptes du personnel. Le même lien fonctionne sur tous les appareils.

## Bon à savoir
- **Vitesse :** un écran se rafraîchit en moins d’une seconde environ (estimation, à confirmer en réel).
- **Sauvegardes :** l’écran « Sauvegardes » indique « inactive » sur Vercel. Les sauvegardes chiffrées automatiques vers le stockage de Vercel font l’objet de l’étape suivante.
- **Limitation des tentatives :** le blocage d’un compte après des échecs répétés reste appliqué par la base ; le plafond par adresse Internet est propre à chaque instance du serveur.
