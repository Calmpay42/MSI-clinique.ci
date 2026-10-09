"""Parcours navigateur du module Consultations (base de formation). Usage : python parcours-consultation.py comptes.txt"""
import os, re, sys, json, time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright

BASE = os.environ.get('MSI_URL', 'http://localhost:8081')
import tempfile
CAPTURES = os.environ.get('CAPTURES', tempfile.gettempdir())
MDP = {}
for l in open(sys.argv[1] if len(sys.argv) > 1 else 'comptes.txt', encoding='utf-8'):
    m = re.match(r'\s*(\w+)[\s=]+(\S+)', l)
    if m: MDP[m.group(1)] = m.group(2)
erreurs, etapes = [], []
def ok(msg): etapes.append(msg); print('OK  ', msg, flush=True)
def session(b, login, w=1280, h=900):
    pg = b.new_context(viewport={'width': w, 'height': h}, locale='fr-FR').new_page()
    pg.on('pageerror', lambda e: erreurs.append(f'{login}: {e}'))
    pg.goto(BASE); pg.fill('#cx-login', login); pg.fill('#cx-mdp', MDP[login]); pg.press('#cx-mdp', 'Enter')
    pg.wait_for_selector('.topbar', timeout=10000)
    return pg
def toast(pg, motif, timeout=9000):
    pg.wait_for_function('(m) => [...document.querySelectorAll(".toast")].some(t => new RegExp(m).test(t.textContent))', arg=motif, timeout=timeout)
    return [t.text_content() for t in pg.query_selector_all('.toast')][-1]
def choisir(pg, sel, texte):
    v = pg.eval_on_selector(sel, "(s, t) => { const o = [...s.options].find(x => x.textContent.includes(t)); return o ? o.value : null; }", texte)
    assert v is not None, f'option {texte} absente de {sel}'
    pg.select_option(sel, v)
def emettre(pg, motif='émis|envoyé|enregistré'):
    pg.click('.modal [data-action="docEmettre"]')
    t = toast(pg, motif)
    pg.wait_for_timeout(800)
    if pg.query_selector('.modal'):
        pg.click('.modal [data-action="closeModal"] >> nth=0')
        pg.wait_for_selector('.modal', state='detached')
    return t

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None)
    acc = session(b, 'accueil1')
    acc.fill('#acc-q', 'kouassi'); acc.click('[data-action="accChoisir"]:has-text("KOUASSI")')
    acc.wait_for_selector('#acc-detail .pat-name')
    choisir(acc, '#acc-acte', 'Ophtalmologie'); acc.fill('#acc-accord', 'ASC-2026-0555'); acc.click('[data-action="ouvrirPassage"]')
    toast(acc, 'Passage V-'); ok('Accueil : consultation d’ophtalmologie ouverte avec accord ASCOMA')

    med = session(b, 'medecin1')
    assert med.get_attribute('.tab[aria-current="page"]', 'data-tab') == 'consultations'
    med.click('[data-action="consChoisir"]:has-text("KOUASSI")')
    med.wait_for_selector('#cons-detail .notice.bad')
    assert not med.query_selector('[data-action="consCommencer"]'), 'bouton de consultation visible avant paiement'
    ok('Médecin : consultation bloquée tant que le bon n’est pas réglé')

    cai = session(b, 'caisse1')
    cai.fill('#sess-fonds', '20000'); cai.click('[data-action="ouvrirCaisse"]'); cai.wait_for_selector('.sess-strip')
    cai.click('[data-action="caiChoisir"]:has-text("KOUASSI")'); cai.click('[data-action="payer"]'); cai.click('[data-action="payValider"]')
    cai.wait_for_selector('.modal .ticket'); cai.click('.modal [data-action="closeModal"]')
    ok('Caisse : part patient encaissée (20 % de la consultation)')

    med.wait_for_selector('[data-action="consChoisir"]:has-text("KOUASSI") .badge:has-text("Prêt")', timeout=12000)
    med.click('[data-action="consChoisir"]:has-text("KOUASSI")')
    med.click('[data-action="consCommencer"]')
    med.wait_for_selector('textarea[data-k="motif"]')
    ok('Médecin : dossier débloqué automatiquement après paiement, consultation commencée')
    med.click('[data-action="consChip"][data-k="motif"] >> nth=0')
    assert med.input_value('textarea[data-k="motif"]').strip(), 'suggestion non insérée'
    med.fill('[data-k="ta"]', '150/95'); med.wait_for_selector('#al-ta:has-text("Tension élevée")')
    med.fill('[data-k="to"][data-cote="OD"]', '26'); med.fill('[data-k="to"][data-cote="OG"]', '17')
    assert 'PIO élevée' in med.text_content('#cons-detail'), 'alerte PIO absente'
    med.select_option('select[data-k="porte_verres"]', 'Oui')
    med.fill('[data-k="av_loin_sc"][data-cote="OD"]', '3/10'); med.fill('[data-k="av_loin_sc"][data-cote="OG"]', '8/10')
    med.click('[data-action="consChip"][data-k="diagnostic"]:has-text("Suspicion de glaucome")')
    med.click('[data-action="consEnregistrer"]'); toast(med, 'nregistr')
    ok('Consultation : suggestions, alertes TA et PIO, AV et tension oculaire par œil, brouillon enregistré')
    med.screenshot(path=os.path.join(CAPTURES, 'c1-consultation.png'), full_page=True)

    med.click('[data-action="consOnglet"][data-o="documents"]') if med.query_selector('[data-action="consOnglet"][data-o="documents"]') else med.click('[data-action="consOnglet"]:has-text("Documents")')
    med.click('[data-action="docNouveau"][data-type="examens"]')
    med.check('.modal input[value="Champ Visuel Automatisé"]'); med.click('.modal details.constats summary'); med.check('.modal input[value="Nfs"]'); med.check('.modal input[value="Angiographie Fluoresceinique"]')
    t = emettre(med, 'caisse|émis'); ok('Demande d’examens : ' + t)
    med.click('[data-action="docNouveau"][data-type="ordonnance"]')
    med.fill('.modal [data-input="ordChamp"][data-c="medicament"] >> nth=0', 'Maxmoist')
    med.fill('.modal [data-input="ordChamp"][data-c="duree"] >> nth=0', '1 mois')
    med.dispatch_event('.modal [data-input="ordChamp"][data-c="medicament"] >> nth=0', 'change')
    time.sleep(0.3)
    poso = med.input_value('.modal [data-input="ordChamp"][data-c="posologie"] >> nth=0')
    assert 'goutte' in poso, 'posologie non proposée : ' + poso
    emettre(med); ok('Ordonnance : posologie proposée depuis le référentiel OphtaSuite (' + poso + ')')
    med.click('[data-action="docNouveau"][data-type="lunettes"]')
    med.fill('[data-lun="od.sphere"]', '-1,25'); med.fill('[data-lun="og.sphere"]', '-1,00'); med.fill('#lun-ecart', '62')
    emettre(med); ok('Ordonnance de lunettes émise')
    med.click('[data-action="docNouveau"][data-type="certificat"]')
    med.click('.modal [data-action="certType"]:not([data-s="medical"])')
    med.fill('#cert-jours', '3')
    emettre(med); ok('Certificat d’arrêt de travail émis')
    med.click('[data-action="docNouveau"][data-type="compte_rendu"]')
    choisir(med, '.modal select[data-change="crType"]', 'Champ visuel')
    med.click('.modal [data-action="crModele"]:has-text("Glaucomateux")')
    emettre(med); ok('Compte rendu de champ visuel émis à partir du modèle « glaucomateux »')
    med.click('[data-action="docNouveau"][data-type="orientation"]')
    choisir(med, '#ori-dest', 'Cardiologie')
    med.click('.modal [data-action="chipCible"] >> nth=0')
    emettre(med); ok('Lettre d’orientation vers la cardiologie émise')
    demain = (date.today() + timedelta(days=1)).isoformat()
    med.click('[data-action="docNouveau"][data-type="rdv"]')
    med.fill('#rdv-date', demain); med.fill('#rdv-heure', '09:30')
    med.click('.modal [data-action="rdvEnregistrer"]'); toast(med, 'endez-vous'); ok('Rendez-vous de contrôle posé pour demain 9 h 30')
    n_docs = len(med.query_selector_all('[data-action="docVoir"]'))
    assert n_docs >= 6, f'{n_docs} documents listés'
    med.click('[data-action="docVoir"] >> nth=0'); med.wait_for_selector('.modal .doc img[src="/img/logo-msi.png"]')
    med.screenshot(path=os.path.join(CAPTURES, 'c2-document.png'))
    med.click('.modal [data-action="closeModal"]')
    ok(f'{n_docs} documents numérotés, aperçu imprimable avec le logo officiel MSI')

    med.click('[data-action="consOnglet"]:has-text("Consultation")')
    med.click('[data-action="consValider"]'); med.click('.modal [data-action="consValiderConfirmer"]')
    toast(med, 'alid'); med.wait_for_selector('[data-action="consChoisir"]:has-text("KOUASSI") .badge:has-text("Terminée")', timeout=12000)
    assert not med.query_selector('textarea[data-k="motif"]'), 'formulaire encore modifiable après validation'
    ok('Consultation validée : figée, lecture seule')

    time.sleep(6)
    cai.wait_for_selector('[data-action="caiChoisir"]:has-text("KOUASSI")', timeout=12000)
    cai.click('[data-action="caiChoisir"]:has-text("KOUASSI")')
    cai.wait_for_selector('#cai-detail .coupon:has-text("Champ Visuel")')
    assert 'NFS' in cai.text_content('#cai-detail') and 'Angiographie' not in cai.text_content('#cai-detail')
    ok('Caisse : champ visuel et NFS à encaisser ; angiographie (hors MSI) non facturée')

    pha = session(b, 'pharma1')
    choisir(pha, '[data-change="phaPassage"]', 'KOUASSI')
    pha.wait_for_selector('[data-action="phaReprendre"]', timeout=8000)
    assert 'Maxmoist' in pha.text_content('#main') and 'glaucome' not in pha.text_content('#main').lower()
    ok('Pharmacie : ordonnance du médecin reçue, sans aucun diagnostic')

    acc.reload(); acc.wait_for_selector('.topbar')
    assert 'KOUASSI' in acc.text_content('#main') and '09:30' in acc.text_content('#main'), 'rendez-vous absent de l’accueil'
    ok('Accueil : rendez-vous de demain visible avec l’heure')

    acc.fill('#acc-q', 'diabat'); acc.click('[data-action="accChoisir"]:has-text("DIABATÉ")'); acc.wait_for_selector('#acc-detail .pat-name')
    choisir(acc, '#acc-acte', 'Cardiologie'); acc.click('[data-action="ouvrirPassage"]'); toast(acc, 'Passage V-')
    time.sleep(1)
    cai.reload(); cai.wait_for_selector('.topbar')
    cai.click('[data-action="caiChoisir"]:has-text("DIABATÉ")'); cai.click('[data-action="payer"]'); cai.click('[data-action="payValider"]'); cai.wait_for_selector('.modal .ticket')
    med2 = session(b, 'medecin2')
    assert 'KOUASSI' not in med2.text_content('.list'), 'patient d’ophtalmologie visible par le généraliste'
    med2.click('[data-action="consChoisir"]:has-text("DIABATÉ")'); med2.click('[data-action="consCommencer"]')
    med2.wait_for_selector('textarea[data-k="auscultation"]')
    txt = med2.text_content('#cons-detail')
    assert 'Acuité' not in txt and 'Tension oculaire' not in txt and 'Auscultation cardiaque' in txt
    med2.fill('[data-k="ta_bras"][data-cote="Bras gauche"]', '185/115'); med2.wait_for_selector('#cons-detail .alerte:has-text("HTA sévère")')
    med2.screenshot(path=os.path.join(CAPTURES, 'c3-cardiologie.png'), full_page=True)
    med2.click('[data-action="consOnglet"]:has-text("Documents")')
    assert not med2.query_selector('[data-action="docNouveau"][data-type="lunettes"]'), 'lunettes proposées en cardiologie'
    ok('Cardiologie : formulaire propre (auscultation, TA aux deux bras, HTA sévère signalée), sans rien d’ophtalmologique')
    b.close()

print('\n', len(etapes), 'étapes réussies')
print('ERREURS JAVASCRIPT :', json.dumps(erreurs, ensure_ascii=False) if erreurs else 'aucune')
