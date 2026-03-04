# KOS_COMPTA — Compliance Audit Middleware for Accounting Documents

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Claude API](https://img.shields.io/badge/Claude%20API-Sonnet%204.6-orange)
![GitLab CI](https://img.shields.io/badge/GitLab%20CI-4%20stages-FC6D26)
![Hackathon](https://img.shields.io/badge/GitLab%20AI%20Hackathon-2026-purple)

> _The KOS is the legislator. The LLM is the executor. The CI/CD is the tribunal._

---

## The Problem

French accounting law (Art. L123-14, Code de Commerce) requires every document entering the books to satisfy three principles: **régularité** (compliance), **sincérité** (good faith), **image fidèle** (true and fair view).

Today this audit is manual — slow, inconsistent, and exposed to human error. A single non-compliant invoice slips through and the company faces a tax audit.

---

## The Solution

KOS_COMPTA is a **GitLab CI/CD agent** that intercepts accounting documents before ERP injection, audits them against French law using Claude API + a vectorized legal corpus (RAG), and produces a structured verdict.

**No non-compliant document enters the books.**

---

## Architecture

```
[E3.1 Dropzone]      Drop invoice .md or PDF here

    [DETECT]         detect_document_type.py
                     Identifies: facture_fournisseur / note_de_frais / ecriture

    [LOAD KOS]       ingest_kos.py → ChromaDB
                     RAG: loads matching E1 laws + E2 internal SOP

    [AUDIT]          agent_compliance.py → Claude Sonnet 4.6
                     Checks: régularité · sincérité · image fidèle

    [ROUTE]
       ├── CONFORME      → PAYLOAD_*.json   → ready for ERP injection
       ├── AVERTISSEMENT → RAPPORT_*.json   → human review queue
       └── REJET         → RAPPORT_*.json   → legal article cited + corrections

    [REPORT]         publish_report.py
                     Auto-posts verdict as comment on GitLab MR
```

**GitLab CI/CD pipeline — 4 stages:** `setup` → `detect` → `audit` → `report`

---

## What Works Right Now

Tested on **11 real accounting documents** across 2 pipeline runs:

| Metric | Value |
|--------|-------|
| Documents audited | 11 |
| CONFORME | 2 |
| REJET | 5 |
| AVERTISSEMENT | 4 |
| ERREUR | 0 |
| Total LLM cost | €0.21 |
| Avg time per run | ~96 sec |
| Model | claude-sonnet-4-6 |

**Test cases included in E3.1:**

| Document | Type | Expected verdict |
|----------|------|-----------------|
| `facture_A102.md` | Champagne coffrets 120€/unit | REJET (CGI Art.236) |
| `facture_B001.md` | Fournitures bureau | CONFORME |
| `facture_C001.md` | Facture sans n° TVA ni SIRET | REJET (CGI Art.289) |
| `note_frais_D001.md` | Repas 16,50€ ticket de caisse | AVERTISSEMENT |
| `note_frais_E001.md` | Repas 110€ sans justificatif | AVERTISSEMENT → REJET |

---

## Quick Start

```bash
# 1. Clone
git clone https://gitlab.com/[USERNAME]/kos-compta.git
cd kos-compta

# 2. Install
pip install anthropic chromadb sentence-transformers python-frontmatter pyyaml rich

# 3. API key
export ANTHROPIC_API_KEY=sk-ant-...

# 4. Load the legal corpus into ChromaDB (one-time)
python E0_MOTEUR_AGENTIQUE/ingest_kos.py

# 5. Run the compliance audit
python E0_MOTEUR_AGENTIQUE/agent_compliance.py
```

Results appear in:
- `E4_AUDIT_ET_ROUTAGE/E4.1_Rapports_Conformite/` — REJET + AVERTISSEMENT reports
- `E4_AUDIT_ET_ROUTAGE/E4.2_Payloads_ERP/` — CONFORME payloads ready for ERP

---

## Verdict JSON — Real Output (facture_A102.md)

5 bottles of champagne at 120€ TTC each — company gifts for clients.

```json
{
  "verdict": "REJET",
  "motif": "Cadeaux d'entreprise — valeur unitaire TTC 120,00 € > seuil légal 73,00 € TTC (CGI Art. 236). TVA 100,00 € non déductible. Imputer 600,00 € TTC en compte 6230 sans séparation HT/TVA.",
  "articles_appliques": [
    "CGI Art. 236 — Exclusion du droit à déduction sur cadeaux ≥ 73 € TTC",
    "CGI Art. 271 — Conditions générales de déductibilité de la TVA",
    "BOFiP TVA-DED-30-30-20 — TVA sur cadeaux d'entreprise",
    "PCG ANC 2014-03 — Règles d'imputation compte 6230"
  ],
  "corrections_requises": [
    "Imputer 600,00 € TTC en compte 6230 (charges non déductibles)",
    "TVA 100,00 € non déductible — ne pas comptabiliser en 44566"
  ],
  "imputation_recommandee": {
    "compte_debit": "6230",
    "compte_credit": "401",
    "montant_ht": 500.00,
    "tva_deductible": 0.00,
    "tva_non_deductible": 100.00,
    "montant_ttc": 600.00
  },
  "niveau_risque": "ELEVE",
  "action_erp": "BLOQUER",
  "_meta": {
    "llm": "claude-sonnet-4-6",
    "input_tokens": 4353,
    "output_tokens": 589,
    "cout_estime_eur": 0.02189
  }
}
```

---

## Legal Corpus (E1 — Read-Only)

4 norms currently vectorized in ChromaDB:

| File | Norm | Coverage |
|------|------|----------|
| `loi_tva_cadeaux.md` | CGI Art.236 | Company gifts — 73€ TTC deduction threshold |
| `mentions_obligatoires_facture.md` | CGI Art.289 | Mandatory invoice fields |
| `tva_regles_generales.md` | CGI Art.271 | TVA deductibility rules (5.5% / 10% / 20%) |
| `pcg_classes_1_a_4.md` | PCG ANC 2014-03 | French chart of accounts — classes 1 to 4 |

---

## Traceability

| System | File | Role |
|--------|------|------|
| **KOS Journal** | `KOS_JOURNAL.json` | Timestamped log of every decision (J_0001 → J_0032) |
| **Iteration Log** | `ITERATIONS_LOG.json` | Token cost + duration per run |
| **Shadow Clone** | `shadow_clone.py` | Immutable code snapshots at each deploy |
| **ERGO Registry** | `KOS_ERGO_REGISTRY.json` | Auto-scanned registry of active components |

---

## Roadmap

> The items below are **not yet implemented** — they represent the post-hackathon roadmap.

**V2 — Self-Healing Legal Corpus**
Connect to PISTE (Légifrance API). When a CGI article changes, CI/CD auto-updates ChromaDB. The agent stays legally current without manual intervention.

**V3 — Native Factur-X (XML)**
September 2026: structured e-invoicing becomes mandatory in France. `pdf_extractor.py` will ingest the embedded XML stream directly — no OCR uncertainty, 100% reliable input for the audit LLM.

**V4 — REST API + Multi-Client**
FastAPI layer exposing the compliance engine as a service. Any ERP or SaaS can call it before committing a document.

---

## Project Structure

```
E0_MOTEUR_AGENTIQUE/    Brain — agent scripts + constitutional JSON files
E1_CORPUS_LEGAL_ETAT/   French law — PCG, TVA, CGI, ANC norms (read-only)
E2_SOP_INTERNE_ET_ERP/  Internal company rules + ERP config
E3_INTERFACES_ACTEURS/
  E3.1_Dropzone_Factures/   Incoming documents (drop here)
E4_AUDIT_ET_ROUTAGE/
  E4.1_Rapports_Conformite/ REJET + AVERTISSEMENT reports
  E4.2_Payloads_ERP/        CONFORME payloads → ERP
  E4.3_Imports_ERP/         CSV exports (CEGID format)
```

---

## Mode Opératoire de Travail (MOT)

> How an accounting team uses this pipeline daily.

```
RÉCEPTION D'UN DOCUMENT COMPTABLE
────────────────────────────────────────────────────────────────────────
Facture PDF / XML / note de frais reçue par email ou scan
                          │
                          ▼
        ┌─────────────────────────────┐
        │  ÉTAPE 1 — DÉPÔT           │
        │  Copier le PDF dans        │
        │  E3.1_Dropzone/input/      │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │  ÉTAPE 2 — CONVERSION ETL  │
        │  python pdf_extractor.py   │
        │  --batch                   │
        │                            │
        │  Output : facture_XXX.md   │
        │  (frontmatter + tableau)   │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │  ÉTAPE 3 — AUDIT IA        │
        │  python agent_compliance.py│
        │                            │
        │  Claude lit le document,   │
        │  interroge le RAG (E1+E2), │
        │  produit un verdict JSON   │
        └──────────────┬──────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
   ┌────────────────┐   ┌────────────────────┐
   │  CONFORME      │   │  REJET /           │
   │  ──────────    │   │  AVERTISSEMENT     │
   │  E4.2 Payload  │   │  ──────────────    │
   │  JSON → ERP    │   │  E4.1 Rapport      │
   └───────┬────────┘   │  → Comptable       │
           │            │    pour review     │
           ▼            └────────────────────┘
   ┌────────────────┐
   │  ÉTAPE 4 — ERP │
   │  python        │
   │  export_erp.py │
   │                │
   │  Output :      │
   │  IMPORT_CEGID  │
   │  _YYYYMMDD.csv │
   └───────┬────────┘
           │
           ▼
   ┌────────────────────────────────┐
   │  IMPORT DANS L'ERP            │
   │  (CEGID / Sage / Pennylane)   │
   │                               │
   │  Écritures comptables prêtes  │
   │  en partie double :           │
   │  Débit charge + TVA / Crédit  │
   │  fournisseur                  │
   └────────────────────────────────┘
```

### Typical Verdicts by Document Type

| Document | Expected Verdict | Reason |
|----------|-----------------|--------|
| Facture fournisseur conforme (SIRET, TVA, montants) | ✅ CONFORME | All mandatory fields present — CGI Art.289 |
| Cadeau client > 73€ TTC | 🚫 REJET | Above deduction ceiling — CGI Art.236 |
| Note de frais sans justificatif | ⚠️ AVERTISSEMENT | Missing proof — REVUE_HUMAINE required |
| Document non comptable (attestation…) | 🚫 REJET | Not an invoice — CGI Art.289, L123-22 |
| Dépense personnelle (animal, loisir…) | 🚫 REJET | No professional link — CGI Art.39-1 |
| Facture énergie usage mixte (télétravail TNS) | ⚠️ AVERTISSEMENT | Pro/perso ratio required — CGI Art.39 |

### Economics (per 1,000 documents/month)

| Solution | Monthly Cost |
|---------|-------------|
| Human accounting assistant | €2,000 – €3,500 |
| **KOS_COMPTA (Claude API)** | **~€20** |
| Savings | **~€3,000 / month** |

> Cost estimate: ~11 documents = €0.21 → ~€19/1,000 docs. First-pass triage only — human accountant reviews flagged documents.

---

## Author

**ERGO Capital — Adam**
BTS Comptabilité et Gestion · Alternance Toulouse
Bachelor Data & IA (en cours)

Built for the **GitLab AI Hackathon 2026** — deadline 25 mars 2026.

---

_KOS_COMPTA : L'automatisation par la preuve._
