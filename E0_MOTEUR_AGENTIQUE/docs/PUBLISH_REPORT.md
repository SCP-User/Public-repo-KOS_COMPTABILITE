---
ergo_id: PUBLISH_REPORT
doc_id: DOC_0006
fichier: publish_report.py
version: 1.0.0
doc_revision: 1
sha256_source: dfaee3ca
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-23
---

# PUBLISH_REPORT — `publish_report.py`

## Rôle

Stage REPORT - publie le verdict de conformite sur GitLab MR

---

## Description

publish_report.py
ERGO KOS_COMPTA — Stage REPORT

Lit les résultats d'audit produits dans E4 et publie un commentaire Markdown
structuré sur la Merge Request GitLab via l'API REST v4.
Fonctionne aussi en mode local (affichage console) si aucun contexte MR n'est détecté.

---

## Entrées / Sorties

**Entrées :**

`E4_AUDIT_ET_ROUTAGE/E4.1_Rapports_Conformite/RAPPORT_*.json`

**Sorties :**

`Commentaire GitLab MR (API REST)`

**Variables d'environnement requises :**

- `GITLAB_TOKEN`
- `CI_MERGE_REQUEST_IID`
- `CI_PROJECT_ID`

**Dépendances :**

`requests`

---

## Fonctions publiques

### `lire_rapports(report_dir: Path) → list[dict]`

Charge tous les rapports JSON depuis E4.1_Rapports_Conformite.

**Paramètres :**

```
    report_dir: Chemin vers le dossier E4.1.
```

**Retourne :**

Liste de dictionnaires {'fichier': str, 'data': dict} par rapport trouvé.

---

### `lire_payloads(payload_dir: Path) → list[dict]`

Charge tous les payloads ERP JSON depuis E4.2_Payloads_ERP.

**Paramètres :**

```
    payload_dir: Chemin vers le dossier E4.2.
```

**Retourne :**

Liste de dictionnaires {'fichier': str, 'data': dict} par payload trouvé.

---

### `formater_rapport(rapport: dict) → str`

Formate un rapport de rejet ou avertissement en Markdown GitLab.

**Paramètres :**

```
    rapport: Dictionnaire {'fichier': str, 'data': dict} produit par lire_rapports().
```

**Retourne :**

Bloc Markdown formaté pour la Merge Request.

---

### `formater_payload(payload: dict) → str`

Formate un payload ERP CONFORME en Markdown GitLab.

**Paramètres :**

```
    payload: Dictionnaire {'fichier': str, 'data': dict} produit par lire_payloads().
```

**Retourne :**

Bloc Markdown formaté pour la Merge Request.

---

### `construire_commentaire(rapports: list[dict], payloads: list[dict]) → str`

Assemble le commentaire Markdown global pour la Merge Request.

**Paramètres :**

```
    rapports: Liste produite par lire_rapports().
    payloads: Liste produite par lire_payloads().
```

**Retourne :**

Commentaire Markdown complet prêt à poster sur GitLab.

---

### `poster_commentaire_mr(project_id: str, mr_iid: str, token: str, body: str) → bool`

Poste un commentaire sur une Merge Request via l'API REST GitLab v4.

**Paramètres :**

```
    project_id: ID numérique du projet GitLab.
    mr_iid:     IID de la Merge Request (numéro interne au projet).
    token:      Personal Access Token GitLab (PRIVATE-TOKEN).
    body:       Corps Markdown du commentaire.
```

**Retourne :**

True si le commentaire a été publié avec succès, False sinon.

---

### `afficher_commentaire_local(body: str) → None`

Affiche le commentaire en mode local (aucun contexte MR détecté).

**Paramètres :**

```
    body: Corps Markdown du commentaire.
```

---

## Point d'entrée — `main()`

Point d'entrée CLI du stage REPORT.

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `PUBLISH_REPORT` |
| DOC_ID | `DOC_0006` |
| Révision doc | `1` |
| SHA-256 source | `dfaee3ca` |
| Fichier source | `publish_report.py` |
| Généré le | 2026-02-23 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*