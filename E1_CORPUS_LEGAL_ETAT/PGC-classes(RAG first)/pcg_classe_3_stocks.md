---
type: norme_comptable
source: PCG_ANC_2014-03
version: 2025
classe: 3
intitule: Comptes de Stocks et d'En-Cours
tags: [pcg, classe3, stocks, matieres_premieres, marchandises, en_cours, depreciations, bilan, actif_circulant]
applicable_a: [bilan, ecriture_comptable, cycle_achat, cycle_production, inventaire]
rag_chunk: PCG_CLASSE_3
---

# PCG — Classe 3 : Comptes de Stocks et d'En-Cours

> Comptes de bilan — Actif circulant. Biens détenus pour être vendus ou consommés dans le cycle d'exploitation.

---

## 31 — Matières premières (et fournitures)

| Compte | Libellé | Obligatoire |
|---|---|---|
| 311 | Matières premières | ✅ |
| 312 | Fournitures | ✅ |

---

## 32 — Autres approvisionnements

| Compte | Libellé | Obligatoire |
|---|---|---|
| 321 | Matières consommables | ✅ |
| 322 | Fournitures consommables | ✅ |
| 3221 | Combustibles | |
| 3222 | Produits d'entretien | |
| 3223 | Fournitures d'atelier et d'usine | |
| 3224 | Fournitures de magasin | |
| 3225 | Fournitures de bureau | |
| 326 | Emballages | ✅ |
| 3261 | Emballages perdus | |
| 3265 | Emballages récupérables non identifiables | |
| 3267 | Emballages à usage mixte | |

---

## 33 — En-cours de production de biens

| Compte | Libellé | Obligatoire |
|---|---|---|
| 331 | Produits en cours | ✅ |
| 335 | Travaux en cours | ✅ |

---

## 34 — En-cours de production de services

| Compte | Libellé | Obligatoire |
|---|---|---|
| 341 | Études en cours | ✅ |
| 345 | Prestations de services en cours | ✅ |

---

## 35 — Stocks de produits

| Compte | Libellé | Obligatoire |
|---|---|---|
| 351 | Produits intermédiaires | ✅ |
| 355 | Produits finis | ✅ |
| 358 | Produits résiduels (ou matières de récupération) | ✅ |
| 3581 | Déchets | |
| 3585 | Rebuts | |
| 3586 | Matières de récupération | |

---

## 36 — (Compte à ouvrir, le cas échéant, sous l'intitulé « Stocks provenant d'immobilisations »)

> Usage exceptionnel — cession d'immobilisation transférée en stock.

---

## 37 — Stocks de marchandises

| Compte | Libellé | Obligatoire |
|---|---|---|
| 371 | Stocks de marchandises | ✅ |
| 372 | Emballages commerciaux | ✅ |

---

## 38 — Stocks en voie d'acheminement, mis en dépôt ou donnés en consignation

> Compte utilisé pour stocks en transit ou consignés.

---

## 39 — Dépréciations des stocks et en-cours

| Compte | Libellé |
|---|---|
| 391 | Dépréciations des matières premières et fournitures |
| 392 | Dépréciations des autres approvisionnements |
| 393 | Dépréciations des en-cours de production de biens |
| 394 | Dépréciations des en-cours de production de services |
| 395 | Dépréciations des stocks de produits |
| 397 | Dépréciations des stocks de marchandises |

---

## Règles d'imputation — Classe 3

| Opération | Débit | Crédit |
|---|---|---|
| Entrée stock (inventaire permanent) | 31xxx / 37xxx Stock | 603x Variation de stock |
| Sortie stock | 603x Variation de stock | 31xxx / 37xxx Stock |
| Dépréciation stock (inventaire) | 6817 Dépréciation actifs circulants | 39xxx Dépréciation |
| Reprise dépréciation | 39xxx Dépréciation | 7817 Reprise |

> **Note :** En inventaire intermittent (PME), les comptes 31 et 37 sont soldés en fin d'exercice via le compte 603x.

---

## Références légales

- PCG — Règlement ANC 2014-03 modifié
- Code de Commerce Art. L123-16 — Évaluation des stocks au coût d'entrée
- PCG Art. 321-3 — Méthodes d'évaluation (FIFO, CMP)
