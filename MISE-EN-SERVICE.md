# Dossier de mise en service, MSI Gestion 2.2.1

Ce dossier organise le passage du classeur actuel à MSI Gestion, sans perte de recette et sans interruption de l’accueil. Le démarrage se décide sur **un critère unique** : une recette de 200 passages sans aucun écart (§ 2).

---

## 1. Check-list avant démarrage

| N° | Étape | Responsable | Fait |
|---|---|---|---|
| 1 | Serveur installé, onduleur, adresse IP fixe, démarrage automatique testé (README § 2) | Technicien | ☐ |
| 2 | HTTPS activé et certificat accepté sur chaque poste (README § 4) | Technicien | ☐ |
| 3 | Sauvegarde cloud configurée ; clé de sauvegarde copiée sur 2 clés USB (coffre, gérant) | Technicien et gérant | ☐ |
| 4 | Test de restauration réussi sur une copie (README § 6) | Technicien | ☐ |
| 5 | Première connexion `admin`, mot de passe personnel choisi | Gérant | ☐ |
| 6 | Paramètres vérifiés : identité légale, plafond de remise, délai du contrôle gratuit, seuil d’ajustement, horaires des vacations | Direction | ☐ |
| 7 | **Chaque tarif d’acte vérifié et validé** (ou import de la grille réelle) : la facturation reste bloquée sinon | RAF et direction | ☐ |
| 8 | Liste des 27 assureurs complétée, avec le niveau de prix de chacun (assurances majeures ou autres) | RAF | ☐ |
| 9 | Inventaire physique de la pharmacie, puis import du catalogue et du stock initial par lot (modèle CSV) | Pharmacie et RAF | ☐ |
| 10 | Un compte par agent, profils conformes (jamais caisse et pharmacie ensemble) ; mots de passe remis en main propre | Administrateur | ☐ |
| 11 | Formation de chaque agent sur la **base de formation** (1 h 30 par poste) | Direction | ☐ |
| 12 | Recette des 200 passages validée (§ 2) | Direction | ☐ |
| 13 | Formalités ARTCI vérifiées avec le conseil (README § 12) | Gérant | ☐ |
| 14 | Imprimante thermique réglée : 80 mm, marges nulles, échelle 100 % | Technicien | ☐ |
| 15 | Comptes médecins créés, avec leurs spécialités et leur n° d’inscription à l’Ordre | Administrateur | ☐ |
| 16 | Tarifs des 7 nouvelles consultations et des 11 examens d’ophtalmologie validés | Direction | ☐ |
| 17 | **Référentiel de chaque spécialité relu par le médecin concerné** : suggestions, examens, modèles, posologies indicatives | Chaque spécialiste | ☐ |
| 18 | Imprimante A5 ou A4 réglée pour les ordonnances et certificats (échelle 100 %) | Technicien | ☐ |
| 19 | Reprise d’OphtaSuite : sauvegarde exportée, analysée puis importée la veille de la bascule ; 10 dossiers repris contrôlés au hasard | Ophtalmologue | ☐ |
| 20 | Fiches conseils relues par chaque spécialiste (textes remis aux patients) | Chaque spécialiste | ☐ |
| 21 | Valeurs de référence du laboratoire relues et validées ; compte laboratoire créé | Biologiste | ☐ |
| 22 | Premier bordereau de chaque assureur contrôlé ligne à ligne avant envoi | RAF | ☐ |
| 23 | Circuit des avances expliqué à la caisse : dépôt, utilisation, remboursement validé par la direction | Direction | ☐ |

## 2. Recette par le personnel

La recette se fait sur la **base de formation**, pendant **deux vacations complètes** (jour et garde), avec les agents qui utiliseront l’application.

**Critère d’acceptation :** 200 passages saisis, **zéro écart** entre les actes réalisés, les bons, les reçus et la caisse comptée, et aucune délivrance sans paiement hors urgence.

| N° | Scénario | Résultat attendu |
|---|---|---|
| 1 | Patient assuré avec n° d’accord | Part patient seule à la caisse ; reçu avec la couverture et le n° d’accord |
| 2 | Patient assuré sans n° d’accord, puis accord saisi à la caisse | D’abord facturé comme non assuré, puis recalculé dès la saisie de l’accord |
| 3 | Contrôle dans les 15 jours | Bon gratuit, rien à payer ; au-delà du délai, tarif normal |
| 4 | Paiement mixte (espèces et mobile money) | Référence obligatoire ; une référence déjà utilisée est refusée |
| 5 | Remise au-delà du plafond | Bons bloqués jusqu’à la décision d’un autre membre de la direction |
| 6 | Ordonnance présentée à la pharmacie avant paiement | Délivrance refusée, tentative visible dans les contrôles anti-fuite |
| 7 | Urgence | Soins et produits délivrés avant paiement ; « à régulariser » suivi jusqu’à l’encaissement |
| 8 | Annulation d’un reçu | Avoir numéroté après validation ; remboursement tracé |
| 9 | Clôture avec un écart | Justification exigée, écart transmis à la direction, caisse figée |
| 10 | Lot périmé en stock | Jamais délivré ; le lot qui expire en premier sort d’abord |
| 11 | Patient en consultation avant paiement | Consultation bloquée pour le médecin, déblocage automatique après encaissement |
| 12 | Examens prescrits | Examens réalisés à MSI envoyés à la caisse ; examens extérieurs seulement imprimés |
| 13 | Ordonnance du médecin présentée à la pharmacie | Reprise d’un clic, sans aucun diagnostic visible |
| 14 | Consultation validée | Non modifiable ; précision par note complémentaire |
| 15 | Examen de laboratoire non réglé | Saisie du résultat refusée ; après paiement, valeur hors normes signalée, résultat validé visible du médecin |
| 16 | Avance du patient | Paiement plafonné au solde ; remboursement seulement après validation de la direction ; caisse juste au franc près |
| 17 | Bordereau assureur | Un acte facturé une seule fois ; règlement plafonné au reste dû ; rejet motivé |
| 18 | Facture récapitulative d’un passage ancien | Établie, numérotée, figée |
| 19 | Passage ouvert deux fois (double clic, double saisie) | Alerte « Passage déjà ouvert » ; un second passage seulement sur confirmation, signalé à la direction |
| 20 | Passage ouvert par erreur, patient reparti sans être vu | Annulation motivée à l’accueil ou à la caisse ; patient retiré de la file ; refusée dès qu’un acte est payé, délivré ou commencé |
| 21 | Clôture sans avoir saisi le billetage | Le logiciel fait recompter avant d’accepter la clôture |
| 22 | Ordonnance sans posologie ou sans durée | Émission refusée, la ligne incomplète est nommée |
| 23 | Ordonnance « Paracétamol 1 g » reprise à la pharmacie, seul le 500 mg en stock | Rien n’est ajouté d’office : avertissement nominatif, le pharmacien décide et en informe le patient |
| 24 | Même médicament saisi deux fois sur une ordonnance | Émission refusée : la posologie se regroupe sur une seule ligne |
| 25 | Direction : recettes du tableau de bord comparées aux reçus de la journée | Montants identiques ; rapport de la période imprimable |
| 26 | Patient payé, constantes prises à l’infirmerie puis orientation vers un médecin | Le patient n’apparaît que dans la file de ce médecin ; constantes reprises en lecture seule dans la consultation |
| 27 | Constantes demandées pour un passage non réglé | Refusé : « envoyez d’abord le patient à la caisse » |
| 28 | Rendez-vous pris à l’accueil, médecin prévenu | Message personnalisé modifiable ; WhatsApp ou SMS s’ouvre avec le texte prêt |
| 29 | Médicament ajouté par le gérant de la pharmacie | Visible au stock avec « Prix à valider » ; vendable après validation par la direction |
| 30 | Ordonnance, reçu et facture imprimés | Format A4, en-tête complet de la clinique, identité du patient et du praticien |
| 31 | Tension 165/105 saisie à l’infirmerie | Encadré rouge, cardiologie suggérée ; patient prioritaire en tête de la file du médecin, notification prioritaire |
| 32 | Médecin et motif choisis à l’accueil | Médecin prévenu ; médecin présélectionné à l’infirmerie ; motif pré-rempli dans la consultation |
| 33 | Résultat de laboratoire hors normes validé | Notification « Résultats anormaux » au médecin |
| 34 | Lot qui périme dans moins de 3 mois | Notification au gérant et à la pharmacie ; lot périmé signalé « à retirer » |
| 35 | Connexion du facturiste | Arrivée sur le tiers payant ; caisse et dossiers médicaux inaccessibles |
| 36 | Admission en chambre standard avec un infirmier assigné | Séjour HOS- numéroté ; chambre occupée sur le plan ; référent, infirmier et caisse prévenus |
| 37 | Tension anormale saisie pendant le séjour | Alerte prioritaire au médecin référent ; entrée visible dans l’historique des soins |
| 38 | Soin facturable ajouté le lendemain de l’admission | Bon créé sur le séjour ; médicaments et examens toujours possibles |
| 39 | Sortie prononcée après un transfert en VIP | Nuits facturées au tarif de chaque chambre occupée ; chambre libérée |
| 40 | Quitus demandé avant paiement | Refusé avec le reste à payer ; accordé après encaissement ; bon de sortie A4 imprimable |
| 41 | Quitus forcé par la direction | Motif obligatoire, alerte tracée au journal |
| 42 | Nouvel employé en CDD | Matricule attribué ; date de fin exigée ; alerte 30 jours avant l’échéance |
| 43 | Deux créneaux qui se chevauchent pour la même personne | Second créneau refusé, avec le créneau en conflit |
| 44 | Paie préparée pour un médecin ayant assuré 3 gardes et reçu une avance | Gardes comptées depuis le planning, CNPS et CMU retenues, avance déduite |
| 45 | Validation demandée sans ITS saisi | Refusée, avec le nom des salariés concernés ; acceptée après saisie (zéro compris) |
| 46 | Bulletin validé puis modifié | Refusé : bulletin figé ; paiement enregistré avec mode et référence |
| 47 | « Mon planning » ouvert par un médecin | Ses créneaux des 30 prochains jours |
| 48 | Constantes anormales prises pour un patient du médecin | Alerte « en attente de consultation » dans « Mon activité », compteur de l’onglet ; « patient reçu » après la consultation |
| 49 | Clôture mensuelle lancée par le facturiste | Un bordereau par assureur ; plus rien à facturer pour le mois ; opération tracée |
| 50 | Clôture relancée après une prise en charge tardive | Seule la nouvelle prise en charge est facturée ; aucun acte facturé deux fois |
| 51 | Rapport de clôture et impression des bordereaux | Rapport A4 complet (répartition par service, signatures) ; tous les bordereaux du mois imprimés, un par page |
| 52 | Connexion depuis un téléphone en 4G, hors de la clinique, par le lien https:// | Écran de connexion ; chaque profil retrouve son espace |
| 53 | Saisie de l’adresse en http:// | Redirection automatique vers https:// |
| 54 | Premier démarrage du serveur en ligne | Mot de passe administrateur provisoire dans le journal ; changement imposé à la première connexion |
| 55 | Copie nocturne des sauvegardes | Sauvegardes chiffrées présentes sur le stockage distant le lendemain matin |
| 56 | Surveillance de /api/sante | Réponse « ok » ; alerte reçue si le serveur est arrêté |
| 57 | Mot de passe saisi puis vérifié avec l’œil | Saisie affichée puis masquée, sans perdre le curseur |
| 58 | Consultation d’un patient assuré payée en mobile money | Écriture : produit 7061, part assureur sur 4111 (tiers : l’assureur), part patient sur le compte du mobile money |
| 59 | Sortie de caisse, réception de médicaments, paie validée puis payée | Charges (compte de la catégorie, 601, 6611) et dettes (401, 4313, 433, 4472, 422) ; paiement en banque |
| 60 | Balance de la période consultée par le comptable | Total des débits égal au total des crédits ; contrôle d’équilibre affiché |
| 61 | Export des écritures | Fichier CSV lisible dans Excel (accents corrects), importable par le logiciel du comptable |
| 62 | L’accueil demande l’annulation d’un passage ouvert par erreur | Envoi impossible sous 10 caractères de motif ; demande envoyée à l’administrateur |
| 63 | La caisse tente d’encaisser ce passage | Refusé : encaissement suspendu jusqu’à la décision ; passage marqué « Annulation demandée » |
| 64 | L’administrateur accepte la demande | Passage annulé, il ne compte plus ; décision historisée ; demandeur prévenu |
| 65 | L’administrateur refuse une demande | Raison obligatoire, transmise au demandeur ; élément intact |
| 66 | Un médecin modifie sa consultation validée | Motif obligatoire ; version précédente conservée ; « Modifiée après validation » affiché |
| 67 | Un médecin corrige la fiche d’un patient | Modification enregistrée et journalisée |

La recette automatique (`npm test`, 95 scénarios) et les parcours navigateur (58 étapes, tous les profils) vérifient déjà ces règles. La recette par le personnel valide, en plus, l’organisation réelle du travail.

## 3. Jour de bascule

- **Moment :** en début de permanence de jour, un jour de faible affluence.
- **Caisses :** l’ancienne caisse est clôturée à 8 h ; la première caisse MSI Gestion est ouverte avec le fonds compté.
- **Ophtalmologie :** reprise d’OphtaSuite la veille (étape 19). OphtaSuite est ensuite conservé en consultation seule, sans nouvelle saisie.
- **Impayés antérieurs :** ils restent suivis dans le classeur actuel jusqu’à leur règlement, car la version 1.0 n’importe pas l’existant (voir § 5).
- **Contrôles gratuits :** pendant les 15 premiers jours, les contrôles se vérifient sur l’ancien registre, car l’historique des consultations démarre avec l’application.
- **Accompagnement :** la direction consulte les contrôles anti-fuite à midi et à 18 h pendant la première semaine.
- **Plan de repli :** si le serveur est indisponible plus de 30 minutes, les agents reviennent au registre papier numéroté, puis les opérations sont ressaisies au retour du service.

## 4. Matrice de traçabilité des exigences de la phase 1

**Légende :** Couvert = exigence réalisée ; Partiel = cœur réalisé, compléments indiqués ; Reporté = phase ultérieure.

### Accueil

| Exigence | Statut | Réalisation dans la version 1.0 |
|---|---|---|
| ACC-01 Recherche et doublons | Partiel | Nom, téléphone, IPP, date de naissance, doublons probables. La lecture du QR code arrive avec la carte patient (ACC-11, phase 2). |
| ACC-02 Dossier administratif | Partiel | Identité, sexe, naissance, téléphone, commune, personne à prévenir ; prénoms et téléphone mis en forme automatiquement. Employeur, photo et second téléphone sont reportés. |
| ACC-03 IPP permanent | Couvert | P-000001, continu, jamais réattribué |
| ACC-04 Couvertures | Partiel | Assureur, n° d’assuré, taux, validité. Souscripteur, plafond et ayants droit sont reportés. |
| ACC-05 Accord assurance | Partiel | N° d’accord, date de saisie, recalcul automatique. Montant accordé et pièce scannée sont reportés. |
| ACC-06 Ouverture du passage | Partiel | 6 types de passage ; spécialité choisie explicitement ; alerte si un passage identique est déjà ouvert le jour même ; annulation motivée d’un passage ouvert par erreur. Le choix du médecin arrive en phase 2. |
| ACC-07 Bon de consultation | Couvert | Selon le tarif et la catégorie du patient |
| ACC-08 Files d’attente | Partiel | File de caisse en temps réel. Files par service et par médecin en phase 2. |
| ACC-09 Alertes | Partiel | Impayé antérieur, droits expirés, doublon, passage identique déjà ouvert. Plafond atteint reporté. |
| ACC-10 Historique | Couvert | Passages, bons, accords, statut de paiement |

### Caisse

| Exigence | Statut | Réalisation dans la version 1.0 |
|---|---|---|
| CAI-01 Bons en temps réel | Partiel | Bons créés par l’accueil, la pharmacie et la caisse (prescriptions papier). Médecins, soins et laboratoire en phase 2. |
| CAI-02 Part patient et part assureur | Couvert | Calcul automatique, recalcul à l’ajout d’un accord |
| CAI-03 Paiement total, partiel, mixte | Couvert | 8 modes ; paiement partiel par sélection des bons |
| CAI-04 Référence obligatoire | Couvert | Référence exigée hors espèces **et refusée si déjà utilisée** |
| CAI-05 Reçu | Couvert | Numéro continu, QR, détail, mentions légales, code de contrôle vérifiable |
| CAI-06 Session par agent et vacation | Couvert | Fonds, billetage, écart justifié, recomptage demandé si rien n’est compté ou si l’écart atteint 5 000 FCFA, passation |
| CAI-07 Facture récapitulative | Couvert | Par passage, numérotée, figée, au nom du patient, d’un employeur ou d’un organisme ; la facture à l’assureur est le bordereau |
| CAI-08 Remises plafonnées | Couvert | Plafond global paramétrable ; au-delà, validation par un autre membre de la direction. Plafond par profil reporté. |
| CAI-09 Annulation par avoir | Couvert | Avoir numéroté après validation ; jamais de suppression |
| CAI-10 Avances et impayés | Couvert | Impayés suivis ; avances numérotées, utilisées dans la limite du solde, remboursées après validation de la direction |
| CAI-11 Journal et dépenses SYSCOHADA | Couvert | Comptes 60 à 66, n° de justificatif obligatoire, export |
| CAI-12 Contrôle gratuit | Couvert | Automatique dans le délai paramétré, par spécialité |

### Pharmacie

| Exigence | Statut | Réalisation dans la version 1.0 |
|---|---|---|
| PHA-01 Catalogue | Partiel | Tenu par le gérant de la pharmacie, prix validés par la direction : code, nom, DCI, forme et dosage, famille, seuil. Conditionnement et fournisseur attitré reportés. |
| PHA-02 Trois niveaux de prix | Couvert | Assurances majeures, autres assurances, non assurés ; prix jamais modifiable au comptoir |
| PHA-03 Lots et péremption | Couvert | Sortie du lot qui expire en premier ; lot périmé bloqué |
| PHA-04 Dispensation | Couvert | Ordonnance du médecin reprise d’un clic, à dosage identique, sans substitution silencieuse ; ordonnance extérieure saisie au comptoir ; délivrance seulement après paiement, lot le plus proche de la péremption servi en premier |
| PHA-05 Vente comptoir | Couvert | Tarif non assurés ; prescripteur exigé pour les psychotropes |
| PHA-06 Approvisionnement | Partiel | Réception contrôlée (lot, péremption, prix d’achat). Proposition et bon de commande reportés. |
| PHA-07 Sorties internes | Couvert | Imputées au service destinataire |
| PHA-08 Alertes | Partiel | Rupture, sous le seuil, péremption à 30 et 90 jours, périmés. Produits dormants reportés. |
| PHA-09 Inventaires | Partiel | Ajustements valorisés ; validation de la direction au-delà du seuil. Session d’inventaire complet reportée. |
| PHA-10 Retours, casse, périmés | Couvert | Avec motif obligatoire |
| PHA-11 Registre des psychotropes | Couvert | Tenu automatiquement, exportable |

### Administration et assureurs

| Exigence | Statut | Réalisation dans la version 1.0 |
|---|---|---|
| ADM-01 Référentiel des actes | Partiel | Code, libellé, famille, spécialité. Cotation et consommables associés reportés. |
| ADM-02 Grilles tarifaires | Partiel | 3 catégories ; les factures passées ne changent jamais. Catégories entreprises et personnel, et dates d’effet, reportées. |
| ADM-03 à ADM-05 Médecins et honoraires | Reporté | Avec le parcours clinique (phase 2) |
| ADM-06 Utilisateurs et droits | Couvert | 6 profils, moindre privilège, séparation caisse et pharmacie |
| ADM-07 Modèles de documents | Partiel | Identité légale paramétrable sur les reçus. Modèles par spécialité en phase 2. |
| ADM-08 Référentiels généraux | Partiel | Catégories SYSCOHADA. Services, salles et fournisseurs structurés reportés. |
| ASS-01 Référentiel des assureurs | Partiel | Nom, niveau de prix, statut de convention. Contacts et délais reportés. |
| ASS-04 Accords | Partiel | N° d’accord (voir ACC-05) |
| ASS-09 Rapport des tiers payants | Couvert | Export par assureur, en remplacement du classeur |
| ASS-05 à ASS-08 | Couvert | Bordereaux numérotés et figés par assureur, export Excel, règlements lettrés, rejets motivés, annulation par la direction, balance âgée |
| ASS-02, ASS-03 | Reporté | Conventions détaillées et lettres-clés |

### Règles de gestion et verrous anti-fuite

| Règle | Statut | Mise en œuvre |
|---|---|---|
| RG-ACC-1 Un patient, un IPP | Couvert | Doublon signalé ; fusion réservée à la direction et tracée |
| RG-ACC-2 Identité provisoire en urgence | Couvert | Dossier « provisoire », signalé jusqu’à complétude |
| RG-ACC-3 Sans accord, non assuré | Couvert | Dérogation tracée non disponible en version 1.0 |
| RG-PHA-1 à RG-PHA-4 | Couvert | Blocage sans paiement, séparation encaisser et délivrer, prix automatique, périmés bloqués, validation des gros ajustements |
| RG-CAI-1 à RG-CAI-4 | Couvert | Pour la pharmacie ; les autres services exécutants arrivent en phase 2 |
| RG-ASS-1 Part assureur | Couvert | Convention active et accord valide à la date du passage |
| RG-ADM-1 Tarifs sans effet rétroactif | Partiel | Prix figé dans chaque bon ; dates d’effet reportées |
| RG-ADM-3 Paramètres sensibles | Partiel | Réservés à la direction et au RAF, journalisés avant et après. Double validation des tarifs reportée. |
| Verrous 1, 2, 5, 6, 7 | Couvert | Passage et bon obligatoires, blocage à l’exécution, séparation des fonctions, journal inviolable, numérotation continue et clôture par vacation |
| Verrous 3 et 4 | Partiel | Contrôles quotidiens au tableau de bord, dont les examens payés non réalisés. Consommation théorique des réactifs reportée. |

## 5. Module Consultations : ce qui est repris d’OphtaSuite et ce qui est retiré

### Repris pour l’ophtalmologie

- **Formulaire complet :**
  - antécédents, dont les traumatismes et le port de verres ;
  - constantes ;
  - acuité visuelle de loin, de près et au trou sténopéique, par œil ;
  - tension oculaire et pachymétrie ;
  - segment antérieur et fond d’œil, avec leurs constats.
- **Référentiels :** suggestions, diagnostics et conduites à tenir.
- **Examens :** les 15 examens, dont 11 facturés aux tarifs d’OphtaSuite.
- **Documents :**
  - comptes rendus de champ visuel, d’OCT, de fond d’œil et de PIO, avec les modèles normal et glaucomateux ;
  - comptes rendus opératoires de cataracte et de ptérygion ;
  - certificats ;
  - ordonnance de lunettes.
- **Médicaments :** les 129 du référentiel, avec leur posologie indicative.
- **Bilan biologique :** le bulletin de biologie MSI.
- **Depuis la version 1.2 :**
  - les 12 fiches conseils ;
  - les photos du dossier ;
  - la reprise des dossiers existants (patients, consultations, documents, photos, rendez-vous à venir).

### Retiré, et pourquoi

| Élément d’OphtaSuite | Raison |
|---|---|
| Fichier patients, tarifs, stock | Déjà gérés par l’accueil, la caisse et la pharmacie : un seul IPP, un seul tarif, un seul stock |
| Stockage en ligne (JSONBin) et envoi par WhatsApp | Les données de santé restent sur le serveur de la clinique |
| Images de signature et de cachet du médecin | Elles permettraient à tout utilisateur de produire un document « signé » : la signature et le cachet restent manuels |
| Nom de médecin inscrit dans les modèles | Le prescripteur est toujours le médecin connecté |
| Statistiques et fichier des médecins | Couverts par la direction et le paramétrage |
| Tracé du schéma du fond d’œil | Commentaires et photo du schéma repris ; le tracé lui-même n’est pas repris |
| Encyclopédie des pathologies | Reportée à une version ultérieure |

### Autres spécialités

Médecine générale, cardiologie, rhumatologie, néphrologie, dermatologie, diabétologie, infectiologie, pédiatrie médicale, chirurgie pédiatrique, gynécologie-obstétrique, psychiatrie et psychologie suivent la même structure, avec leur propre contenu.

Chaque spécialité a en outre ses outils :

| Spécialité | Outils propres |
|---|---|
| Cardiologie | TA aux deux bras, interprétation d’ECG et d’échocardiographie |
| Gynécologie-obstétrique | Terme et date prévue d’accouchement calculés |
| Pédiatrie | Signes généraux de danger, posologies rapportées au poids |
| Psychiatrie et psychologie | Évaluation du risque suicidaire |
| Psychologie | Pas d’ordonnance |

Le contenu de ces spécialités est une base de départ : **chaque spécialiste doit le relire avant la mise en service** (étape 17).

## 6. Limites connues de la version 2.2.0

- **Suppressions :** l’annulation des reçus est désormais décidée par l’administrateur (auparavant par la direction). Seul l’auteur d’une consultation validée peut la modifier ; un confrère ajoute une note complémentaire.
- **Comptabilité :** les comptes proposés sont à valider par l’expert-comptable. Les écritures d’inventaire (variation de stock, amortissements, provisions), les charges patronales et les déclarations restent hors du logiciel. Les rejets des assureurs sont datés du dernier règlement du bordereau. Un avoir remboursé autrement qu’en espèces reste sur 4198 jusqu’à son lettrage par le comptable.
- **Édition en ligne :** la clinique dépend d’Internet (prévoir une box 4G de secours et une procédure papier). L’hébergement des données de santé demande l’autorisation de l’ARTCI, et une autorisation de transfert si le serveur est à l’étranger (voir `deploiement/MISE-EN-LIGNE.md`). L’édition locale n’est pas synchronisée avec le serveur en ligne.
- **Paie :** les taux proposés (retraite CNPS, plafond, CMU) sont indicatifs et à confirmer par l’expert-comptable. L’ITS est saisi par le comptable (le logiciel exige seulement qu’il soit renseigné). Les charges patronales et les déclarations CNPS et fiscales sont établies hors du logiciel.
- **Cahier des charges :** tous les modules sont couverts (voir la notice, §24). Les déclarations sociales et fiscales restent établies par le comptable, hors du logiciel.
- **Clôture du mois en cours :** elle couvre jusqu’au jour même ; relancez-la en fin de mois pour facturer les derniers jours (sans risque de double facturation).
- **Caution d’hospitalisation :** elle s’encaisse comme une avance à la caisse, prévenue à chaque admission ; les nuits sont facturées à la sortie, et le quitus garantit le solde avant le départ du patient.
- **Notifications :** le signal sonore ne retentit qu’après un premier clic dans la page (règle des navigateurs). Les alertes du système demandent l’autorisation du navigateur, et l’application Android affiche les notifications dans l’application seulement.
- **Messages WhatsApp et SMS :** le logiciel prépare le message et ouvre l’application ; l’envoi se confirme dans WhatsApp ou dans l’application de SMS. Sur un ordinateur sans WhatsApp Desktop, le lien ouvre WhatsApp Web, et le SMS suppose un téléphone.
Ces limites sont acceptables pour démarrer. Chacune a une solution d’attente :

- **Reprise de l’existant :**
  - les impayés et l’historique des consultations antérieurs ne sont pas importés ;
  - en attendant, ils restent suivis sur l’ancien registre jusqu’à leur solde.
- **Dérogation « assuré sans accord » :** non disponible. En attendant, le passage est facturé comme non assuré, puis l’accord est ajouté dès sa réception.
- **Dates d’effet des tarifs :** un changement de prix s’applique dès l’enregistrement. En attendant, modifiez les tarifs en fin de journée.
- **Inventaire complet :** il se fait par ajustements lot par lot, validés au-delà du seuil de valeur.
- **Bons de commande :** ils restent hors application. La réception de la marchandise, elle, est contrôlée dans l’application.
- **Médicaments sur ordonnance au comptoir :** seuls les psychotropes exigent le prescripteur et le n° d’ordonnance (registre PHA-11). Pour les antibiotiques et les injectables, le pharmacien vérifie l’ordonnance papier en attendant que la direction arrête la liste des produits concernés.
- **Édition autonome (fichier HTML) :** elle garde la base dans le navigateur d’un seul ordinateur. Elle convient à la formation, à la démonstration ou à un démarrage sur un poste. Dès que plusieurs postes doivent partager la base, installez l’édition serveur et restaurez-y la dernière sauvegarde du fichier HTML.
