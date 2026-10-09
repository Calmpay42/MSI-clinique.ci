# MSI Gestion, version 2.3.0 (recettes, consultations, laboratoire et tiers payant)

Système de gestion de la **Maison de Santé Innov’Care** (MSI), Bingerville. La version 1.0 couvre l’accueil, la caisse, la pharmacie, la direction et le paramétrage. La version 1.1 ajoute le poste **Consultations** : dossier médical, documents et rendez-vous pour 13 spécialités, sur le modèle d’OphtaSuite (§ 9). La version 1.2 ajoute la reprise des dossiers d’OphtaSuite, les photos et documents scannés du dossier, et les fiches conseils remises aux patients. La version 1.3 ajoute les bordereaux assureurs, le laboratoire, les avances des patients et la facture récapitulative (§ 10).

Principes de fonctionnement :

- **Un PC serveur** installé à la clinique héberge l’application et la base de données.
- **Les postes** (PC, tablettes, téléphones) ouvrent simplement un navigateur sur le réseau de la clinique.
- **Internet n’est pas nécessaire** au fonctionnement ; il sert uniquement à la copie des sauvegardes dans le cloud.
- **Toutes les règles de gestion sont appliquées par le serveur.** Aucun poste ne peut les contourner : paiement avant délivrance, remises plafonnées, numérotation continue, journal d’audit.

> Avant le démarrage réel, suivez le **dossier de mise en service** (`MISE-EN-SERVICE.md`).

---

## 1. Matériel et logiciels requis

| Élément | Exigence |
|---|---|
| PC serveur | Windows 10 ou 11 (64 bits), ou Linux Ubuntu 22.04 et plus. 8 Go de mémoire, disque SSD. |
| Alimentation | **Onduleur obligatoire.** Le serveur reste allumé 24 h/24. |
| Adresse réseau | Adresse IP fixe : réservation dans le routeur ou la box, par exemple `192.168.1.10`. |
| Logiciel | **Node.js LTS**, version 20 ou 22 (nodejs.org). |
| Postes | Chrome, Edge ou Firefox récents, sur le même réseau que le serveur. |
| Caisse | Imprimante thermique 80 mm, définie comme imprimante par défaut du poste de caisse. |
| Copie hors site | Google Drive pour ordinateur ou OneDrive, installé sur le serveur. |
| Disque | Chiffrement BitLocker activé sur le serveur (données de santé). |

---

## 2. Installation sur Windows

**Le plus simple :** copiez le dossier `deploiement/windows/Demarrer-MSI-Gestion.bat` à la racine du logiciel (il y est déjà dans le paquet « serveur de la clinique pour Windows ») et double-cliquez dessus. Il vérifie Node.js, installe les composants, crée la base, affiche le mot de passe de l’administrateur, démarre le serveur et indique l’adresse à donner aux autres postes. **Node.js 20 ou 22 obligatoire** : le composant de base de données n’existe pas encore en version précompilée pour Node.js 24 sous Windows.

Installation manuelle, pour un prestataire informatique :

1. Installez **Node.js LTS**, en gardant les options par défaut.
2. Copiez le dossier `msi-gestion` dans `C:\MSI\msi-gestion`.
3. Ouvrez **PowerShell** dans ce dossier et installez les composants :
   ```
   npm install --omit=dev
   ```
4. Copiez `config.exemple.json` en `config.json`, puis ajustez-le (voir § 5).
5. Initialisez la base de production :
   ```
   npm run initialiser
   ```
   **Notez le mot de passe provisoire du compte `admin`**, affiché une seule fois. **Copiez aussitôt** le fichier `donnees\cle-sauvegarde.key` sur deux clés USB (voir § 6).
6. Démarrez le serveur :
   ```
   npm start
   ```
   Il affiche l’adresse à ouvrir depuis les autres postes, par exemple `http://192.168.1.10:8080`.
7. **Pare-feu** : autorisez le port, dans PowerShell ouvert en administrateur.
   ```
   netsh advfirewall firewall add rule name="MSI Gestion" dir=in action=allow protocol=TCP localport=8080 profile=private
   ```
8. **Démarrage automatique** : créez une tâche planifiée au démarrage de Windows, dans PowerShell ouvert en administrateur.
   ```
   schtasks /Create /TN "MSI Gestion" /SC ONSTART /RU SYSTEM /RL HIGHEST /TR "cmd /c cd /d C:\MSI\msi-gestion && \"C:\Program Files\nodejs\node.exe\" serveur\index.js >> donnees\serveur.log 2>&1"
   ```
   Redémarrez le PC et vérifiez que l’application répond sans intervention.

## 3. Installation sur Linux (variante)

Exécutez les mêmes étapes 1 à 6 dans `/opt/msi-gestion`, puis créez le service `/etc/systemd/system/msi-gestion.service` :

```
[Unit]
Description=MSI Gestion
After=network.target

[Service]
WorkingDirectory=/opt/msi-gestion
ExecStart=/usr/bin/node serveur/index.js
Restart=always
User=msi
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

Activez-le avec `systemctl enable --now msi-gestion`.

## 4. Connexion sécurisée HTTPS (recommandée)

Sur un réseau Wi-Fi, activez le HTTPS pour que les mots de passe ne circulent jamais en clair :

```
npm run certificat
```

Redémarrez ensuite le serveur : il passe automatiquement en `https://`. Sur chaque poste, le navigateur signale un certificat « non reconnu » à la première visite. Acceptez-le une fois, en vérifiant que l’adresse est bien celle du serveur MSI.

## 5. Configuration (`config.json`)

| Clé | Rôle | Valeur par défaut |
|---|---|---|
| `port` | Port d’écoute (la base de formation utilise le port suivant) | `8080` |
| `base` | Fichier de la base de production | `donnees/msi.db` |
| `fuseau` | Fuseau horaire des vacations et des reçus | `Africa/Abidjan` |
| `sauvegarde.dossier` | Dossier local des sauvegardes | `donnees/sauvegardes` |
| `sauvegarde.dossier_cloud` | Second dossier, synchronisé avec le cloud ou situé sur un NAS | vide |
| `sauvegarde.intervalle_min` | Fréquence des sauvegardes, en minutes | `15` |

---

## 6. Sauvegardes et restauration

**Fonctionnement automatique :**

- Une copie de la base est faite **toutes les 15 minutes**, sans arrêter le service.
- Chaque copie est **chiffrée (AES-256)**.
- Elle est écrite dans `donnees/sauvegardes`, puis dans `dossier_cloud` s’il est configuré.
- Conservation : les 96 dernières copies (24 heures), puis une copie par jour pendant 90 jours.

**Copie hors site :**

- **Solution simple :** dans Google Drive pour ordinateur, ouvrez « Préférences », puis « Mon ordinateur », et ajoutez le dossier `C:\MSI\msi-gestion\donnees\sauvegardes`.
- **Autre solution :** indiquez un dossier OneDrive dans `dossier_cloud`.
- Le serveur doit rester connecté à sa session Windows (écran verrouillé) pour que la synchronisation fonctionne.

**La clé de chiffrement `donnees/cle-sauvegarde.key` est vitale :**

- sans elle, aucune sauvegarde n’est lisible ;
- gardez-en **deux copies sur clé USB** : l’une au coffre, l’autre chez le gérant ;
- ne la mettez **jamais** dans le dossier cloud.

**Vérification :** l’écran **Paramétrage, puis Sauvegardes** affiche la dernière copie et son statut cloud. Le bouton « Sauvegarder maintenant » lance une copie immédiate.

**Test de restauration mensuel,** sans toucher à la production :

```
npm run restaurer -- donnees\sauvegardes\msi-AAAAMMJJ-HHMMSS.msibak --vers donnees\essai-restauration.db
```

Le script vérifie l’intégrité de la base et affiche le nombre de patients, de passages et de reçus.

**Restauration réelle,** après un sinistre :

1. Arrêtez le serveur.
2. Lancez `npm run restaurer -- <fichier.msibak>`.
3. Redémarrez le serveur.

La base remplacée est conservée sous le nom `msi.avant-restauration-<date>.db`. Sur un nouveau PC, réinstallez l’application (§ 2, étapes 1 à 3) et replacez la clé dans `donnees/` **avant** de restaurer.

---

## 7. Base de formation

La base de formation est séparée de la production. Elle contient des données fictives et un bandeau « Base de formation » s’affiche sur tous les écrans.

```
npm run formation
npm start -- --formation
```

Elle répond sur le port **8081**. Les comptes d’essai sont affichés à l’initialisation : `accueil1`, `caisse1`, `pharma1`, `medecin1` (ophtalmologie), `medecin2` (médecine générale et cardiologie), `labo1` (laboratoire), `raf1`, `direction1` et `admin`. Rien de ce qui est saisi en formation n’atteint la production.

## 8. Profils et accès

| Profil | Écrans |
|---|---|
| Accueil, accord assurance | Accueil |
| Accueil, facturation (caisse) | Caisse |
| Pharmacie | Pharmacie |
| Gérant de la pharmacie | Pharmacie, plus le catalogue des médicaments : ajout et modification, prix validés par la direction |
| Médecin ou praticien | Consultations, limitées à ses spécialités |
| Laboratoire | Laboratoire : examens payés à réaliser, saisie et validation des résultats |
| Infirmier ou infirmière | Infirmerie : constantes du patient, puis orientation vers le médecin qui le recevra |
| Facturiste | Tiers payant, factures et exports : bordereaux par assureur, règlements, rejets, créances |
| Ressources humaines | Personnel et planning ; préparation de la paie, que seule la direction valide |
| Comptable | Comptabilité : journal, grand livre, balance, plan de correspondance, export ; aucun accès aux dossiers médicaux |
| Responsable administratif et financier | Direction (indicateurs, exports), Tiers payant, Paramétrage (tarifs, produits, assureurs, imports) |
| Direction | Direction (dont validations), Accueil, stock de la pharmacie, Paramétrage (dont paramètres sensibles) |
| Administrateur système | Paramétrage (comptes, sauvegardes, intégrité du journal) |

Règles de gestion des comptes :

- Un même compte ne peut jamais cumuler **caisse** et **pharmacie**, **caisse** et **médecin**, ni **caisse** et **laboratoire** : celui qui encaisse ne délivre, ne prescrit ni ne réalise l’examen.
- Un compte médecin indique ses spécialités et son n° d’inscription à l’Ordre ; ce numéro figure sur les documents imprimés.
- Un membre de la direction ne peut pas valider **sa propre** demande.
- Le gérant reçoit en général les profils **Direction** et **Administrateur système**.

## 9. Poste Consultations (médecins)

Le poste Consultations reprend OphtaSuite pour l’ophtalmologie et applique le même modèle aux autres spécialités. Il couvre les 11 spécialités de l’en-tête MSI, plus la psychiatrie et la psychologie.

**Déroulé :**

1. L’accueil ouvre le passage.
2. Le patient apparaît dans la file du médecin de la spécialité, marqué « À régler à la caisse ».
3. **La consultation ne s’ouvre qu’une fois le bon réglé** ; font exception l’urgence et le contrôle gratuit. Le déblocage est automatique après l’encaissement.
4. Le médecin remplit le formulaire de sa spécialité :
   - motif, antécédents, constantes et examen propre à la spécialité, puis conclusion ;
   - un clic sur une suggestion l’insère dans le champ, où elle reste modifiable ;
   - des alertes signalent notamment une tension élevée, une hypoglycémie, une PIO au-dessus de 21 mmHg, un DFG abaissé ou une hypoxie ;
   - chez l’enfant, aucune alerte adulte ne se déclenche.
5. Il émet ses documents, numérotés et imprimables en A5 avec le logo MSI :
   - ordonnance, demande d’examens, certificat, compte rendu, lettre d’orientation ;
   - ordonnance de lunettes en ophtalmologie ;
   - rendez-vous.
6. **Les examens réalisés à MSI partent à la caisse** au tarif du catalogue ; ceux réalisés à l’extérieur sont seulement imprimés.
7. La pharmacie reprend l’ordonnance d’un clic.
8. L’accueil voit les rendez-vous.
9. Le médecin **valide** la consultation : elle devient définitivement non modifiable. Une précision ultérieure passe par une note complémentaire.

**Secret médical :**

- seul le profil médecin lit le contenu clinique ;
- la caisse ne voit que les bons, la pharmacie que les médicaments prescrits, l’accueil que les rendez-vous ;
- la direction ne lit pas les dossiers médicaux ;
- chaque ouverture de dossier est journalisée.

**Adapter une spécialité :** tout le contenu clinique se trouve dans `public/js/specialites.js`. Ce fichier contient, pour chaque spécialité :

- les suggestions, les champs d’examen et les diagnostics ;
- les examens et leur code tarifaire ;
- les médicaments, avec une posologie indicative ;
- les modèles de comptes rendus et de certificats.

Le formulaire se construit à partir de ce fichier : modifier une spécialité ne demande aucune autre programmation. Après toute modification, lancez `npm test`, qui vérifie la cohérence du référentiel.

**Photos et documents scannés :**

- depuis l’onglet Documents, le médecin joint une photo (rétinophotographie, lésion cutanée…) ou un PDF (résultat d’examen extérieur), 3 Mo au plus ;
- les photos sont réduites automatiquement ;
- le format est vérifié sur le contenu réel du fichier ;
- une pièce jointe n’est jamais modifiable ni supprimable, et relève du secret médical comme le reste du dossier.

**Fiches conseils :** chaque spécialité propose des fiches à remettre au patient, dont les 12 d’OphtaSuite en ophtalmologie. Le médecin coche les fiches voulues, qui s’impriment sous son nom ; le texte remis reste figé dans le dossier.

**Reprise d’OphtaSuite** (bouton « Reprise OphtaSuite », réservé aux médecins habilités en ophtalmologie) :

1. Dans OphtaSuite, exportez la sauvegarde (fichier `ophtasuite-sauvegarde-AAAA-MM-JJ.json`).
2. Dans MSI Gestion, choisissez ce fichier puis cliquez sur « Analyser » : l’écran indique ce qui sera repris.
3. Cliquez sur « Importer ».

L’import se fait tout ou rien et respecte ces règles :

- **patients** : ceux déjà connus de MSI sont rapprochés de leur dossier (mêmes nom et prénoms, et même date de naissance ou même téléphone) ;
- **consultations** : figées à leur date, attribuées au compte technique « Reprise OphtaSuite », avec le nom du médecin d’origine conservé ;
- **documents, photos et rendez-vous à venir** : repris ;
- **caisse** : aucun bon n’est créé ;
- **relance** : relancer la reprise ne crée aucun doublon ;
- **non repris** : tarifs, stock et fichier des médecins, déjà gérés par MSI Gestion ; tracé des schémas du fond d’œil, dont les commentaires et la photo sont repris.

## 10. Tiers payant, laboratoire, avances et factures (version 1.3)

**Tiers payant** (onglet « Tiers payant », pour le RAF et la direction) :

- **À facturer** : la part assureur encaissée et pas encore facturée, par assureur.
- **Bordereau** : il se crée en un clic, pour une période donnée. Numéroté (BRD-AAAA-NNNN) et figé, il s’imprime ou s’exporte vers Excel pour l’assureur. **Un acte n’est jamais facturé deux fois.**
- **Règlements** : virement, chèque, mobile money ou espèces, avec référence. Chaque règlement est lettré sur le bordereau et ne peut pas dépasser le reste dû.
- **Rejets** : les lignes refusées par l’assureur sont rejetées avec un motif.
- **Annulation** : un bordereau non réglé ne s’annule que par la direction, avec motif ; ses actes redeviennent à facturer.
- **Balance âgée** : par assureur, le non facturé et les restes dus à 30, 60, 90 jours et au-delà.

**Laboratoire** (onglet « Laboratoire ») :

- La liste de travail montre les examens de laboratoire prescrits ou saisis à la caisse. **Un examen non réglé ne peut pas être réalisé**, sauf en urgence.
- Sept examens ont un modèle de saisie avec leurs valeurs de référence : NFS, goutte épaisse, glycémie, créatininémie, CRP, transaminases, ECBU.
- Toute valeur hors normes est signalée, élevée ou basse.
- Le résultat validé est figé, imprimable, et visible du médecin dans le dossier.
- Une erreur se corrige par une rectification motivée, qui garde l’historique.
- La direction suit les examens payés mais non réalisés.

**Avances des patients et facture récapitulative** (caisse) :

- **Avance** : bouton « Avance patient ». L’avance est numérotée (DEP-AAAA-NNNNN) et encaissée comme un paiement.
- **Utilisation** : le patient règle ensuite ses bons avec le mode « Avance du patient », dans la limite de son solde. Si le reçu est annulé, l’avance est restituée.
- **Remboursement** : demandé à la caisse, validé par la direction, puis versé en espèces depuis une caisse ouverte. La caisse reste juste au franc près.
- **Facture récapitulative** : bouton « Facture » sur un reçu, ou « Facture récapitulative » dans la fiche du patient à la caisse.
  - Elle récapitule un passage : actes, part assureur, remises, règlements et reste à payer.
  - Elle est numérotée (FAC-AAAA-NNNNN), figée, et peut être établie au nom du patient, d’un employeur ou d’un organisme.
  - Elle reste possible des jours après le passage.

## 11. Exploitation quotidienne

- **Prise de vacation :** chaque agent de caisse ouvre **sa** caisse avec son fonds.
- **Passation :** l’agent sortant clôture avec le billetage, puis le suivant ouvre la sienne.
- **Écart de caisse :** il est justifié par l’agent, puis validé par la direction (Direction, rubrique « Validations »).
- **Demandes en attente :** remises au-delà du plafond, annulations de reçus, écarts et gros ajustements de stock attendent la direction. Les bons concernés restent bloqués jusqu’à la décision.
- **Exports** (Direction, rubrique « Exports pour Excel ») : journal de caisse, sorties SYSCOHADA, tiers payants par assureur, stock, registre des psychotropes, journal d’audit.
- **Déconnexion :** automatique après 30 minutes d’inactivité (paramétrable). Chaque agent se déconnecte en quittant son poste.

## 12. Mises à jour

1. Faites une sauvegarde manuelle (Paramétrage, puis Sauvegardes).
2. Arrêtez le serveur.
3. Remplacez tous les fichiers, **sauf** `donnees/` et `config.json`.
4. Lancez `npm install --omit=dev`, puis redémarrez.
5. Vérifiez que l’écran de connexion s’affiche et que la dernière sauvegarde est récente.

Au démarrage, le serveur ajoute au catalogue les actes apparus dans la nouvelle version, sans modifier les tarifs existants. En production, ces nouveaux actes arrivent marqués « à valider ».

## 13. Sécurité

Protections intégrées :

- **Comptes nominatifs** avec mots de passe hachés (scrypt) et changement obligatoire à la première connexion.
- **Verrouillage** du compte pendant 15 minutes après 5 échecs de connexion.
- **Aucune suppression possible,** même directement dans la base : reçus, bons, patients, paiements, sorties, mouvements de stock.
- **Caisse clôturée et reçus figés.**
- **Journal d’audit chaîné :** toute retouche de l’historique est détectée (Paramétrage, puis Journal, puis « Vérifier maintenant »).
- **Reçus authentifiables :** chaque reçu porte un code de contrôle, vérifiable dans Direction, rubrique « Vérifier un reçu ».

Mesures à la charge de la clinique :

- serveur dans un local fermé ;
- session Windows protégée par mot de passe ;
- **BitLocker** activé ;
- clé de sauvegarde au coffre ;
- revue mensuelle des comptes actifs.

## 14. Protection des données personnelles

L’application traite des données de santé, qui sont des données sensibles au sens de la loi ivoirienne n° 2013-450 du 19 juin 2013 relative à la protection des données à caractère personnel. Avant la mise en production, faites vérifier par votre conseil les obligations suivantes :

- les formalités préalables auprès de l’**ARTCI** (déclaration ou autorisation) ;
- l’information des patients ;
- les durées de conservation ;
- la sécurité de la copie hors site.

Cette note n’est pas un avis juridique.

## 15. Dépannage

| Symptôme | Cause probable et solution |
|---|---|
| « Base introuvable » au démarrage | La base n’est pas initialisée : lancez `npm run initialiser`. |
| Un poste n’accède pas à l’application | Pare-feu (§ 2, étape 7), adresse IP du serveur modifiée, ou poste sur un autre réseau. |
| « Serveur injoignable » à l’écran | Le serveur est arrêté ou redémarre : attendez 30 secondes, puis vérifiez la tâche planifiée. |
| Le port est déjà utilisé | Une autre instance tourne déjà, ou changez `port` dans `config.json`. |
| Heure fausse sur les reçus | Réglez l’horloge du serveur (synchronisation automatique de Windows). |
| Ticket coupé ou trop petit | Dans la boîte d’impression : papier 80 mm, marges « aucune », échelle 100 %. |
| Compte bloqué | Attendez 15 minutes, ou faites réinitialiser le mot de passe par l’administrateur. |
| « Tarif non validé » à l’accueil | Le tarif est encore marqué à valider : Paramétrage, puis Tarifs, puis « Vérifier ». |

## 16. Pour le technicien

| Élément | Emplacement |
|---|---|
| Serveur | `serveur/` : Node.js, Express, SQLite en mode WAL. Les règles métier sont dans `regles.js`, `caisse.js`, `pharmacie.js`, `direction.js` et `admin.js`. |
| Interface | `public/` : JavaScript sans compilation, un fichier par poste. |
| Recette automatique | `npm test` lance 34 scénarios : sécurité, droits, règles de gestion, verrous anti-fuite, sauvegarde, module clinique, reprise d’OphtaSuite, pièces jointes, avances, facture récapitulative, laboratoire, bordereaux. Quatre parcours navigateur facultatifs, et leurs données de test, se trouvent dans `tests/navigateur/`. |
| Référentiel clinique | `public/js/specialites.js`, partagé par le serveur et les écrans |
| Montants | Entiers en francs CFA. Chaque bon garde le prix de sa date : une modification de tarif ne change jamais les factures passées. |

## 17. Édition autonome (un seul fichier HTML)

`MSI-Gestion.html` contient tout le logiciel : le code du serveur, exécuté dans le navigateur, et SQLite en WebAssembly. Il s’ouvre par double-clic dans **Chrome ou Edge**, sans installation ni internet.

| Point | Édition autonome | Édition serveur (ce dossier) |
|---|---|---|
| Installation | Aucune : double-clic | Node.js, `npm install`, démarrage du serveur |
| Postes | Un ordinateur, un onglet à la fois | Tous les postes du réseau local |
| Données | Dans le navigateur de cet ordinateur, enregistrées à chaque saisie | `donnees/msi.db` sur le serveur |
| Sauvegardes | Téléchargées depuis « Données de cet ordinateur » (en bas à gauche) | Automatiques toutes les 15 minutes, avec copie cloud |
| Règles et verrous | Identiques : même code | Identiques |

- **Première ouverture :** choisir la base réelle ou la base de formation, noter les mots de passe affichés, télécharger la clé de sauvegarde.
- **Chaque soir :** « Données de cet ordinateur », puis « Télécharger une sauvegarde », et garder une copie hors de l’ordinateur. Effacer les données de navigation efface aussi la base.
- **Passer au serveur :** copier `cle-sauvegarde.key` dans `donnees/`, puis lancer `npm run restaurer -- msi-AAAAMMJJ-HHMMSS.msibak`. Dans l’autre sens : « Restaurer une sauvegarde » dans le fichier HTML, avec la sauvegarde et la clé du serveur.
- **Reconstruire le fichier après une mise à jour :** kit `msi-gestion-autonome-sources.zip`, commande `node construire.js`.

## 18. Historique des versions

| Version | Contenu |
|---|---|
| 1.0 | Accueil, caisse, pharmacie, direction, paramétrage, sauvegardes chiffrées |
| 1.1 | Consultations des 13 spécialités |
| 1.2 | Reprise OphtaSuite, photos du dossier, fiches conseils |
| 1.3 | Tiers payant, laboratoire, avances, factures récapitulatives |
| 1.3.1 | Corrections issues de la recette accueil → caisse ; édition autonome en un seul fichier HTML |
| 1.3.2 | Corrections issues de la recette médecin → pharmacie |
| 1.4.0 | Tableau de bord et statistiques de pilotage (courbes, diagrammes, alertes, rapport imprimable), courbes des constantes du patient, barre latérale sur ordinateur |
| 1.5.0 | Infirmerie (constantes et orientation vers le médecin), rendez-vous pris à l’accueil avec message WhatsApp ou SMS, catalogue tenu par le gérant de la pharmacie, tous les documents en A4 |
| 1.6.0 | Notifications en temps réel, constantes anormales signalées en priorité avec spécialiste suggéré, médecin et motif choisis à l’accueil, profil Facturiste |
| 1.7.0 | Hospitalisation : chambres standard et VIP, admission, infirmiers assignés, soins tracés, nuits facturées, quitus de sortie et bon de sortie |
| 1.8.0 | Ressources humaines : personnel, planning des gardes et consultations, paie (gardes et vacations depuis le planning, CNPS, CMU, avances, ITS contrôlé), bulletin et journal de paie |
| 1.9.0 | Tableau de bord personnel du médecin (« Mon activité »), clôture mensuelle du tiers payant par assureur avec rapport et impression groupée des bordereaux |
| 2.0.0 | Édition en ligne : serveur sur Internet derrière un relais HTTPS, connexions non chiffrées refusées, limitation des tentatives par adresse, adresse de santé, kit d’installation et guide de mise en ligne |
| 2.0.1 | Vrai logo de la clinique partout : barre latérale (sur cartouche clair), écran de connexion, reçus, clôture de caisse, rapport de pilotage ; icône d’onglet et icône de l’application aux deux flammes du logo |
| 2.1.0 | Espace comptable : écritures SYSCOHADA générées depuis les opérations, journal, grand livre, balance, plan de correspondance, export CSV ; profil Comptable ; mot de passe visible à la demande |
| 2.2.0 | Suppressions réservées à l’administrateur, sur demande motivée des autres utilisateurs ; consultation validée modifiable par son auteur avec historique ; fiche patient corrigeable par les médecins |
| 2.2.1 | Mise en ligne sans serveur à administrer (Render, en un clic), redirection d’un lien Netlify, avertissement quand l’édition autonome est ouverte depuis un site Internet |
| 2.3.0 | Édition Vercel : base en ligne Turso par un pont synchrone, sans réécriture du code métier (95 scénarios vérifiés à travers le pont) ; point d’entrée et configuration Vercel |

**Corrections de la version 1.3.1** (aucune modification de la base : mise à jour par simple remplacement des fichiers, voir §12) :

- **Accueil :** la consultation se choisit explicitement, sans présélection, et le choix repart à zéro à chaque patient. Les champs manquants sont signalés tous en une fois. Prénoms et téléphone sont mis en forme. Les droits expirés sont annoncés à l’ouverture du passage.
- **Passage identique le jour même :** alerte, second passage seulement sur confirmation, compté à la direction (« Seconds passages identiques »).
- **Annulation d’un passage ouvert par erreur :** à l’accueil, à la caisse ou par la direction, avec motif obligatoire. Elle est tracée au journal et comptée au tableau de bord (« Passages annulés »). Elle est refusée dès qu’un acte est payé, délivré ou commencé, ou qu’une facture existe. Un passage d’un jour précédent ne peut être annulé que par la direction.
- **Caisse :** avant une clôture sans comptage, ou avec un écart d’au moins 5 000 FCFA, le logiciel fait recompter. Les notifications ne masquent plus les boutons.
- **Recette :** 42 scénarios automatiques, 58 étapes navigateur pour l’édition serveur, 16 étapes pour l’édition autonome.

**Corrections de la version 1.3.2** (aucune modification de la base : mise à jour par simple remplacement des fichiers) :

- **Ordonnance complète exigée :** chaque médicament porte une posologie et une durée. Le message nomme la ligne incomplète, par exemple « Posologie (Amoxicilline) : champ obligatoire ». La pharmacie voit désormais la durée, qui lui sert à calculer la quantité à délivrer.
- **Pas de substitution silencieuse à la pharmacie :** la reprise de l’ordonnance exige le même dosage que la prescription. « Paracétamol 1 g » n’est plus repris en « Paracétamol 500 mg ». En cas de dosage différent, un avertissement nominatif reste affiché et le pharmacien décide.
- **Numéro d’inscription à l’Ordre :** en production, le médecin est averti s’il n’est pas renseigné, car il manquerait sur ses ordonnances et certificats.
- **Saisie de l’ordonnance :** la posologie usuelle se remplit sans effacer ce que le médecin est en train de taper. Un même médicament ne peut plus figurer deux fois sur une ordonnance : la posologie se regroupe sur une seule ligne.
- **Réception de marchandise :** « Choisissez le produit reçu » remplace « Produit inconnu » quand aucun produit n’est choisi.
- **Recette :** 45 scénarios automatiques, 58 étapes navigateur pour l’édition serveur, 16 étapes pour l’édition autonome.

## 19. Tableau de bord et statistiques (version 1.4)

Réservés à la direction et au RAF, qui y arrivent à la connexion. Sur ordinateur, les postes s’affichent dans une barre latérale ; sur téléphone, la barre d’onglets reste en bas de l’écran.

- **Tableau de bord :** recettes du jour et courbe des 30 derniers jours ; recettes, chiffre d’affaires, passages et nouveaux patients du mois, comparés au mois dernier à la même date ; créances des assureurs ; chiffre d’affaires et passages des 12 derniers mois ; recettes par service ; modes de paiement ; alertes (validations en attente, ruptures et péremptions, écart de caisse, tarifs à valider, créances de plus de 90 jours), chacune menant à l’écran concerné.
- **Statistiques :** mois en cours, 12 derniers mois, année en cours, année précédente ou depuis le début, comparés à la période précédente. Activité, chiffre d’affaires et cumul, services, modes de paiement, types de passage, spécialités, actes et médicaments, facturé et réglé par assureur, créances par ancienneté, fréquentation par jour et par heure, écarts de caisse. « Imprimer le rapport » en donne une version papier ou PDF.
- **Calcul :** le serveur applique les règles de la caisse (même calcul des parts patient et assureur, mêmes remises). Les reçus, bons et passages annulés, ainsi que les soldes repris de l’ancien logiciel, sont exclus de l’activité. Les recettes du tableau de bord égalent la somme des reçus de la période.
- **Courbes des constantes (médecins) :** dans l’onglet Dossier d’une consultation, tension artérielle, poids, glycémie et température au fil des consultations, avec zones normales et seuils d’alerte.

## 20. Infirmerie, rendez-vous, catalogue et documents A4 (version 1.5)

**Infirmerie.** Le profil « Infirmier ou infirmière » ouvre le poste Infirmerie :

1. Le patient payé à la caisse apparaît dans « Patients du jour », avec le statut « À prendre ».
2. L’infirmier saisit les constantes de la spécialité (tension, pouls, température, saturation, poids, taille, glycémie…). L’IMC se calcule seul et les mêmes alertes que chez le médecin s’affichent.
3. Il note une observation, choisit le médecin qui recevra le patient, puis valide.

Le patient n’apparaît alors que dans la file de ce médecin, avec la mention « Constantes prises par ». À l’ouverture de la consultation, les constantes sont reprises en lecture seule, avec leur auteur, l’heure et l’observation. Le médecin ne complète que ce qui manque, et le formulaire ne peut pas remplacer une valeur de l’infirmier. L’infirmier peut corriger ou réorienter tant que la consultation n’a pas commencé. Comme pour le médecin, un passage non réglé est refusé.

**Rendez-vous et messages.** Sur la fiche du patient, « Prendre un rendez-vous » enregistre la date, l’heure, le médecin, la spécialité et le motif. La fenêtre « Prévenir par message » s’ouvre ensuite, et le bouton « Prévenir » de la liste des rendez-vous la rouvre à tout moment. On y choisit le médecin ou le patient, on modifie le message, puis on l’envoie par WhatsApp ou par SMS : l’application s’ouvre avec le texte prêt, il reste à confirmer l’envoi.

Le téléphone de chaque médecin se saisit dans Paramétrage, Utilisateurs. Un numéro à 10 chiffres est complété automatiquement par l’indicatif 225.

**Catalogue de la pharmacie.** Le profil « Gérant de la pharmacie » dispose de tous les droits de la pharmacie, plus le catalogue : « Ajouter un médicament » et « Modifier », dans Pharmacie, État du stock. Un prix fixé ou modifié par le gérant porte la mention « Prix à valider ». En base réelle, le médicament n’est vendable qu’après validation par la direction, qui ouvre le produit dans Paramétrage, Référentiels, puis l’enregistre. Le médicament est aussitôt disponible pour les ordonnances.

**Documents en A4.** Tout sort en A4 : ordonnances, certificats, comptes rendus, bons d’examens, reçus, factures et bordereaux. Chaque document médical porte l’identité complète de la clinique (raison sociale, capital, adresse, téléphone, RCCM, numéro de compte contribuable), le praticien et son numéro d’Ordre, le lieu, la date et le numéro du document. Il comporte aussi le patient (nom, IPP, sexe, date de naissance et âge, poids et taille s’ils ont été mesurés), une zone de signature et de cachet, et un pied de page.

**Mise à jour depuis la 1.4.** Remplacez les fichiers en gardant le dossier `donnees/` (voir §12). Au démarrage, la base reçoit d’elle-même la table des constantes et le téléphone des comptes. Créez ensuite les comptes de l’infirmerie et du gérant, puis saisissez le téléphone des médecins.

**Recette de la 1.5 :** 54 scénarios automatiques, 58 étapes navigateur pour l’édition serveur, 16 et 6 étapes pour l’édition autonome, 8 étapes pour l’application Android.

## 21. Notifications, alertes infirmières et admission (version 1.6)

**Notifications en temps réel.** La cloche, en haut de la barre latérale ou dans l’en-tête sur téléphone, compte les notifications non lues ; son compteur passe au rouge s’il y a une urgence. Une notification arrivée pendant le travail s’affiche à l’écran, avec un signal sonore (trois notes pour une urgence). Un clic dans la liste ouvre l’écran concerné. « Activer les alertes du navigateur » permet aussi de les recevoir quand MSI Gestion est en arrière-plan.

| Destinataire | Événements signalés |
|---|---|
| Médecin | Nouveau patient en salle d’attente, patient prioritaire (constantes anormales), résultats prêts ou anormaux |
| Infirmier | Patient réglé à prendre en charge, urgence |
| Laboratoire | Examen réglé à réaliser |
| Pharmacie et gérant | Stock bas ou rupture, péremption dans moins de 3 mois, lot périmé à retirer |
| Direction | Demande à valider (remise, annulation de reçu) |

**Alertes infirmières.** Pendant la saisie des constantes, toute valeur anormale (tension élevée, fièvre, hypoxie, hyperglycémie…) affiche un encadré rouge et le spécialiste suggéré : cardiologie pour la tension ou le pouls, diabétologie pour la glycémie, infectiologie pour la fièvre, prise en charge immédiate pour la saturation, pédiatrie pour un enfant de moins de 15 ans. Le patient est alors **prioritaire** : il passe en tête de la file du médecin, marqué en rouge avec ses alertes, et le médecin reçoit une notification prioritaire.

**Admission.** À l’ouverture d’une consultation, l’accueil peut choisir le médecin et saisir le motif. Le médecin est prévenu aussitôt. L’infirmerie le trouve présélectionné et peut le changer, et le motif est déjà rempli dans la consultation.

**Profil Facturiste.** Tiers payant, factures et exports : bordereaux par assureur, règlements, rejets et créances par ancienneté. Il n’a pas accès à la caisse ni aux dossiers médicaux.

**Recette de la 1.6 :** 60 scénarios automatiques, 58 étapes navigateur pour l’édition serveur, 16, 6 et 6 étapes pour l’édition autonome, 8 étapes pour l’application Android.

## 22. Hospitalisation (version 1.7)

**Avant la première admission.** La direction crée les chambres (Paramétrage, Chambres : numéro, nom, catégorie standard ou VIP, nombre de lits), puis valide les tarifs « Journée d’hospitalisation, chambre standard » et « chambre VIP » (Paramétrage, Tarifs des actes). Ces tarifs sont créés automatiquement, y compris lors de la mise à jour d’une base existante.

**Admission.** Depuis la fiche du patient (« Hospitaliser ») ou l’onglet Hospitalisation : motif, médecin référent, chambre libre, infirmiers assignés, accord d’assurance s’il y a lieu. Le séjour est numéroté HOS-AAAA-NNNN et porte un passage de facturation. Le référent, les infirmiers et la caisse sont prévenus ; la caisse encaisse la caution comme une avance.

**Pendant le séjour.** L’onglet affiche le plan des chambres et le taux d’occupation des lits. Le dossier du séjour regroupe les constantes, les soins et les observations, avec leurs auteurs et leurs heures. Des constantes anormales alertent le médecin référent en priorité. Un soin facturable (injection, pansement…) crée un bon sur le séjour. Le séjour reste ouvert à la pharmacie et aux examens jusqu’à la sortie. Aucun soin ne peut être modifié ni supprimé : on ajoute une nouvelle entrée.

**Sortie.** Le médecin prononce la sortie (mode de sortie et compte rendu obligatoires). Les nuits sont alors facturées : une journée par nuit passée, au tarif de la chambre occupée cette nuit-là (transferts compris), une journée au minimum. La chambre est libérée.

**Quitus de sortie (anti-fuite).** Après la sortie médicale, le patient est « en attente de quitus » et la caisse reçoit une notification prioritaire. La caisse ne délivre le quitus qu’une fois la part patient soldée. La direction peut passer outre, avec un motif d’au moins 10 caractères tracé en alerte au journal. Le bon de sortie A4 (identité, séjour, chambres, règlement, quitus, signatures) se remet au contrôle de sortie.

**Accès.** Admission : accueil, médecin, direction. Soins : infirmier, médecin. Infirmiers et transferts : médecin, infirmier, direction. Sortie médicale : médecin, direction. Quitus : caisse, direction.

**Recette de la 1.7 :** 68 scénarios automatiques, dont un garde-fou qui interdit à deux écrans de déclarer le même nom ; 58 étapes navigateur pour l’édition serveur ; 16, 6, 6 et 6 étapes pour l’édition autonome ; 8 étapes pour l’application Android.

## 23. Ressources humaines (version 1.8)

**Personnel.** Chaque employé a une fiche : matricule EMP-NNNN, fonction, service, contrat (CDI, CDD, vacataire, stage), date d’embauche, numéro CNPS, mode de paiement, et éventuellement son compte de connexion. Un CDD exige sa date de fin, et une alerte prévient les RH 30 jours avant. « Reprendre les comptes existants » crée en un clic les fiches du personnel déjà inscrit dans le logiciel. Un départ s’enregistre par l’archivage (date et motif de sortie) ; la fiche reste consultable.

**Planning.** La semaine s’affiche sur 7 colonnes : gardes, consultations, permanences, astreintes, congés et absences. Une garde de nuit (18 h – 8 h) ou de 24 heures se saisit naturellement, et deux créneaux qui se chevauchent pour la même personne sont refusés. « Recopier la semaine précédente » prépare la semaine en un clic, en ignorant les conflits. Le planning s’imprime en A4 paysage. Chaque utilisateur retrouve ses créneaux des 30 prochains jours dans « Mon planning » (menu du compte) et reçoit une notification pour chaque créneau qui le concerne.

**Paie.** Chaque mois, « Préparer la paie » établit un bulletin par employé actif :

| Ligne | Origine |
|---|---|
| Salaire de base | Fiche de l’employé |
| Primes de garde, vacations | Nombre de gardes et de consultations du planning, multiplié par la prime par garde ou le montant par vacation |
| Cotisation retraite CNPS (salariés CDI et CDD) | Taux et plafond des paramètres, sur le brut cotisable (primes comprises) |
| CMU (part salariale) | Paramètres |
| Avances sur salaire | Avances accordées et non encore déduites |
| ITS | Saisi par le comptable : **obligatoire avant validation** pour un salarié, zéro compris si le salaire n’est pas imposable |
| Primes, indemnités, retenues diverses | Lignes libres, tant que le bulletin n’est pas validé |

Le circuit est cloisonné. Les RH ou le RAF préparent, **seule la direction valide**, puis le RAF enregistre le paiement (mode et référence). Un bulletin validé est figé, un bulletin payé ne s’annule plus, et une annulation libère les avances pour la paie suivante. Le bulletin de paie (A4) et le journal de paie du mois s’impriment.

**Paramètres de paie (direction).** Taux de la retraite CNPS, plafond mensuel, part salariale de la CMU et numéro employeur CNPS. Les valeurs proposées (6,3 %, plafond de 1 647 315 FCFA, CMU de 500 FCFA) sont **indicatives : faites-les confirmer par votre expert-comptable avant la première paie réelle**. Le calcul de l’ITS, les charges patronales et les déclarations CNPS et fiscales restent du ressort du comptable.

**Accès.** Consultation : RH, direction, RAF ; les montants des salaires ne sont visibles qu’avec un droit sur la paie. Personnel et planning : RH, direction. Préparation de la paie : RH, RAF, direction. Validation : direction. Paiement : RAF, direction.

**Recette de la 1.8 :** 75 scénarios automatiques ; 58 étapes navigateur pour l’édition serveur ; 16, 6, 6, 6 et 6 étapes pour l’édition autonome ; 8 étapes pour l’application Android.

## 24. Tableau de bord du médecin et clôture mensuelle (version 1.9)

**« Mon activité » (chaque médecin).** Quatre indicateurs : patients reçus aujourd’hui, patients du mois avec l’évolution par rapport au mois précédent, examens demandés avec les résultats reçus, anormaux ou en attente, alertes de l’infirmerie. S’y ajoutent les alertes du jour (infirmerie et hospitalisation), les consultations des 30 derniers jours, les examens les plus demandés, les documents émis et les rendez-vous de la semaine. Le compteur de l’onglet signale les patients en alerte qui attendent encore leur consultation. Chaque médecin ne voit que sa propre activité.

**Clôture mensuelle (Tiers payant, rubrique « Clôture mensuelle »).** Pour le mois choisi, l’écran présente la part assureur restant à facturer, assureur par assureur. « Clôturer le mois » émet en une seule opération un bordereau par assureur. Pour le mois en cours, la clôture couvre jusqu’au jour même ; elle se rejoue en fin de mois sans risque, car seules les prises en charge non encore facturées sont reprises et un acte n’est jamais facturé deux fois. Le rapport de clôture A4 (bordereaux, montants réglés, rejetés et restant dus, répartition par service, signatures) et l’impression groupée de tous les bordereaux du mois préparent l’envoi aux assureurs. Chaque clôture est historisée et ne peut pas être supprimée. Les 10 premiers jours du mois, le facturiste est prévenu si le mois précédent n’est pas entièrement facturé.

**Couverture du cahier des charges.**

| Module | Couvert par |
|---|---|
| A. Accueil et admission | Fiche patient, assurance et parts calculées, médecin et motif, paiement espèces ou mobile money, notification au médecin |
| B. Infirmerie | Constantes, alertes rouges, spécialiste suggéré, priorité et notification au médecin |
| C. Espace médecin | Consultation complète, documents, examens, « Mon activité » |
| D. Laboratoire | Examens payés à réaliser, résultats validés et notifiés au médecin |
| E. Caisse | Encaissements, reçus, avances, clôture de caisse |
| F. Pharmacie | Catalogue tenu par le gérant, stock par lots, péremption à moins de 3 mois, prescriptions |
| G. Hospitalisation | Chambres standard et VIP, infirmiers assignés, soins tracés, nuits facturées, quitus de sortie |
| H. Facturiste | Tiers payant, bordereaux, règlements, rejets, créances, clôture mensuelle |
| I. Administration et RH | Comptes et rôles, personnel, planning, paie, tableau de bord global, journal d’audit |

**Recette de la 1.9 :** 78 scénarios automatiques ; 58 étapes navigateur pour l’édition serveur ; 16, 6, 6, 6, 6 et 4 étapes pour l’édition autonome ; 8 étapes pour l’application Android.

## 25. Édition en ligne (version 2.0)

MSI Gestion s'installe désormais sur un **serveur Internet** : le personnel se connecte depuis n'importe où, par le lien de la clinique (par exemple `https://gestion.innovcare.ci`), et chacun retrouve son espace selon son profil. Le guide complet se trouve dans **`deploiement/MISE-EN-LIGNE.md`** : matériel, hébergement et données de santé, installation pas à pas, sécurité, sauvegardes, mises à jour.

**Ce qui change en mode en ligne** (réglage `MSI_EN_LIGNE=1`, activé d'office dans le conteneur) :
- le serveur fonctionne derrière un relais HTTPS (Caddy), qui obtient et renouvelle le certificat ;
- HTTPS est imposé au navigateur, toute requête non chiffrée est refusée, et le cookie de session n'est envoyé que chiffré ;
- au-delà de 30 échecs de connexion en 15 minutes depuis une même adresse, les tentatives de cette adresse sont suspendues, en plus du blocage par compte ;
- l'adresse `/api/sante` permet la surveillance du serveur, sans aucune donnée.

**Kit d'installation** (dossier `deploiement`) : image Docker, composition serveur et relais, configuration du relais, réglages (`.env.exemple`), installation en une commande sur un serveur Ubuntu neuf, copie nocturne des sauvegardes hors du serveur.

**L'installation locale reste possible** : sans le réglage en ligne, le fonctionnement sur le réseau de la clinique est inchangé.

**Recette de la 2.0 :** 82 scénarios automatiques, dont 4 pour le mode en ligne. Essai de bout en bout avec le relais HTTPS réel : redirection vers HTTPS, protections envoyées au navigateur, accès direct non chiffré refusé, première connexion avec changement de mot de passe imposé, cookie de session sécurisé. Toutes les recettes navigateur précédentes ont été rejouées.

## 26. Espace comptable et mots de passe visibles (version 2.1)

**Principe.** Les écritures comptables sont **générées automatiquement**, selon le plan SYSCOHADA révisé, à partir des opérations déjà enregistrées : rien n’est ressaisi. Comme une opération ne s’efface jamais (une annulation est une nouvelle opération), les écritures d’un mois passé ne changent pas. Les libellés ne portent **aucun nom de patient** : seuls l’IPP et les numéros de pièce apparaissent.

| Opération | Écriture générée (comptes proposés) |
|---|---|
| Reçu | Crédit des produits par service : 7061 consultations, 7062 laboratoire, 7063 imagerie, 7064 hospitalisation, 7065 soins et autres actes, 701 pharmacie. Débit de la trésorerie selon le mode (5711 caisse, 5521 à 5524 Orange Money, MTN MoMo, Moov Money et Wave, 5211 banque, 5131 chèques), de 4111 pour la part assureur (tiers : l’assureur) et de 709 pour la remise |
| Annulation, puis remboursement | Contre-passation de la vente, part patient en avoir à rembourser (4198), soldé par le remboursement en espèces |
| Avance d’un patient | Dépôt : trésorerie contre 4191 ; remboursement : 4191 contre trésorerie (son utilisation figure dans le reçu) |
| Sortie de caisse | Compte de la catégorie (60 → 605, 61 → 618, 62 → 624, 63 → 638, 64 → 648, 65 → 658, 66 → 668) contre caisse |
| Écart de caisse | Manquant : 658 ; excédent : 758 |
| Assureurs | Règlement : trésorerie contre 4111 ; rejet : 651 contre 4111, daté du dernier règlement du bordereau |
| Achats de la pharmacie | 601 contre 401 (tiers : le fournisseur), au prix d’achat de la réception |
| Paie | Bulletin validé : 6611 au débit ; au crédit 4313 (retraite CNPS), 433 (CMU), 4472 (ITS), 421 (avances) et 422 (net dû). Paiement : 422 contre trésorerie. Avance sur salaire : 421 contre caisse |

**Les cinq rubriques** (onglet Comptabilité, sur la période choisie : ce mois, mois précédent, cette année ou dates libres) :
- **Synthèse** : produits, charges, résultat provisoire, créances sur les assureurs, contrôle d’équilibre, répartition par compte ;
- **Journal** : toutes les écritures, filtrables par journal (ventes, trésorerie, achats, paie, opérations diverses), imprimables en A4 ;
- **Grand livre** : les mouvements d’un compte, avec le solde progressif ;
- **Balance** : débit, crédit et soldes par compte, imprimable ;
- **Plan comptable** : la correspondance entre chaque opération et son compte, modifiable par le comptable et la direction, tracée au journal d’audit.

**Recalcul et export.** Les écritures se recalculent au changement de période, après une modification du plan, ou par le bouton « Actualiser ». « Exporter les écritures (CSV) » produit un fichier lisible dans Excel (accents corrects) et importable par le logiciel du comptable. Ses colonnes : Date, Journal, Pièce, Compte, Libellé du compte, Tiers, Libellé, Débit, Crédit.

**Accès.** Consultation : comptable, RAF, direction. Modification du plan : comptable et direction. Le profil Comptable n’a aucun accès aux dossiers médicaux, à la caisse ni à la pharmacie.

**À valider par l’expert-comptable :** les comptes proposés, modifiables dans le plan. Restent de son ressort : les écritures d’inventaire (variation de stock, amortissements, provisions), les charges patronales et les déclarations. Un avoir remboursé autrement qu’en espèces reste sur 4198 jusqu’à son lettrage.

**Mots de passe visibles.** Chaque champ de mot de passe porte un bouton « œil » qui affiche ou masque la saisie, sans perdre le curseur. Cela vaut pour la connexion, le changement imposé, « Mon compte » et l’édition HTML.

**Recette de la 2.1 :** 87 scénarios automatiques, dont 5 pour la comptabilité, sur les deux moteurs ; 58 étapes navigateur pour l’édition serveur ; 16, 6, 6, 6, 6, 4 et 5 étapes pour l’édition autonome ; 8 étapes pour l’application Android.

## 27. Suppressions réservées à l’administrateur et modification des dossiers (version 2.2)

**Seul l’administrateur supprime.** Les autres utilisateurs n’ont plus de bouton de suppression : ils voient « Demander l’annulation » ou « Signaler un doublon ». La demande part à l’administrateur avec un **motif obligatoire**, saisi avant l’envoi : le bouton d’envoi reste grisé tant que le motif fait moins de 10 caractères. Rien n’est modifié avant la décision.

| Élément | Demandé par | Effet de l’acceptation |
|---|---|---|
| Passage ouvert par erreur | Accueil, caisse | Bons non payés annulés : le passage ne compte plus (caisse, statistiques, comptabilité). **En attendant la décision, il ne peut pas être encaissé.** Un passage déjà payé relève de l’annulation du reçu. |
| Dossier patient en double | Tout utilisateur | Fusion dans le dossier à conserver, après vérification de son IPP |
| Créneau de planning | Ressources humaines | Créneau annulé : il ne compte plus dans les gardes et vacations |
| Bulletin de paie (préparé ou validé) | Ressources humaines, RAF | Bulletin annulé ; ses avances reviennent sur la paie suivante |
| Bordereau d’assureur (non réglé) | Facturiste, RAF | Bordereau annulé ; ses actes redeviennent facturables |
| Reçu (demande faite à la caisse) | Caisse | Avoir émis selon les règles habituelles |

**Rien n’est effacé physiquement :** l’élément accepté est annulé, cesse de compter et reste dans l’historique avec la demande, son motif et la décision.

**Écran de l’administrateur.** L’onglet « Suppressions » liste les demandes en attente, chacune avec son motif, son auteur et son heure, puis les décisions des 30 derniers jours. « Accepter et supprimer » exécute l’opération. « Refuser » exige une raison, transmise au demandeur. L’administrateur est prévenu de chaque demande, et chaque demandeur de la décision (en priorité s’il s’agit d’un refus).

**Changement de contrôle financier :** l’annulation des reçus, auparavant validée par la direction, est désormais décidée par l’administrateur, conformément à la règle « toute suppression passe par l’administrateur ». Les remises restent validées par la direction.

**Consultation validée modifiable par son auteur.** Le médecin qui a réalisé la consultation peut la rouvrir avec « Modifier la consultation », puis l’enregistrer avec un **motif obligatoire**. La version précédente est conservée dans un historique que la base de données interdit de modifier ou d’effacer, et la consultation affiche « Modifiée après validation » avec la date, l’auteur et le motif de chaque modification. Les documents déjà remis au patient ne changent pas, et les constantes prises par l’infirmerie restent celles de l’infirmier.

**Fiche du patient.** Les médecins peuvent corriger la fiche administrative (identité, date de naissance, téléphone, assurance) depuis la consultation, avec « Modifier la fiche du patient ». Chaque modification est journalisée avec l’ancienne et la nouvelle valeur.

**Recette de la 2.2 :** 94 scénarios automatiques sur les deux moteurs ; 58 étapes navigateur pour l’édition serveur ; 16, 6, 6, 6, 6, 4, 5 et 6 étapes pour l’édition autonome ; 8 étapes pour l’application Android.

## 28. Mise en ligne sans serveur à administrer (version 2.2.1)

**Édition autonome ou édition serveur.** Le fichier `MSI-Gestion.html` (édition autonome) et l’application Android enregistrent les données **sur l’appareil où ils s’ouvrent**. Déposé sur un site comme Netlify, ce fichier ne partage rien : chaque appareil y crée sa propre base, et un compte créé sur un ordinateur n’existe pas sur un autre. Pour que tout le personnel se connecte avec **un seul lien** et **les mêmes comptes**, il faut l’édition serveur, sur un hébergeur qui l’exécute.

Désormais, l’édition autonome ouverte depuis un site Internet affiche cet avertissement en tête de son premier écran.

**Render, depuis le navigateur.** Le fichier `render.yaml` permet un déploiement en un clic : serveur à Francfort, disque persistant de 5 Go pour la base, HTTPS automatique, contrôle de santé sur `/api/sante`. Le guide **`deploiement/RENDER.md`** décrit, sans ligne de commande :
- le dépôt du logiciel sur GitHub et la mise en ligne ;
- la lecture du mot de passe provisoire de l’administrateur et la récupération de la clé de sauvegarde ;
- la création des comptes et l’envoi du lien ;
- la connexion des téléphones, par le navigateur ou par l’application Android.

**Garder un lien déjà diffusé.** Le dossier `deploiement/netlify-redirection` renvoie un site Netlify vers le vrai serveur : on y indique l’adresse du serveur, puis on le glisse sur Netlify.

**Côté technique.** Le serveur écoute sur le port imposé par l’hébergeur (variable `PORT`). L’image démarre en administrateur système pour préparer le disque des données, puis le serveur tourne sous un utilisateur restreint. Ces deux points ont été vérifiés en simulation, avec le mode en ligne : HTTPS imposé et accès non chiffré refusé.

## 29. Édition Vercel avec la base Turso (version 2.3.0)

Le serveur parle à sa base de façon synchrone. Pour une base en ligne, `serveur/pont-libsql.js` conserve cette interface : chaque requête passe par un fil d’exécution secondaire, qui interroge **Turso** avec son client officiel. Le **code métier reste inchangé**, et le moteur est choisi selon l’adresse de la base : fichier local (better-sqlite3) ou adresse en ligne (pont).

**Vérifications :**
- les **95 scénarios** automatiques passent à travers le pont, y compris la sauvegarde chiffrée restaurable par reconstruction de la base, table par table ;
- ils passent aussi sur le moteur habituel et sur le moteur du navigateur ;
- une simulation de la fonction Vercel a été jouée : premier démarrage, mot de passe provisoire choisi et changement imposé, HTTPS obligatoire, aucun fichier du projet exposé.

**Mise en ligne :** voir `deploiement/VERCEL.md` (`vercel.json`, `api/index.js`).

**À venir :** sauvegardes chiffrées automatiques vers le stockage de Vercel.
