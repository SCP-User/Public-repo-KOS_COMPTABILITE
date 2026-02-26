---
type: norme_comptable
source: PCG_ANC_2014-03
version: 2025
classe: 1
intitule: Comptes de Capitaux
tags: [pcg, classe1, capitaux, capital, reserves, emprunts, provisions, bilan, passif]
applicable_a: [bilan, ecriture_comptable, cycle_financement]
rag_chunk: PCG_CLASSE_1
---

# PCG — Classe 1 : Comptes de Capitaux

> Comptes de bilan — Passif. Ressources durables de l'entreprise.

---

## 10 — Capital et réserves

| Compte | Libellé | Obligatoire |
|---|---|---|
| 101 | Capital | ✅ |
| 1011 | Capital souscrit — non appelé | |
| 1012 | Capital souscrit — appelé, non versé | |
| 1013 | Capital souscrit — appelé, versé | ✅ |
| 10131 | Capital non amorti | |
| 10132 | Capital amorti | |
| 1018 | Capital souscrit soumis à des réglementations particulières | |
| 102 | Fonds fiduciaires | |
| 104 | Primes liées au capital | |
| 1041 | Primes d'émission | |
| 1042 | Primes de fusion | |
| 1043 | Primes d'apport | |
| 1044 | Primes de conversion d'obligations en actions | |
| 1045 | Bons de souscription d'actions | |
| 105 | Écarts de réévaluation | |
| 106 | Réserves | ✅ |
| 1061 | Réserve légale | ✅ |
| 1062 | Réserves indisponibles | |
| 1063 | Réserves statutaires ou contractuelles | |
| 1064 | Réserves réglementées | |
| 1068 | Autres réserves | |
| 107 | Écart d'équivalence | |
| 108 | Compte de l'exploitant | |
| 109 | Actionnaires : capital souscrit — non appelé | |

---

## 11 — Report à nouveau

| Compte | Libellé | Obligatoire |
|---|---|---|
| 110 | Report à nouveau — solde créditeur | ✅ |
| 119 | Report à nouveau — solde débiteur | ✅ |

---

## 12 — Résultat de l'exercice

| Compte | Libellé | Obligatoire |
|---|---|---|
| 120 | Résultat de l'exercice — bénéfice | ✅ |
| 1209 | Acomptes sur dividendes | |
| 129 | Résultat de l'exercice — perte | ✅ |

---

## 13 — Subventions d'investissement

| Compte | Libellé | Obligatoire |
|---|---|---|
| 131 | Subventions d'investissement octroyées | ✅ |
| 139 | Subventions d'investissement inscrites au compte de résultat | ✅ |

---

## 14 — Provisions réglementées

| Compte | Libellé |
|---|---|
| 143 | Provisions réglementées pour hausse des prix |
| 145 | Amortissements dérogatoires |
| 148 | Autres provisions réglementées |

---

## 15 — Provisions

| Compte | Libellé |
|---|---|
| 151 | Provisions pour risques |
| 1511 | Provisions pour litiges |
| 1512 | Provisions pour garanties données aux clients |
| 1514 | Provisions pour amendes et pénalités |
| 1515 | Provisions pour pertes de change |
| 1516 | Provisions pour pertes sur contrats |
| 1518 | Autres provisions pour risques |
| 152 | Provisions pour charges |
| 1521 | Provisions pour pensions et obligations similaires |
| 1522 | Provisions pour restructurations |
| 1523 | Provisions pour impôts |
| 1524 | Provisions pour renouvellement des immobilisations |
| 1525 | Provisions pour gros entretien ou grandes révisions |
| 1526 | Provisions pour remise en état |
| 1527 | Autres provisions pour charges |

---

## 16 — Emprunts et dettes assimilées

| Compte | Libellé | Obligatoire |
|---|---|---|
| 161 | Emprunts obligataires convertibles | |
| 1618 | Intérêts courus sur emprunts obligataires convertibles | |
| 162 | Obligations représentatives de passifs nets remis en fiducie | |
| 163 | Autres emprunts obligataires | |
| 1638 | Intérêts courus sur autres emprunts obligataires | |
| 164 | Emprunts auprès des établissements de crédit | ✅ |
| 1648 | Intérêts courus sur emprunts auprès des établissements de crédit | |
| 165 | Dépôts et cautionnements reçus | |
| 1651 | Dépôts | |
| 1655 | Cautionnements | |
| 1658 | Intérêts courus sur dépôts et cautionnements reçus | |
| 166 | Participation des salariés aux résultats | |
| 167 | Emprunts et dettes assortis de conditions particulières | |
| 168 | Autres emprunts et dettes assimilées | ✅ |
| 1681 | Autres emprunts | |
| 1685 | Rentes viagères capitalisées | |
| 1687 | Autres dettes | |
| 1688 | Intérêts courus sur autres emprunts et dettes assimilées | |
| 169 | Primes de remboursement des emprunts | |

---

## 17 — Dettes rattachées à des participations

| Compte | Libellé |
|---|---|
| 171 | Dettes rattachées à des participations — groupe |
| 174 | Dettes rattachées à des participations — hors groupe |
| 178 | Dettes rattachées à des sociétés en participation |

---

## 18 — Comptes de liaison des établissements et sociétés en participation

| Compte | Libellé |
|---|---|
| 181 | Comptes de liaison des établissements |
| 186 | Biens et prestations de services échangés entre établissements — charges |
| 187 | Biens et prestations de services échangés entre établissements — produits |
| 188 | Comptes de liaison des sociétés en participation |

---

## Règles d'imputation — Classe 1

| Opération | Débit | Crédit |
|---|---|---|
| Apport en capital | 4561 Apporteurs | 1013 Capital appelé versé |
| Distribution dividendes | 120 Résultat | 457 Associés dividendes |
| Affectation réserve légale | 120 Résultat | 1061 Réserve légale |
| Remboursement emprunt | 164 Emprunt | 512 Banque |
| Constatation provision risque | 681x Dotation | 15xx Provision |

---

## Références légales

- PCG — Règlement ANC 2014-03 modifié
- Code de Commerce Art. L123-12 à L123-23
- Art. L123-14 — Régularité, sincérité, image fidèle
