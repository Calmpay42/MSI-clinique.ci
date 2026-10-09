"""Parcours navigateur : fiches conseils, photo jointe au dossier, reprise d'une sauvegarde OphtaSuite (base de formation).
Usage : python parcours-reprise.py comptes.txt photo.png sauvegarde.json"""
import os, re, sys, json, time
from playwright.sync_api import sync_playwright
BASE = os.environ.get('MSI_URL', 'http://localhost:8081')
MDP = {}
for l in open(sys.argv[1], encoding='utf-8'):
    m = re.match(r'\s*(\w+)[\s=]+(\S+)', l)
    if m: MDP[m.group(1)] = m.group(2)
PHOTO, SAUV = sys.argv[2], sys.argv[3]
# Les rendez-vous du jeu d'essai sont replacés dans le futur à chaque exécution : une date fixe finit par passer,
# et la reprise n'importe à juste titre que les rendez-vous à venir.
import datetime as _dt, json as _json, tempfile as _tf
_d = _json.load(open(SAUV, encoding='utf-8')); _b = _d.get('DB', _d) if isinstance(_d, dict) else _d
for _r in _b.get('rdv', []): _r['date'] = (_dt.date.today() + _dt.timedelta(days=10)).isoformat()
SAUV = _tf.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8').name
_json.dump(_d, open(SAUV, 'w', encoding='utf-8'), ensure_ascii=False)
erreurs, etapes = [], []
def ok(m): etapes.append(m); print('OK  ', m, flush=True)
def session(b, login):
    pg = b.new_context(viewport={'width': 1280, 'height': 900}, locale='fr-FR').new_page()
    pg.on('pageerror', lambda e: erreurs.append(f'{login}: {e}'))
    pg.goto(BASE); pg.fill('#cx-login', login); pg.fill('#cx-mdp', MDP[login]); pg.press('#cx-mdp', 'Enter'); pg.wait_for_selector('.topbar')
    return pg
def toast(pg, motif):
    pg.wait_for_function('(m) => [...document.querySelectorAll(".toast")].some(t => new RegExp(m).test(t.textContent))', arg=motif, timeout=10000)
    return [t.text_content() for t in pg.query_selector_all('.toast')][-1]
def choisir(pg, sel, texte):
    v = pg.eval_on_selector(sel, "(s, t) => { const o = [...s.options].find(x => x.textContent.includes(t)); return o ? o.value : null; }", texte); pg.select_option(sel, v)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM') or None)
    acc = session(b, 'accueil1')
    acc.fill('#acc-q', 'traor'); acc.click('[data-action="accChoisir"]:has-text("TRAORÉ")'); acc.wait_for_selector('#acc-detail .pat-name')
    choisir(acc, '#acc-acte', 'Ophtalmologie'); acc.click('[data-action="ouvrirPassage"]'); toast(acc, 'Passage V-')
    cai = session(b, 'caisse1')
    cai.fill('#sess-fonds', '10000'); cai.click('[data-action="ouvrirCaisse"]'); cai.wait_for_selector('.sess-strip')
    cai.click('[data-action="caiChoisir"]:has-text("TRAORÉ")'); cai.click('[data-action="payer"]'); cai.click('[data-action="payValider"]'); cai.wait_for_selector('.modal .ticket')
    med = session(b, 'medecin1')
    med.click('[data-action="consChoisir"]:has-text("TRAORÉ")'); med.click('[data-action="consCommencer"]'); med.wait_for_selector('textarea[data-k="motif"]')
    ok('Consultation d’ophtalmologie ouverte après paiement')
    med.click('[data-action="consOnglet"][data-o="documents"]')
    med.wait_for_selector('[data-action="docNouveau"][data-type="conseils"]')
    med.click('[data-action="docNouveau"][data-type="conseils"]')
    med.check('.modal input[name="cons-fiche"][value="general"]'); med.check('.modal input[name="cons-fiche"] >> nth=3')
    med.click('.modal [data-action="docEmettre"]'); toast(med, 'émis')
    med.wait_for_selector('.modal .doc .doc-soustitre')
    titres = [t.text_content() for t in med.query_selector_all('.modal .doc .doc-soustitre')]
    assert len(titres) == 2 and 'yeux' in titres[0], titres
    med.screenshot(path=os.path.join(os.environ.get('CAPTURES', '/tmp'), 'r1-fiches-conseils.png'))
    med.click('.modal [data-action="closeModal"] >> nth=0'); med.wait_for_selector('.modal', state='detached')
    ok('Fiches conseils imprimables : ' + ' ; '.join(titres))
    med.click('[data-action="pieceNouvelle"]')
    med.set_input_files('#piece-fichier', PHOTO); med.fill('#piece-legende', 'Rétinophotographie OD')
    med.click('[data-action="pieceEnregistrer"]'); toast(med, 'Pièce jointe')
    med.wait_for_selector('.pieces img[src^="/api/pieces/"]')
    largeur = med.eval_on_selector('.pieces img', 'i => i.complete ? i.naturalWidth : new Promise(r => i.onload = () => r(i.naturalWidth))')
    assert largeur > 0, 'miniature non chargée'
    ok(f'Photo réduite et jointe au dossier, miniature affichée ({largeur} px)')
    med.click('[data-action="repriseOuvrir"]')
    med.set_input_files('#rep-fichier', SAUV); med.click('[data-action="repriseAnalyser"]')
    med.wait_for_selector('[data-action="repriseImporter"]')
    assert 'nouveau(x) dossier' in med.text_content('#rep-res')
    ok('Reprise OphtaSuite : analyse affichée avant import')
    med.click('[data-action="repriseImporter"]'); med.wait_for_selector('#rep-res .notice.ok')
    bilan = med.text_content('#rep-res .notice.ok').replace('\u202f', ' ').replace('\u00a0', ' ')
    assert '1 consultation' in bilan and '1 photo' in bilan and '1 rendez-vous' in bilan, bilan
    med.screenshot(path=os.path.join(os.environ.get('CAPTURES', '/tmp'), 'r2-reprise.png'))
    ok('Reprise OphtaSuite : ' + re.sub(r'\s+', ' ', bilan).strip())
    med.click('.modal [data-action="closeModal"] >> nth=0')
    b.close()
print('\n', len(etapes), 'étapes réussies')
print('ERREURS JAVASCRIPT :', json.dumps(erreurs, ensure_ascii=False) if erreurs else 'aucune')
