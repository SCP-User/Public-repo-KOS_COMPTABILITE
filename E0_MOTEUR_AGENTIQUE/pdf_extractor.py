# ERGO_ID: PDF_EXTRACTOR
"""
pdf_extractor.py
================
ERGO KOS_COMPTA — ETL Layer — Zéro dépendance API
Extract / Load / Transform

Format de sortie hybride optimal LLM :
  - En-tête / pied  → texte structuré plat  (tokens minimum)
  - Lignes facture  → tableau Markdown       (clarté colonnes)

Inputs supportés :
  - PDF natif       → pdfplumber
  - PDF scanné      → pytesseract (lang=fra)
  - XML Factur-X    → lxml

Usage :
  python pdf_extractor.py --input facture.pdf
  python pdf_extractor.py --input facture.xml
  python pdf_extractor.py --batch --dir ./pdfs_entrants/
  python pdf_extractor.py --input scan.pdf --force-ocr

ERGO_REGISTRY:
    role         : ETL sas entrée — PDF/XML → Markdown structuré pour Dropzone
    version      : 1.0.0
    auteur       : ERGO Capital / Adam
    dependances  : pdfplumber, pytesseract, pdf2image, Pillow, lxml
    entrees      : E3.1_Dropzone_Factures/input/*.pdf, *.xml, *.ubl
    sorties      : E3.1_Dropzone_Factures/{stem}_{timestamp}.md
"""

import sys
import os
import re
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

BASE_DIR   = Path(__file__).parent.parent
INPUT_DIR  = BASE_DIR / "E3_INTERFACES_ACTEURS" / "E3.1_Dropzone_Factures" / "input"
DROPZONE   = BASE_DIR / "E3_INTERFACES_ACTEURS" / "E3.1_Dropzone_Factures"
SYSTEM_LOG = Path(__file__).parent / "logs" / "SYSTEM_LOG.json"

CHAMPS_ENTETE = [
    "fournisseur","supplier","vendeur","siret","siren",
    "tva","tva_fr","numéro tva","n° tva",
    "acheteur","buyer","client",
    "numéro","numero","facture n°","invoice",
    "date","date facture","date émission","issuedate",
    "échéance","echeance","duedate",
    "total ht","total ttc","total tva",
    "mode paiement","iban","bic",
]

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("pdf_extractor")


# ── DÉTECTION ───────────────────────────────

def est_xml(path: Path) -> bool:
    return path.suffix.lower() in [".xml", ".ubl", ".facturx"]

def est_pdf_natif(pdf_path: Path, seuil: int = 50) -> bool:
    try:
        import pdfplumber
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t and len(t.strip()) >= seuil:
                    return True
        return False
    except Exception as e:
        log.warning(f"Détection PDF natif : {e}")
        return False


# ── EXTRACT ─────────────────────────────────

def extraire_pdf_natif(pdf_path: Path) -> dict:
    import pdfplumber
    log.info(f"pdfplumber → {pdf_path.name}")
    pages, tables = [], []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages.append(t.strip())
            for tbl in page.extract_tables():
                if tbl:
                    tables.append(tbl)
    return {"methode": "pdfplumber", "pages_texte": pages, "tables_brutes": tables}

def extraire_pdf_scanne(pdf_path: Path) -> dict:
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError(
            "pip install pytesseract pdf2image pillow\n"
            "apt-get install tesseract-ocr tesseract-ocr-fra poppler-utils"
        )
    log.info(f"pytesseract → {pdf_path.name}")
    images = convert_from_path(str(pdf_path), dpi=200)
    pages = []
    for i, img in enumerate(images):
        txt = pytesseract.image_to_string(img, lang="fra")
        pages.append(txt.strip())
        log.info(f"Page {i+1}/{len(images)} OCR OK")
    return {"methode": "pytesseract", "pages_texte": pages, "tables_brutes": []}

def extraire_xml_facturx(xml_path: Path) -> dict:
    try:
        from lxml import etree
    except ImportError:
        raise ImportError("pip install lxml")
    log.info(f"lxml Factur-X → {xml_path.name}")
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()
    def strip_ns(tag):
        return re.sub(r'\{.*?\}', '', tag)
    def to_dict(el):
        r = {}
        for child in el:
            k = strip_ns(child.tag)
            r[k] = to_dict(child) if len(child) else child.text
        return r
    return {
        "methode": "lxml_facturx",
        "pages_texte": [],
        "tables_brutes": [],
        "xml_data": to_dict(root)
    }


# ── TRANSFORM ───────────────────────────────

def extraire_champs_entete(texte: str) -> dict:
    champs = {}
    for ligne in texte.split("\n"):
        for champ in CHAMPS_ENTETE:
            m = re.search(rf"(?i){re.escape(champ)}\s*[:\-]\s*(.+)", ligne)
            if m:
                cle = champ.upper().replace(" ", "_").replace("°", "")
                if cle not in champs:
                    champs[cle] = m.group(1).strip()
    return champs

def tables_vers_markdown(tables: list) -> str:
    md = ""
    for table in tables:
        if not table or not table[0]:
            continue
        def clean(c):
            return str(c).replace("\n", " ").strip() if c else ""
        headers = [clean(c) for c in table[0]]
        if not any(headers):
            continue
        md += f"| {' | '.join(headers)} |\n"
        md += f"| {' | '.join(['---'] * len(headers))} |\n"
        for row in table[1:]:
            cells = [clean(c) for c in row]
            if any(cells):
                md += f"| {' | '.join(cells)} |\n"
        md += "\n"
    return md

def xml_vers_plat(data: dict, prefix: str = "") -> str:
    lignes = []
    for k, v in data.items():
        cle = f"{prefix}.{k}".upper().lstrip(".") if prefix else k.upper()
        if isinstance(v, dict):
            lignes.append(xml_vers_plat(v, prefix=cle))
        else:
            lignes.append(f"{cle}: {v}")
    return "\n".join(lignes)

def transformer_en_markdown(data: dict, source: Path) -> str:
    ts = datetime.now().isoformat()
    methode = data["methode"]

    frontmatter = f"""---
type: facture_fournisseur
format: extrait_{methode}
statut: a_traiter
id: {source.stem.upper()}
source_fichier: {source.name}
extraction_date: {ts}
methode_extraction: {methode}
tags: [facture, extrait_automatique, {methode}]
---"""

    corps = f"\n# Document extrait — {source.name}\n"
    corps += f"> `{methode}` — {ts[:19]}\n"

    if methode == "lxml_facturx" and data.get("xml_data"):
        corps += "\n## Données Factur-X\n\n"
        corps += xml_vers_plat(data["xml_data"])
        corps += "\n"
        return frontmatter + corps

    texte_complet = "\n".join(data["pages_texte"])

    champs = extraire_champs_entete(texte_complet)
    if champs:
        corps += "\n## En-tête\n\n"
        for cle, val in champs.items():
            corps += f"{cle}: {val}\n"

    if data["tables_brutes"]:
        corps += "\n## Lignes facture\n\n"
        corps += tables_vers_markdown(data["tables_brutes"])
    else:
        corps += "\n## Contenu brut\n\n"
        corps += texte_complet + "\n"

    return frontmatter + corps


# ── LOAD ────────────────────────────────────

def charger_en_dropzone(contenu: str, source: Path) -> Path:
    DROPZONE.mkdir(parents=True, exist_ok=True)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = DROPZONE / f"{source.stem}_{ts}.md"
    out.write_text(contenu, encoding="utf-8")
    log.info(f"Dropzone → {out.name}")
    return out


# ── LOG SYSTEM ──────────────────────────────

def log_system(fichier: str, action: str, detail: str):
    entrees = []
    if SYSTEM_LOG.exists():
        try:
            entrees = json.loads(SYSTEM_LOG.read_text(encoding="utf-8"))
        except Exception:
            pass
    n = len(entrees) + 1
    entrees.append({
        "iteration": n,
        "timestamp": datetime.now().isoformat(),
        "fichier": fichier,
        "action": action,
        "detail": detail,
        "auteur": "pdf_extractor",
        "ergo_id": f"ERGO_{n:04d}"
    })
    SYSTEM_LOG.write_text(json.dumps(entrees, ensure_ascii=False, indent=2), encoding="utf-8")


# ── PIPELINE ────────────────────────────────

def _valider_chemin(chemin: Path) -> Path:
    resolu = chemin.resolve()
    if not str(resolu).startswith(str(BASE_DIR.resolve())):
        raise ValueError(f"Chemin hors zone autorisée : {resolu}")
    return resolu


def traiter_fichier(source: Path, force_ocr: bool = False) -> Path:
    source = _valider_chemin(source)
    if not source.exists():
        raise FileNotFoundError(f"Introuvable : {source}")
    log.info(f"═══ ETL START → {source.name} ═══")

    if est_xml(source):
        data = extraire_xml_facturx(source)
    elif force_ocr:
        data = extraire_pdf_scanne(source)
    elif est_pdf_natif(source):
        data = extraire_pdf_natif(source)
    else:
        log.info("Scanné détecté → pytesseract")
        data = extraire_pdf_scanne(source)

    contenu = transformer_en_markdown(data, source)
    out = charger_en_dropzone(contenu, source)
    log_system(source.name, "EXTRACTED", f"methode={data['methode']} | output={out.name}")
    log.info(f"═══ ETL OK → {out.name} ═══")
    return out

def traiter_batch(dossier: Path = None, force_ocr: bool = False):
    dossier = _valider_chemin(dossier or INPUT_DIR)
    fichiers = []
    for ext in ["*.pdf", "*.xml", "*.ubl"]:
        fichiers.extend(dossier.glob(ext))
    if not fichiers:
        log.warning(f"Aucun fichier dans {dossier}")
        return
    log.info(f"{len(fichiers)} fichier(s) à traiter")
    for f in fichiers:
        try:
            traiter_fichier(f, force_ocr)
        except Exception as e:
            log.error(f"Échec {f.name} : {e}")
            log_system(f.name, "FAILED", str(e))


# ── CLI ─────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ERGO PDF Extractor v1 — ETL zéro API → Dropzone KOS_COMPTA"
    )
    parser.add_argument("--input",     type=str)
    parser.add_argument("--batch",     action="store_true")
    parser.add_argument("--dir", type=str, default=str(INPUT_DIR))
    parser.add_argument("--force-ocr", action="store_true")
    args = parser.parse_args()

    if args.batch:
        traiter_batch(Path(args.dir), args.force_ocr)
    elif args.input:
        out = traiter_fichier(Path(args.input), args.force_ocr)
        print(f"[OK] → {out}", flush=True)
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
