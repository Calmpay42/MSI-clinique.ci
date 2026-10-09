"""Parcours de bout en bout dans un navigateur, sur la BASE DE FORMATION (facultatif, pour le technicien).
Prérequis : Python 3, « pip install playwright », « playwright install chromium ».
Usage : npm run formation  >  comptes.txt   (puis garder les lignes « identifiant mot-de-passe »)
        npm start -- --formation
        python tests/navigateur/parcours.py comptes.txt
Variables facultatives : MSI_URL (défaut http://localhost:8081), CHROMIUM (chemin d'un Chromium). """
import os, re, sys, json, time
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get('MSI_URL', 'http://localhost:8081')
import tempfile
CAPTURES = os.environ.get('CAPTURES', tempfile.gettempdir())
MDP = {}
for l in open(sys.argv[1] if len(sys.argv) > 1 else 'comptes.txt', encoding='utf-8'):
    m = re.match(r'\s*(accueil1|caisse1|pharma1|raf1|direction1|admin)[\s=]+(\S+)', l)
    if m: MDP[m.group(1)] = m.group(2)
erreurs = []
refus = []
etapes = []

def ok(msg):
    etapes.append(msg); print('OK  ', msg, flush=True)

def session(browser, login, largeur=1280, hauteur=860):
    ctx = browser.new_context(viewport={'width': largeur, 'height': hauteur}, locale='fr-FR', timezone_id='Africa/Abidjan')
    page = ctx.new_page()
    page.on('pageerror', lambda e: erreurs.append(f'{login} pageerror: {e}'))
    # Les refus du serveur (401 avant connexion, 409/400 des règles testées) sont attendus : comptés à part, pas comme des erreurs.
    page.on('console', lambda m: (refus.append(m.text) if 'responded with a status of 4' in m.text else erreurs.append(f'{login} console.{m.type}: {m.text}')) if m.type == 'error' else None)
    page.goto(BASE)
    page.fill('#cx-login', login)
    page.fill('#cx-mdp', MDP[login])
    page.press('#cx-mdp', 'Enter')
    page.wait_for_selector('.topbar', timeout=10000)
    return page

def toast(page, motif, timeout=8000):
    page.wait_for_function('(m) => [...document.querySelectorAll(".toast")].some(t => new RegExp(m).test(t.textContent))', arg=motif, timeout=timeout)
    return [t.text_content() for t in page.query_selector_all('.toast')]

def choisir(page, selecteur, texte):
    valeur = page.eval_on_selector(selecteur, "(s, t) => { const o = [...s.options].find(x => x.textContent.includes(t)); return o ? o.value : null; }", texte)
    assert valeur is not None, f'option « {texte} » absente de {selecteur}'
    page.select_option(selecteur, valeur)

def onglets(page):
    return [t.text_content().strip() for t in page.query_selector_all('.tabs .tab span:not(.sr)')]

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None)

    # 1. Mauvais mot de passe
    ctx = browser.new_context(); pg = ctx.new_page(); pg.goto(BASE)
    pg.fill('#cx-login', 'accueil1'); pg.fill('#cx-mdp', 'faux'); pg.click('[data-action="connexion"]')
    toast(pg, 'incorrect'); ok('Connexion refusée avec un mauvais mot de passe'); ctx.close()

    # 2. Accueil
    acc = session(browser, 'accueil1')
    assert onglets(acc) == ['Accueil', 'Hospitalisation'], onglets(acc)
    ok(f'Accueil : onglets visibles {onglets(acc)}')
    acc.fill('#acc-q', 'kouassi')
    acc.wait_for_selector('[data-action="accChoisir"]:has-text("KOUASSI")')
    acc.click('[data-action="accChoisir"]:has-text("KOUASSI")')
    acc.wait_for_selector('#acc-detail .pat-name:has-text("KOUASSI")')
    choisir(acc, '#acc-acte', 'Cardiologie')
    acc.fill('#acc-accord', 'ASC-2026-0412')
    acc.click('[data-action="ouvrirPassage"]')
    t = toast(acc, 'Passage V-'); ok('Passage consultation cardiologie ouvert avec accord : ' + t[-1])
    acc.wait_for_selector('.plist li:has-text("accord ASC-2026-0412")')
    # Contrôle gratuit (DIABATÉ, MG payée il y a 6 jours)
    acc.fill('#acc-q', 'diabat')
    acc.wait_for_selector('[data-action="accChoisir"]:has-text("DIABATÉ")')
    acc.click('[data-action="accChoisir"]:has-text("DIABATÉ")')
    acc.wait_for_selector('#acc-detail .pat-name:has-text("DIABATÉ")')
    acc.click('[data-action="accType"][data-type="controle"]')
    choisir(acc, '#acc-acte', 'Médecine générale')
    assert 'contrôle gratuit' in acc.text_content('#acc-detail'), 'indication contrôle gratuit absente'
    acc.click('[data-action="ouvrirPassage"]')
    toast(acc, 'contrôle gratuit'); ok('Contrôle gratuit détecté et appliqué (DIABATÉ)')
    # Nouveau patient puis doublon
    acc.click('[data-action="nouveauPatient"]')
    acc.fill('#np-nom', 'Bamba'); acc.fill('#np-prenoms', 'Issouf'); acc.select_option('#np-sexe', 'M')
    acc.fill('#np-naissance', '1990-05-17'); acc.fill('#np-tel', '07 01 02 03 04'); acc.fill('#np-commune', 'Bingerville')
    choisir(acc, '#np-ass', 'MCI'); acc.fill('#np-num', 'MCI-5555'); acc.fill('#np-taux', '80'); acc.fill('#np-val', '2027-12-31')
    acc.click('[data-action="enregistrerPatient"]')
    t = toast(acc, 'Dossier créé'); ok('Nouveau patient créé : ' + t[-1])
    acc.click('[data-action="nouveauPatient"]')
    acc.fill('#np-nom', 'BAMBA'); acc.fill('#np-prenoms', 'Issouf'); acc.select_option('#np-sexe', 'M')
    acc.fill('#np-naissance', '1990-05-17'); acc.fill('#np-tel', '0701020304')
    acc.click('[data-action="enregistrerPatient"]')
    acc.wait_for_selector('.modal h2:has-text("Doublon probable")')
    ok('Doublon probable détecté à la création')
    acc.click('[data-action="ouvrirDoublon"]')
    acc.wait_for_selector('#acc-detail .pat-name:has-text("BAMBA")')
    acc.screenshot(path=os.path.join(CAPTURES, '1-accueil.png'), full_page=True)

    # 3. Pharmacie : ordonnance, délivrance bloquée avant paiement
    pha = session(browser, 'pharma1')
    assert onglets(pha) == ['Pharmacie'], onglets(pha)
    choisir(pha, '[data-change="phaPassage"]', 'KOUASSI')
    pha.fill('[data-input="phaRecherche"]', 'amox')
    pha.click('[data-action="phaAjouter"]:has-text("Amoxicilline")')
    pha.click('[data-action="phaPas"][data-d="1"]'); pha.click('[data-action="phaPas"][data-d="1"]')
    lignes = pha.text_content('#pha-lignes').replace('\u202f', ' ').replace('\u00a0', ' ')
    assert '3 500 FCFA l’unité' in lignes and '10 500 FCFA' in lignes, 'prix assurances majeures (ASCOMA) attendu : ' + lignes
    pha.click('[data-action="phaEnvoyer"]')
    t = toast(pha, 'Ordonnance ORD-'); ok('Ordonnance envoyée à la caisse : ' + t[-1])
    pha.click('[data-action="delivrer"]')
    t = toast(pha, 'Délivrance bloquée'); ok('Règle d’or : délivrance bloquée avant paiement')

    # 4. Caisse
    cai = session(browser, 'caisse1')
    assert onglets(cai) == ['Hospitalisation', 'Caisse'], onglets(cai)
    assert cai.get_attribute('.tab[aria-current="page"]', 'data-tab') == 'caisse', 'le caissier arrive sur sa caisse'
    cai.fill('#sess-fonds', '50000'); cai.click('[data-action="ouvrirCaisse"]')
    cai.wait_for_selector('.sess-strip'); ok('Caisse ouverte avec 50 000 FCFA de fonds')
    cai.click('[data-action="caiChoisir"]:has-text("KOUASSI")')
    cai.wait_for_selector('#cai-detail .pat-name:has-text("KOUASSI")')
    net = cai.text_content('#cai-sum-lignes .total strong')
    ok('Coupons KOUASSI : net à payer ' + net.replace('\u202f', ' ').replace('\u00a0', ' '))
    cai.click('[data-action="payer"]')
    cai.wait_for_selector('.modal .pay-line')
    cai.click('[data-action="payAjouter"]')
    montants = cai.query_selector_all('[data-input="payMontant"]')
    total = int(montants[0].input_value())
    montants[0].fill('5000'); montants[1].fill(str(total - 5000))
    cai.fill('[data-input="payRemis"]', '10000')
    cai.fill('[data-input="payRef"]', 'OM-MP2609.1432')
    assert 'Complète' in cai.text_content('#pay-total')
    cai.click('[data-action="payValider"]')
    cai.wait_for_selector('.modal .ticket')
    tk = cai.text_content('.modal .ticket')
    assert re.search(r'R-\d{4}-000001', tk), tk
    assert cai.query_selector('.modal .t-qr svg'), 'QR absent'
    assert 'Code de contrôle' in tk and 'ASCOMA 80' in tk
    ok('Paiement mixte (espèces + Orange Money) : reçu R-…-000001 avec QR et code de contrôle')
    cai.screenshot(path=os.path.join(CAPTURES, '2-recu.png'))
    cai.click('.modal [data-action="closeModal"]')
    # Référence réutilisée refusée (KONAN, impayé antérieur)
    cai.click('[data-action="caiChoisir"]:has-text("KONAN")')
    cai.wait_for_selector('#cai-detail .coupon:has-text("Solde impayé")')
    cai.click('[data-action="payer"]')
    cai.select_option('[data-change="payMode"]', 'Orange Money')
    cai.fill('[data-input="payRef"]', 'OM-MP2609.1432')
    cai.click('[data-action="payValider"]')
    toast(cai, 'déjà utilisée'); ok('Référence Orange Money réutilisée : refusée')
    cai.click('.modal [data-action="closeModal"]')
    # Remise au-delà du plafond
    cai.fill('#cai-remise', '30')
    cai.wait_for_selector('[data-action="demanderRemise"]')
    cai.fill('#cai-motif', 'Patient en difficulté, avis social')
    cai.click('[data-action="demanderRemise"]')
    toast(cai, 'Demande envoyée'); ok('Remise de 30 % transmise à la direction')

    # 5. Délivrance après paiement (synchronisation entre postes)
    time.sleep(6)
    pha.wait_for_selector('.ord .badge:has-text("Payée")', timeout=12000)
    ok('Pharmacie : l’ordonnance passe « Payée » automatiquement (synchronisation entre postes)')
    pha.click('[data-action="delivrer"]')
    t = toast(pha, 'Délivré'); ok('Délivrance FEFO : ' + t[-1])
    assert 'AMX-2602' in t[-1] and 'AMX-2501' not in t[-1], 'le lot périmé ne doit jamais sortir'
    pha.click('[data-action="phaSub"][data-sub="stock"]')
    pha.click('[data-action="phaFiltre"][data-f="alertes"]')
    pha.wait_for_selector('td:has-text("Amoxicilline")')
    pha.click('tr:has(td:has-text("Amoxicilline")) [data-action="phaLots"]'); pha.wait_for_selector('.lot.is-exp:has-text("AMX-2501")')
    pha.screenshot(path=os.path.join(CAPTURES, '3-stock.png'), full_page=True)
    ok('Stock : alertes et lots affichés')

    # 6. Direction
    dirp = session(browser, 'direction1')
    assert onglets(dirp) == ['Tableau de bord', 'Accueil', 'Hospitalisation', 'Pharmacie', 'Direction', 'Tiers payant', 'Comptabilité', 'Ressources humaines', 'Paramétrage'], onglets(dirp)
    assert dirp.get_attribute('.tab[aria-current="page"]', 'data-tab') == 'pilotage', 'écran d’arrivée de la direction : le tableau de bord'
    dirp.click('[data-action="onglet"][data-tab="direction"]')
    dirp.wait_for_selector('.dem:has-text("Remise")')
    dirp.click('.dem:has-text("Remise") [data-action="decider"][data-ok="1"]')
    toast(dirp, 'validée'); ok('Direction : remise validée')
    kp = dirp.text_content('.kpis')
    assert 'Encaissé' in kp
    dirp.fill('#vr-num', re.search(r'R-\d{4}-000001', tk).group(0))
    dirp.click('[data-action="verifierRecu"]')
    dirp.wait_for_selector('#vr-res .notice.ok')
    ok('Vérification du reçu : authentique')
    with dirp.expect_download() as dl:
        dirp.click('a[href^="/api/exports/journal-caisse"]')
    contenu = open(dl.value.path(), encoding='utf-8-sig').read()
    assert 'R-' in contenu and 'Net encaissé' in contenu
    ok('Export Excel du journal de caisse téléchargé (' + str(len(contenu.splitlines())) + ' lignes)')
    dirp.screenshot(path=os.path.join(CAPTURES, '4-direction.png'), full_page=True)

    # 7. Caisse : encaissement avec remise validée, puis clôture avec écart
    time.sleep(6)
    cai.click('[data-action="caiChoisir"]:has-text("KONAN")')
    cai.wait_for_selector('#cai-detail .coupon:has-text("remise 30")')
    cai.click('[data-action="payer"]')
    cai.click('[data-action="payValider"]')
    cai.wait_for_selector('.modal .ticket')
    ok('Remise validée appliquée : ' + cai.text_content('.modal .t-total').replace('\u202f', ' ').replace('\u00a0', ' ').strip())
    cai.click('.modal [data-action="closeModal"]')
    cai.click('[data-action="cloture"]')
    cai.fill('[data-k="b10000"]', '5')
    cai.fill('[data-k="b5000"]', '1')
    cai.click('[data-action="clotureValider"]')
    toast(cai, 'justifiez'); ok('Clôture refusée sans justification de l’écart')
    cai.fill('#clo-justif', 'Erreur de rendu de monnaie')
    cai.click('[data-action="clotureValider"]')
    toast(cai, 'Caisse clôturée'); ok('Clôture avec écart justifié, transmis à la direction')
    cai.screenshot(path=os.path.join(CAPTURES, '5-caisse.png'), full_page=True)

    # 8. Paramétrage : administrateur et RAF
    adm = session(browser, 'admin')
    assert onglets(adm) == ['Paramétrage', 'Suppressions'], onglets(adm)
    adm.click('[data-action="admSub"][data-sub="comptes"]')
    adm.wait_for_selector('td:has-text("accueil1")')
    adm.click('[data-action="compteNouveau"]')
    adm.fill('#cp-login', 'awa.kone'); adm.fill('#cp-nom', 'Awa KONÉ')
    adm.check('input[name="cp-role"][value="accueil"]')
    adm.click('[data-action="compteCreer"]')
    adm.wait_for_selector('.modal .mdp')
    mdp_awa = adm.text_content('.modal .mdp').strip()
    ok('Compte créé avec mot de passe provisoire affiché une seule fois')
    adm.click('.modal [data-action="closeModal"]')
    adm.click('[data-action="admSub"][data-sub="sauvegardes"]')
    adm.click('[data-action="sauvegarder"]')
    toast(adm, 'Sauvegarde effectuée'); ok('Sauvegarde manuelle chiffrée effectuée')
    adm.click('[data-action="admSub"][data-sub="journal"]')
    adm.click('[data-action="verifierJournal"]')
    adm.wait_for_selector('.notice.ok:has-text("Journal intègre")')
    ok('Intégrité du journal : ' + adm.text_content('.notice.ok').replace('\u202f', ' ').strip())
    raf = session(browser, 'raf1')
    assert onglets(raf) == ['Tableau de bord', 'Direction', 'Tiers payant', 'Comptabilité', 'Ressources humaines', 'Paramétrage'], onglets(raf)
    raf.click('[data-action="onglet"][data-tab="parametrage"]')
    raf.wait_for_selector('td:has-text("CS-CAR")')
    raf.click('tr:has-text("CS-CAR") [data-action="refModifier"]')
    raf.fill('#fm-prix_non', '27000')
    raf.click('[data-action="refEnregistrer"]')
    toast(raf, 'Enregistré'); ok('RAF : tarif modifié et journalisé')
    raf.screenshot(path=os.path.join(CAPTURES, '6-parametrage.png'), full_page=True)

    # 9. Premier accès avec mot de passe provisoire (mobile)
    ctx = browser.new_context(viewport={'width': 390, 'height': 844}, locale='fr-FR', is_mobile=True, has_touch=True)
    mob = ctx.new_page()
    mob.on('pageerror', lambda e: erreurs.append(f'mobile pageerror: {e}'))
    mob.goto(BASE)
    mob.fill('#cx-login', 'awa.kone'); mob.fill('#cx-mdp', mdp_awa); mob.click('[data-action="connexion"]')
    mob.wait_for_selector('#mdp-nouveau')
    mob.fill('#mdp-ancien', mdp_awa); mob.fill('#mdp-nouveau', 'AccueilMSI2026'); mob.fill('#mdp-confirm', 'AccueilMSI2026')
    mob.click('[data-action="changerMdp"]')
    mob.wait_for_selector('.topbar')
    ok('Premier accès : changement de mot de passe imposé, puis ouverture de l’accueil')
    mob.fill('#acc-q', '0708')
    mob.wait_for_selector('[data-action="accChoisir"]:has-text("KOUASSI")')
    mob.screenshot(path=os.path.join(CAPTURES, '7-mobile.png'), full_page=True)
    largeur = mob.evaluate('document.documentElement.scrollWidth')
    assert largeur <= 390, f'défilement horizontal sur mobile : {largeur}px'
    ok('Affichage mobile sans débordement horizontal')

    browser.close()

print('\n', len(etapes), 'étapes réussies')
print('Refus serveur attendus (401 avant connexion, règles métier testées) :', len(refus))
print('ERREURS NAVIGATEUR :', json.dumps(erreurs, ensure_ascii=False, indent=1) if erreurs else 'aucune')
