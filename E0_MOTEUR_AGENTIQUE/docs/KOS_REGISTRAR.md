---
ergo_id: KOS_REGISTRAR
doc_id: DOC_0005
fichier: kos_registrar.py
version: 1.0.0
doc_revision: 2
sha256_source: 17ce95bc
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-23
---

# KOS_REGISTRAR — `kos_registrar.py`

## Rôle

Registre des composants ERGO_ID - scan + generation KOS_ERGO_REGISTRY.json

---

## Description

kos_registrar.py
ERGO KOS_COMPTA — Registre des Composants KOS

Scanne tous les fichiers Python du projet portant un header `# ERGO_ID: XXX`,
extrait les métadonnées de chaque composant depuis leur docstring (section ERGO_REGISTRY),
et génère/met à jour `KOS_ERGO_REGISTRY.json` — le registre central et versionné
de l'infrastructure KOS_COMPTA.

Appelé automatiquement en stage `setup` du pipeline GitLab CI/CD.
Peut aussi être exécuté localement pour inspecter ou documenter le projet.

---

## Entrées / Sorties

**Entrées :**

`tous les fichiers .py avec header # ERGO_ID:`

**Sorties :**

`E0_MOTEUR_AGENTIQUE/registry/KOS_ERGO_REGISTRY.json`

**Dépendances :**

`(stdlib uniquement)`

---

## Fonctions publiques

### `extraire_ergo_id(contenu: str) → str | None`

Extrait le ERGO_ID depuis la première ligne d'un fichier Python.

**Paramètres :**

```
    contenu: Contenu texte complet du fichier.
```

**Retourne :**

Valeur de l'ERGO_ID (str) ou None si absent.

---

### `extraire_registry_section(contenu: str) → dict`

Extrait et parse la section ERGO_REGISTRY: de la docstring d'un fichier.

**Paramètres :**

```
    contenu: Contenu texte complet du fichier.
```

**Retourne :**

Dictionnaire des clés/valeurs extraites de la section ERGO_REGISTRY.

---

### `scanner_composants(racines: list[Path]) → list[dict]`

Scanne les dossiers fournis pour trouver tous les fichiers Python avec ERGO_ID.

**Paramètres :**

```
    racines: Liste de dossiers à scanner récursivement.
```

**Retourne :**

Liste de dictionnaires décrivant chaque composant trouvé.

---

### `lire_registre() → dict`

Charge le registre existant depuis KOS_ERGO_REGISTRY.json.

**Retourne :**

Dictionnaire complet du registre, ou structure vide si absent.

---

### `fusionner_composants(existants: list[dict], nouveaux: list[dict]) → list[dict]`

Fusionne les composants existants avec les nouveaux en préservant l'historique.

**Paramètres :**

```
    existants: Liste des composants déjà dans le registre.
    nouveaux:  Liste produite par scanner_composants().
```

**Retourne :**

Liste fusionnée et dédupliquée par ergo_id.

---

### `ecrire_registre(composants: list[dict]) → None`

Sérialise et écrit le registre complet dans KOS_ERGO_REGISTRY.json.

**Paramètres :**

```
    composants: Liste fusionnée des composants à persister.
```

---

### `afficher_registre(registre: dict, ergo_id: str | None) → None`

Affiche le registre ou un composant spécifique en console.

**Paramètres :**

```
    registre: Dictionnaire complet du registre.
    ergo_id:  Si fourni, affiche uniquement le composant correspondant.
```

---

## Point d'entrée — `main()`

Point d'entrée CLI du registre KOS.

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `KOS_REGISTRAR` |
| DOC_ID | `DOC_0005` |
| Révision doc | `2` |
| SHA-256 source | `17ce95bc` |
| Fichier source | `kos_registrar.py` |
| Généré le | 2026-02-23 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*