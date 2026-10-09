"""Parcours navigateur v1.3 : avances, facture récapitulative, laboratoire, bordereaux assureurs (base de formation).
Usage : python parcours-v13.py comptes.txt"""
import os, re, sys, json, time
from playwright.sync_api import sync_playwright
BASE = os.environ.get('MSI_URL', 'http://localhost:8081')
MDP = {m.group(1): m.group(2) for l in open(sys.argv[1], encoding='utf-8') for m in [re.match(r'\s*(\w+)[\s=]+(\S+)', l)] if m}
CAP = os.environ.get('CAPTURES', '/tmp')
erreurs, etapes = [], []
def ok(m): etapes.append(m); print('OK  ', m, flush=True)
def session(b, login):
    pg = b.new_context(viewport={'width': 1280, 'height': 900}, locale='fr-FR').new_page()
    pg.on('pageerror', lambda e: erreurs.append(f'{login}: {e}'))
    pg.goto(BASE); pg.fill('#cx-login', login); pg.fill('#cx-mdp', MDP[login]); pg.press('#cx-mdp', 'Enter'); pg.wait_for_selector('.topbar')
    return pg
def toast(pg, motif, t=10000):
    pg.wait_for_function('(m) => [...document.querySelectorAll(".toast")].some(x => new RegExp(m).test(x.textContent))', arg=motif, timeout=t)
    return [x.text_content() for x in pg.query_selector_all('.toast')][-1]
def choisir(pg, sel, texte):
    v = pg.eval_on_selector(sel, "(s, t) => { const o = [...s.options].find(x => x.textContent.includes(t)); return o ? o.value : null; }", texte)
    assert v is not None, f'option {texte} absente'; pg.select_option(sel, v)
def fermer(pg):
    pg.wait_for_timeout(500)
    if pg.query_selector('.modal'): pg.click('.modal [data-action="closeModal"] >> nth=0'); pg.wait_for_selector('.modal', state='detached')
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None)
    acc = session(b, 'accueil1')
    acc.fill('#acc-q', 'kouassi'); acc.click('[data-action="accChoisir"]:has-text("KOUASSI")'); acc.wait_for_selector('#acc-detail .pat-name')
    choisir(acc, '#acc-acte', 'Cardiologie'); acc.fill('#acc-accord', 'ASC-2026-0901'); acc.click('[data-action="ouvrirPassage"]'); toast(acc, 'Passage V-')
    acc.fill('#acc-q', 'diabat'); acc.click('[data-action="accChoisir"]:has-text("DIABATÉ")'); acc.wait_for_selector('#acc-detail .pat-name')
    acc.click('[data-action="accType"][data-type="labo"]'); acc.click('[data-action="ouvrirPassage"]'); toast(acc, 'Passage V-')
    cai = session(b, 'caisse1')
    cai.fill('#sess-fonds', '20000'); cai.click('[data-action="ouvrirCaisse"]'); cai.wait_for_selector('.sess-strip')
    cai.click('[data-action="caiChoisir"]:has-text("KOUASSI")'); cai.click('[data-action="payer"]'); cai.click('[data-action="payValider"]'); cai.wait_for_selector('.modal .ticket'); fermer(cai)
    ok('Consultation assurée ASCOMA encaissée (part patient)')
    # Avance : dépôt puis paiement par avance
    cai.click('[data-action="avanceNouvelle"]')
    cai.fill('#av-q', 'konan'); cai.click('[data-action="avanceChercher"]'); cai.click('[data-action="avanceChoisir"] >> nth=0')
    cai.fill('#av-montant', '20000'); choisir(cai, '#av-mode', 'Espèces'); cai.fill('#av-motif', 'Provision pour bilan')
    cai.click('[data-action="avanceEnregistrer"]'); t = toast(cai, 'vance|pôt'); fermer(cai)
    ok('Avance de 20 000 FCFA reçue : ' + t)
    cai.click('[data-action="caiChoisir"]:has-text("KONAN")'); cai.click('[data-action="payer"]')
    choisir(cai, '[data-change="payMode"]', 'Avance')
    cai.click('[data-action="payValider"]'); cai.wait_for_selector('.modal .ticket')
    assert 'Avance' in cai.text_content('.modal .ticket'), 'mode avance absent du reçu'
    fermer(cai); ok('Impayé antérieur de KONAN réglé sur son avance')
    # Facture récapitulative
    cai.click('tr:has-text("KONAN") [data-action="factureNouvelle"]'); cai.wait_for_selector('#fa-passage')
    assert 'REPRISE' in cai.text_content('#fa-passage'), 'passage ancien absent de la facture'
    cai.click('[data-action="factureCreer"]')
    t = toast(cai, 'FAC-|acture'); cai.screenshot(path=os.path.join(CAP, 'v13-facture.png')); fermer(cai)
    ok('Facture récapitulative émise : ' + t)
    # Laboratoire : glycémie payée puis saisie
    cai.click('[data-action="caiChoisir"]:has-text("DIABATÉ")')
    cai.click('[data-action="ajouterActes"]'); cai.click('.modal .acte:has-text("Glycémie") [data-d="1"]'); cai.click('[data-action="ajouterActesValider"]'); toast(cai, 'Bons créés')
    cai.click('[data-action="caiChoisir"]:has-text("DIABATÉ")'); cai.click('[data-action="payer"]'); cai.click('[data-action="payValider"]'); cai.wait_for_selector('.modal .ticket'); fermer(cai)
    lab = session(b, 'labo1')
    assert lab.get_attribute('.tab[aria-current="page"]', 'data-tab') == 'laboratoire'
    lab.click('[data-action="labChoisir"]:has-text("DIABATÉ")'); lab.wait_for_selector('[data-input="labChamp"]')
    lab.fill('[data-input="labChamp"][data-c="valeur"] >> nth=0', '2,35')
    lab.click('[data-action="labEnregistrer"]'); toast(lab, 'hors normes')
    lab.click('[data-action="labValider"]'); toast(lab, 'alid')
    lab.screenshot(path=os.path.join(CAP, 'v13-labo.png'))
    ok('Laboratoire : glycémie à 2,35 g/L signalée anormale, résultat validé et figé')
    # Bordereau ASCOMA puis règlement
    raf = session(b, 'raf1')
    raf.click('[data-action="onglet"][data-tab="tiers"]'); raf.wait_for_selector('[data-action="brdNouveau"]')
    raf.click('[data-action="brdNouveau"] >> nth=0'); raf.click('[data-action="brdCreer"]'); t = toast(raf, 'BOR-|ordereau'); fermer(raf)
    ok('Bordereau ASCOMA émis : ' + t)
    raf.click('[data-action="tpSub"] >> nth=1') if raf.query_selector('[data-action="tpSub"]') else None
    raf.wait_for_selector('[data-action="brdVoir"]'); raf.click('[data-action="brdVoir"] >> nth=0'); raf.wait_for_selector('.modal')
    raf.screenshot(path=os.path.join(CAP, 'v13-bordereau.png'))
    assert 'KOUASSI' in raf.text_content('.modal'), 'ligne du bordereau absente'
    raf.click('.modal [data-action="brdReglement"]'); raf.wait_for_selector('#rg-montant')
    montant = raf.input_value('#rg-montant') or '20000'
    raf.fill('#rg-montant', montant); raf.fill('#rg-ref', 'VIR-ASCOMA-0926')
    raf.click('[data-action="brdReglementOk"]'); t = toast(raf, 'glement'); fermer(raf)
    ok('Règlement ASCOMA enregistré et lettré : ' + t)
    b.close()
print('\n', len(etapes), 'étapes réussies')
print('ERREURS JAVASCRIPT :', json.dumps(erreurs, ensure_ascii=False) if erreurs else 'aucune')
