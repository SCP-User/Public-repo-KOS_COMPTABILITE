# CLAUDE.md — KOS_COMPTA Project Memory

> Ce fichier est lu automatiquement par Claude Code à chaque session.
> Il contient tout le contexte nécessaire pour intervenir sur le projet sans briefing supplémentaire.

## PROTOCOLE DE DÉMARRAGE DE SESSION

**À chaque session, Claude Code doit dans cet ordre :**

1. Lire `E0_MOTEUR_AGENTIQUE/KOS_JOURNAL.json` — voir les tâches `TODO` et `IN_PROGRESS`
2. Lire `E0_MOTEUR_AGENTIQUE/SYSTEM_LOG.json` — voir le dernier état de l'infrastructure
3. Lire `E0_MOTEUR_AGENTIQUE/KOS_ERGO_REGISTRY.json` — connaître les composants actifs
4. Informer Adam : "Session démarrée — X tâches en attente : [liste des TODO]"

**Quand Adam dit "okay on met à jour le log" :**

Ajouter une entrée dans `KOS_JOURNAL.json` avec :
- `id` : prochain `J_XXXX` séquentiel
- `timestamp` : horodatage ISO 8601 actuel
- `session` : "Claude Code"
- `type` : DECISION | ACTION | TACHE | CORRECTION | NOTE
- `statut` : TODO | IN_PROGRESS | DONE | CANCELLED
- `sujet` : titre court de ce qui a été fait/décidé
- `detail` : description complète
- `fichiers_impactes` : liste des fichiers créés/modifiés
- `ergo_ids_impactes` : ERGO_IDs concernés

Puis mettre à jour les entrées précédentes dont le statut a changé (ex: TODO → DONE).

---

## IDENTITÉ DU PROJET

**KOS_COMPTA** — Compliance ERP Middleware
**Hackathon GitLab AI 2026** — deadline 25 mars 2026, 14h00 EDT (20h00 heure française)
**Bonus visés** : Anthropic ($10K) + Most Impactful ($5K)

**Principe fondateur :**
> *The KOS is the legislator. The LLM is the executor. The CI/CD is the tribunal.*

**Ce que ça fait :** Agent GitLab CI/CD qui intercepte les documents comptables avant injection ERP,
les audite contre le droit français (Art. L123-14 Code de Commerce), et produit un verdict JSON
structuré : CONFORME → payload ERP / REJET → rapport légal motivé.

---

## RÔLES

| Acteur | Rôle |
|---|---|
| **Claude Code** | Agent Ouvrier — exécute, code, teste, push |
| **Claude.ai** | Architecte — conçoit, documente, structure |
| **Adam** | Chef d'Orchestre — valide et oriente |

---

## ARBORESCENCE

```
Public-repo-KOS_COMPTABILITE/
├── CLAUDE.md                            ← ce fichier (mémoire projet)
├── README.md                            ← documentation publique hackathon
├── .gitlab-ci.yml                       ← pipeline CI/CD 4 stages
├── requirements.txt                     ← dépendances Python
├── .gitignore
│
├── E0_MOTEUR_AGENTIQUE/
│   ├── agent_compliance.py              ← ERGO_ID: COMPLIANCE_AGENT
│   ├── detect_document_type.py          ← ERGO_ID: DETECT_DOCUMENT
│   ├── publish_report.py                ← ERGO_ID: PUBLISH_REPORT
│   ├── shadow_clone.py                  ← ERGO_ID: SHADOW_CLONE
│   ├── ergo_core_system.py              ← ERGO_ID: CORE_BOOTSTRAP
│   ├── system_code_register.py          ← ERGO_ID: CODE_REGISTER
│   ├── kos_registrar.py                 ← ERGO_ID: KOS_REGISTRAR
│   ├── doc_generator.py                 ← ERGO_ID: DOC_GENERATOR
│   ├── docs/                            ← documentation .md auto-générée
│   │   ├── DOC_INDEX.json               ← index versionné (DOC_XXXX, SHA-256, révisions)
│   │   └── <ERGO_ID>.md                 ← un fichier par composant
│   ├── KOS_COMPTA_Taxonomie.json        ← carte constitutionnelle
│   ├── KOS_COMPTA_Agentique.json        ← règles de comportement agent
│   ├── KOS_COMPTA_Client_Log.json       ← journal client
│   ├── KOS_ERGO_REGISTRY.json           ← registre auto-généré par kos_registrar.py
│   ├── ITERATIONS_LOG.json              ← log cumulatif des runs (auto-généré)
│   └── SYSTEM_LOG.json                  ← log infrastructure (auto-généré)
│
├── E1_CORPUS_LEGAL_ETAT/                ← normes légales françaises (READ-ONLY)
│   ├── loi_tva_cadeaux.md               ← CGI Art.236 — seuil 73€ TTC
│   ├── mentions_obligatoires_facture.md ← CGI Art.289
│   ├── tva_regles_generales.md          ← taux 5.5/10/20% + règles déductibilité
│   └── pcg_classes_1_a_4.md             ← Plan Comptable Général classes 1 à 4
│
├── E2_SOP_INTERNE_ET_ERP/               ← procédures internes client (à remplir)
│
├── E3_INTERFACES_ACTEURS/
│   ├── E3.1_Dropzone_Factures/          ← documents à auditer (entrée pipeline)
│   │   ├── facture_A102.md              ← champagne 120€ → REJET attendu
│   │   ├── facture_B001.md              ← fournitures bureau → CONFORME attendu
│   │   ├── facture_C001.md              ← sans n° TVA → REJET attendu
│   │   ├── note_frais_D001.md           ← repas 16€50 → CONFORME attendu
│   │   └── note_frais_E001.md           ← repas 110€ sans justif → AVERTISSEMENT attendu
│   └── E3.2_Requetes_Assistants/        ← requêtes libres (mode copilot — à venir)
│
└── E4_AUDIT_ET_ROUTAGE/
    ├── E4.1_Rapports_Conformite/        ← RAPPORT_*.json générés automatiquement
    └── E4.2_Payloads_ERP/               ← PAYLOAD_*.json générés automatiquement
```

---

## SYSTÈME DE TRAÇABILITÉ — ERGO_ID

### Règle d'annotation

Chaque fichier Python du projet **doit** avoir :
1. Un header `# ERGO_ID: NOM_COMPOSANT` en première ligne
2. Une docstring de module avec une section `ERGO_REGISTRY:` structurée

Format obligatoire :
```python
# ERGO_ID: MON_COMPOSANT
"""
mon_module.py
=============
Description courte.

ERGO_REGISTRY:
    version      : 1.0.0
    auteur       : ERGO Capital / Adam
    dependances  : [autre_module.py, fichier.json]
    entrees      : [chemin/entree/*.ext]
    sorties      : [chemin/sortie/*.json]
    variable_env : [MA_VAR_ENV]
"""
```

### Règles de documentation (NO COMMENTS)

| Autorisé | Interdit |
|---|---|
| Docstrings Google-style sur fonctions/modules | Commentaires inline `# explication logique` |
| Type annotations sur tous les paramètres | Section headers `# ─────────────────────` |
| `ERGO_ID` + `ERGO_REGISTRY` dans docstring | Commentaires d'explication de structure |

### Outils de traçabilité

```bash
# Régénérer toute la documentation Markdown versionnée
python E0_MOTEUR_AGENTIQUE/doc_generator.py

# Régénérer la doc d'un seul composant
python E0_MOTEUR_AGENTIQUE/doc_generator.py --ergo-id COMPLIANCE_AGENT

# Consulter l'index DOC (DOC_XXXX, SHA-256, révisions)
cat E0_MOTEUR_AGENTIQUE/docs/DOC_INDEX.json

# Régénérer le registre des composants
python E0_MOTEUR_AGENTIQUE/kos_registrar.py

# Lister tous les composants enregistrés
python E0_MOTEUR_AGENTIQUE/kos_registrar.py --list

# Détail d'un composant
python E0_MOTEUR_AGENTIQUE/kos_registrar.py --ergo-id COMPLIANCE_AGENT

# Enregistrer une action sur un fichier
python E0_MOTEUR_AGENTIQUE/system_code_register.py --fichier agent.py --action UPDATED --detail "ajout feature X"

# Créer un shadow clone (snapshot du code)
python E0_MOTEUR_AGENTIQUE/shadow_clone.py --action create --label "avant refacto"

# Voir les diffs depuis un clone
python E0_MOTEUR_AGENTIQUE/shadow_clone.py --action diff --clone-id SHADOW_20260323_...
```

---

## SYSTÈME D'ITÉRATION LOG

`ITERATIONS_LOG.json` — log cumulatif de chaque run du pipeline.

**Schema d'une itération :**
```json
{
  "iteration_id":        "ITER_0001",
  "pipeline_id":         "local | <CI_PIPELINE_ID>",
  "timestamp_start":     "ISO 8601",
  "timestamp_end":       "ISO 8601",
  "duration_seconds":    44.67,
  "documents_count":     1,
  "resume":              {"CONFORME": 0, "REJET": 1, "AVERTISSEMENT": 0, "ERREUR": 0},
  "cout_total_eur":      0.00045,
  "tokens_total_input":  800,
  "tokens_total_output": 250,
  "documents": [
    {
      "fichier":            "facture_A102.md",
      "type":               "facture_fournisseur",
      "verdict":            "REJET",
      "motif":              "TVA non déductible — valeur unitaire > 73€ TTC",
      "articles_appliques": ["CGI Art.236"],
      "niveau_risque":      "ELEVE",
      "action_erp":         "BLOQUER",
      "llm":                "claude-sonnet-4-6",
      "tokens_input":       800,
      "tokens_output":      250,
      "cout_eur":           0.00045,
      "fichier_sorti":      "RAPPORT_facture_A102_20260323_142501.json"
    }
  ]
}
```

---

## SYSTÈME DOC_INDEX — Versioning de la documentation

`E0_MOTEUR_AGENTIQUE/docs/DOC_INDEX.json` — registre versionné de chaque doc générée.

**Schema d'une entrée DOC :**
```json
{
  "doc_id":               "DOC_0001",
  "ergo_id":              "COMPLIANCE_AGENT",
  "fichier_source":       "agent_compliance.py",
  "fichier_doc":          "E0_MOTEUR_AGENTIQUE/docs/COMPLIANCE_AGENT.md",
  "sha256_source":        "a1b2c3d4",
  "source_version":       "1.0.0",
  "doc_revision":         1,
  "premiere_generation":  "2026-02-23T14:36:22",
  "derniere_mise_a_jour": "2026-02-23T14:36:22"
}
```

**Règle de révision :** `doc_revision` s'incrémente uniquement si le SHA-256 du `.py` source a changé depuis la dernière génération. Permet de détecter les dérives entre code et documentation.

---

## PIPELINE CI/CD — 4 STAGES

```yaml
setup:   bootstrap → shadow_clone → kos_registrar → system_code_register
detect:  detect_document_type → dotenv (DOCUMENT_TYPE, DOCUMENT_FILE, ...)
audit:   agent_compliance → E4.1 (rejets) ou E4.2 (conformes)
report:  publish_report → commentaire MR GitLab
```

**Variables GitLab CI/CD à configurer (Settings → CI/CD → Variables) :**
- `ANTHROPIC_API_KEY` : clé API Anthropic (masked, protected)
- `GITLAB_TOKEN` : Personal Access Token avec scope `api` (masked)

---

## FORMAT VERDICT JSON

```json
{
  "verdict": "CONFORME | REJET | AVERTISSEMENT",
  "motif": "explication courte",
  "articles_appliques": ["CGI Art.236"],
  "corrections_requises": ["correction si applicable"],
  "imputation_recommandee": {
    "compte_debit": "XXXXX",
    "compte_credit": "XXXXX",
    "montant_ht": 0.00,
    "tva_deductible": 0.00,
    "tva_non_deductible": 0.00,
    "montant_ttc": 0.00
  },
  "niveau_risque": "FAIBLE | MOYEN | ELEVE",
  "action_erp": "INJECTER | BLOQUER | REVUE_HUMAINE",
  "_meta": {
    "llm": "claude-sonnet-4-6",
    "input_tokens": 0,
    "output_tokens": 0,
    "cout_estime_eur": 0.00
  }
}
```

---

## FORMAT NORME E1

Chaque fichier `.md` dans `E1_CORPUS_LEGAL_ETAT/` doit avoir ce frontmatter :
```yaml
---
type: norme_fiscale | norme_comptable | procedure
source: CGI_Art_XXX | PCG_classe_X | ANC_2014-03
version: 2026
tags: [tag1, tag2, tag3]
applicable_a: [cycle_achat, cycle_vente, ...]
---
```

---

## FORMAT DOCUMENT E3.1

Chaque facture/note de frais dans `E3.1_Dropzone_Factures/` :
```yaml
---
type: facture_fournisseur | note_de_frais | ecriture | bilan
id: XXXX
statut: en_attente_audit
date_soumission: YYYY-MM-DD
soumis_par: identite
tags: [tag1, tag2, ...]
montant_ht: 0.00
montant_tva: 0.00
montant_ttc: 0.00
---
```

---

## STACK TECHNIQUE

| Composant | Tech |
|---|---|
| LLM principal | claude-sonnet-4-6 (Anthropic API) |
| CI/CD | GitLab CI/CD |
| Vector DB | ChromaDB (local, post-hackathon) |
| Backend | FastAPI (post-hackathon) |
| ERP output | JSON / CSV (Sage, EBP, Cegid, Pennylane) |

**Dépendances :**
```
anthropic>=0.40.0
chromadb>=0.5.0
python-frontmatter>=1.1.0
pyyaml>=6.0.0
requests
rich>=13.0.0
fastapi>=0.115.0
```

---

## RÈGLES AGENTIQUES

1. Lire `KOS_COMPTA_Taxonomie.json` en premier
2. `E1` prime **toujours** sur `E2` en cas de conflit
3. Tout verdict doit citer au moins un article légal
4. Jamais d'injection ERP sans verdict `CONFORME` explicite
5. Logger chaque analyse dans `ITERATIONS_LOG.json`
6. En cas de doute → `AVERTISSEMENT` + `REVUE_HUMAINE`
7. Chaque nouveau fichier Python → header `# ERGO_ID:` obligatoire
8. Après modification d'un fichier → `system_code_register.py --action UPDATED`
9. Après modification d'un fichier Python → régénérer sa doc : `python E0_MOTEUR_AGENTIQUE/doc_generator.py --ergo-id NOM_COMPOSANT`
10. La doc_revision dans DOC_INDEX.json s'incrémente automatiquement si le SHA-256 de la source a changé

---

## DEADLINES ET LIVRABLES

| Date | Livrable |
|---|---|
| **25 mars 2026, 14h00 EDT** | Soumission Devpost + repo GitLab public fonctionnel |
| — | Pipeline CI/CD tournant sur au moins 1 cas de test |
| — | Vidéo démo 2 minutes |
| — | Description Devpost complète |

---

## AUTEUR

**Adam** — ERGO Capital
BTS Comptabilité et Gestion · Alternance Toulouse
Bachelor Data & IA (en cours)
Autodidacte MLOps · KOS builder depuis GPT-3

---

*CLAUDE.md généré le 23 février 2026 — ERGO Capital / Adam*
*Maintenu automatiquement par Claude Code entre les sessions*
