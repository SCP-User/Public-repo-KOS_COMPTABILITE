---
ergo_id: PDF_EXTRACTOR
doc_id: DOC_0010
fichier: pdf_extractor.py
version: 1.0.0
doc_revision: 1
sha256_source: 18b26536
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-25
---

# PDF_EXTRACTOR — `pdf_extractor.py`

## Rôle

ETL sas entrée — PDF/XML → Markdown structuré pour Dropzone

---

## Description

pdf_extractor.py
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

---

## Entrées / Sorties

**Entrées :**

- `E3.1_Dropzone_Factures/input/*.pdf`
- `*.xml`
- `*.ubl`

**Sorties :**

`E3.1_Dropzone_Factures/{stem}_{timestamp}.md`

**Dépendances :**

- `pdfplumber`
- `pytesseract`
- `pdf2image`
- `Pillow`
- `lxml`

---

## Fonctions publiques

### `est_xml(path: Path) → bool`

—

---

### `est_pdf_natif(pdf_path: Path, seuil: int) → bool`

—

---

### `extraire_pdf_natif(pdf_path: Path) → dict`

—

---

### `extraire_pdf_scanne(pdf_path: Path) → dict`

—

---

### `extraire_xml_facturx(xml_path: Path) → dict`

—

---

### `extraire_champs_entete(texte: str) → dict`

—

---

### `tables_vers_markdown(tables: list) → str`

—

---

### `xml_vers_plat(data: dict, prefix: str) → str`

—

---

### `transformer_en_markdown(data: dict, source: Path) → str`

—

---

### `charger_en_dropzone(contenu: str, source: Path) → Path`

—

---

### `log_system(fichier: str, action: str, detail: str)`

—

---

### `traiter_fichier(source: Path, force_ocr: bool) → Path`

—

---

### `traiter_batch(dossier: Path, force_ocr: bool)`

—

---

### `strip_ns(tag)`

—

---

### `to_dict(el)`

—

---

### `clean(c)`

—

---

## Point d'entrée — `main()`

—

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `PDF_EXTRACTOR` |
| DOC_ID | `DOC_0010` |
| Révision doc | `1` |
| SHA-256 source | `18b26536` |
| Fichier source | `pdf_extractor.py` |
| Généré le | 2026-02-25 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*