---
ergo_id: COMPLIANCE_AGENT
doc_id: DOC_0001
fichier: agent_compliance.py
version: 1.1.0
doc_revision: 4
sha256_source: ac36e08c
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-25
---

# COMPLIANCE_AGENT — `agent_compliance.py`

## Rôle

Pipeline principal d'audit de conformite comptable (5 etapes)

---

## Description

agent_compliance.py
ERGO KOS_COMPTA — Compliance ERP Middleware
Hackathon GitLab AI 2026

Pipeline d'audit de conformité comptable en 5 étapes :
1. lire_facture         : lecture et extraction frontmatter YAML depuis E3.1
2. charger_normes       : RAG vectoriel ChromaDB (multilingual-e5-base) sur E1 + E2
3. analyser_avec_claude : audit LLM via Anthropic API (claude-sonnet-4-6)
4. router_verdict       : routage vers E4.1 (rejet/avert.) ou E4.2 (conforme)
5. log_iteration        : journal structuré dans ITERATIONS_LOG.json

---

## Entrées / Sorties

**Entrées :**

`E3_INTERFACES_ACTEURS/E3.1_Dropzone_Factures/*.md`

**Sorties :**

`E4_AUDIT_ET_ROUTAGE/E4.1_Rapports_Conformite/RAPPORT_*.json`

**Variables d'environnement requises :**

`ANTHROPIC_API_KEY (obligatoire)`

**Dépendances :**

- `KOS_COMPTA_Taxonomie.json`
- `KOS_COMPTA_Agentique.json`
- `E1_CORPUS_LEGAL_ETAT`

---

## Fonctions publiques

### `lire_facture(chemin: Path) → dict`

Lit un document Markdown et extrait le frontmatter YAML et le corps.

**Paramètres :**

```
    chemin: Chemin absolu vers le fichier .md à lire.
```

**Retourne :**

Dictionnaire contenant :
        - fichier (str)      : nom du fichier
        - frontmatter (dict) : paires clé/valeur extraites du bloc YAML
        - corps (str)        : contenu Markdown hors frontmatter
        - tags (str)         : valeur brute du champ 'tags' du frontmatter

---

### `charger_normes(tags_facture: str) → str`

Recherche les normes légales et SOP pertinentes via ChromaDB (RAG vectoriel).

**Paramètres :**

```
    tags_facture: Chaîne brute du champ 'tags' du frontmatter (ex: "[tva, cadeau, achat]").
```

**Retourne :**

Contexte structuré des normes les plus similaires (RAG) ou résultat du fallback substring.

---

### `analyser_avec_claude(facture: dict, normes: str) → dict`

Soumet le document et les normes KOS à Claude pour un audit de conformité.

**Paramètres :**

```
    facture: Dictionnaire produit par lire_facture().
    normes:  Contexte textuel des normes applicables produit par charger_normes().
```

**Retourne :**

Dictionnaire JSON du verdict contenant :
        - verdict (str)                : CONFORME | REJET | AVERTISSEMENT
        - motif (str)                  : explication du verdict
        - articles_appliques (list)    : références légales citées
        - corrections_requises (list)  : actions correctives si applicable
        - imputation_recommandee (dict): écriture comptable suggérée
        - niveau_risque (str)          : FAIBLE | MOYEN | ELEVE
        - action_erp (str)             : INJECTER | BLOQUER | REVUE_HUMAINE
        - _meta (dict)                 : llm, tokens, coût estimé

**Lève :**

KeyError: Si la variable d'environnement ANTHROPIC_API_KEY est absente.

---

### `router_verdict(facture: dict, verdict: dict) → Optional[str]`

Route le document vers E4.1 (rejet/avertissement) ou E4.2 (conforme).

**Paramètres :**

```
    facture: Dictionnaire produit par lire_facture().
    verdict: Dictionnaire produit par analyser_avec_claude().
```

**Retourne :**

Nom du fichier généré dans E4 (str), ou None si aucun fichier produit.

---

### `log_iteration(pipeline_id: str, timestamp_start: str, documents_resultats: list[dict]) → None`

Enregistre une itération complète du pipeline dans ITERATIONS_LOG.json.

**Paramètres :**

```
    pipeline_id:          Identifiant du pipeline CI/CD ou "local".
    timestamp_start:      Horodatage ISO 8601 du début du run.
    documents_resultats:  Liste des résultats par document, chacun contenant
                          les clés 'facture', 'verdict', 'fichier_sorti'.
```

---

## Point d'entrée — `main()`

Point d'entrée du pipeline de conformité.

---

## Fonctions internes

| Fonction | Rôle |
|---|---|
| `_lire_iterations()` | Charge le contenu existant de ITERATIONS_LOG.json. |
| `_prochain_iteration_id()` | Génère l'identifiant séquentiel de la prochaine itération. |

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `COMPLIANCE_AGENT` |
| DOC_ID | `DOC_0001` |
| Révision doc | `4` |
| SHA-256 source | `ac36e08c` |
| Fichier source | `agent_compliance.py` |
| Généré le | 2026-02-25 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*