---
type: norme_comptable
source: PCG_ANC_2014-03
version: 2025
classe: 5
intitule: Comptes Financiers
tags: [pcg, classe5, financier, banque, caisse, tresorerie, valeurs_mobilieres, bilan, actif_circulant]
applicable_a: [bilan, ecriture_comptable, tresorerie, rapprochement_bancaire]
rag_chunk: PCG_CLASSE_5
---

# PCG — Classe 5 : Comptes Financiers

> Comptes de bilan — Actif circulant. Liquidités et valeurs immédiatement disponibles.

---

## 50 — Valeurs mobilières de placement

| Compte | Libellé | Obligatoire |
|---|---|---|
| 502 | Actions propres | |
| 5021 | Actions destinées à être attribuées aux employés | |
| 5022 | Actions disponibles pour être attribuées aux employés ou pour régularisation des cours de bourse | |
| 503 | Actions | ✅ |
| 5031 | Titres cotés | |
| 5035 | Titres non cotés | |
| 504 | Autres titres conférant un droit de propriété | |
| 505 | Obligations et bons émis par la société et rachetés par elle | |
| 506 | Obligations | ✅ |
| 5061 | Titres cotés | |
| 5065 | Titres non cotés | |
| 507 | Bons du Trésor et bons de caisse à court terme | ✅ |
| 508 | Autres valeurs mobilières de placement et autres créances assimilées | ✅ |
| 5081 | Autres valeurs mobilières | |
| 5082 | Bons de souscription | |
| 5088 | Intérêts courus sur obligations, bons et valeurs assimilées | |
| 509 | Versements restant à effectuer sur valeurs mobilières de placement non libérées | |

---

## 51 — Banques, établissements financiers et assimilés

| Compte | Libellé | Obligatoire |
|---|---|---|
| 511 | Valeurs à l'encaissement | ✅ |
| 5111 | Coupons échus à l'encaissement | |
| 5112 | Chèques à encaisser | |
| 5113 | Effets à l'encaissement | |
| 5114 | Effets à l'escompte | |
| 512 | Banques | ✅ |
| 5121 | Comptes en euros | ✅ |
| 5124 | Comptes en devises | |
| 517 | Autres organismes financiers | |
| 518 | Intérêts courus | |
| 5181 | Intérêts courus à payer | |
| 5188 | Intérêts courus à recevoir | |
| 519 | Concours bancaires courants | ✅ |
| 5191 | Crédit de mobilisation de créances commerciales | |
| 5193 | Mobilisation de créances nées à l'étranger | |
| 5198 | Intérêts courus sur concours bancaires courants | |

---

## 52 — Instruments financiers à terme et jetons détenus

| Compte | Libellé |
|---|---|
| 521 | Instruments financiers à terme |
| 522 | Jetons détenus |
| 523 | Jetons auto-détenus |
| 524 | Jetons empruntés |

---

## 53 — Caisse

| Compte | Libellé | Obligatoire |
|---|---|---|
| 531 | Caisse siège social | ✅ |
| 532 | Caisse succursale / agence | |

---

## 58 — Virements internes

| Compte | Libellé |
|---|---|
| 580 | Virements internes |

> Compte transitoire — utilisé pour enregistrer les virements entre comptes bancaires ou entre banque et caisse. Toujours soldé en fin de période.

---

## 59 — Dépréciations des comptes financiers

| Compte | Libellé |
|---|---|
| 590 | Dépréciations des valeurs mobilières de placement |
| 5903 | Actions |
| 5904 | Autres titres conférant un droit de propriété |
| 5906 | Obligations |
| 5908 | Autres valeurs mobilières de placement et créances assimilées |

---

## Règles d'imputation — Classe 5

| Opération | Débit | Crédit |
|---|---|---|
| Encaissement client (virement) | 512 Banque | 411 Clients |
| Règlement fournisseur (virement) | 401 Fournisseurs | 512 Banque |
| Retrait espèces | 531 Caisse | 512 Banque |
| Virement interne banque → caisse | 580 Virements internes | 512 Banque / puis 531 ← 580 |
| Achat valeurs mobilières | 50xxx VMP | 512 Banque |
| Cession VMP avec plus-value | 512 Banque | 50xxx + 767 Produit cession |
| Agios bancaires | 627 Services bancaires | 512 Banque |

---

## Point vigilance KOS_COMPTA

| Règle | Conséquence si violation |
|---|---|
| Tout paiement > 1 000€ en espèces entre professionnels est interdit | REJET — Art. L112-6 CMF |
| Compte 580 doit être soldé en fin de mois | AVERTISSEMENT si solde persistant |
| Rapprochement bancaire obligatoire | AVERTISSEMENT si 512 ne correspond pas au relevé |

---

## Références légales

- PCG — Règlement ANC 2014-03 modifié
- Code Monétaire et Financier Art. L112-6 — Plafond paiements espèces
- Code de Commerce Art. L123-12 — Enregistrement chronologique
