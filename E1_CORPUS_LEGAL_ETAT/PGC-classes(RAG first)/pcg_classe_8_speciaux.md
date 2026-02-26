---
type: norme_comptable
source: PCG_ANC_2014-03
version: 2025
classe: 8
intitule: Comptes Spéciaux
tags: [pcg, classe8, engagements, hors_bilan, bilan_ouverture, bilan_cloture, resultat_affectation]
applicable_a: [bilan, hors_bilan, engagements_donnes, engagements_recus]
rag_chunk: PCG_CLASSE_8
---

# PCG — Classe 8 : Comptes Spéciaux

> Comptes hors bilan et comptes de situation. Usage limité — engagements donnés et reçus, bilan d'ouverture/clôture.

---

## 80 — Engagements

### Engagements donnés par l'entité

| Compte | Libellé |
|---|---|
| 801 | Engagements donnés par l'entité |
| 8011 | Avals, cautions, garanties |
| 8014 | Effets circulant sous l'endos de l'entité |
| 8016 | Redevances crédit-bail restant à courir |
| 80161 | Crédit-bail mobilier |
| 80165 | Crédit-bail immobilier |
| 8018 | Autres engagements donnés |

### Engagements reçus par l'entité

| Compte | Libellé |
|---|---|
| 802 | Engagements reçus par l'entité |
| 8021 | Avals, cautions, garanties |
| 8024 | Créances escomptées non échues |
| 8026 | Engagements reçus pour utilisation en crédit-bail |
| 80261 | Crédit-bail mobilier |
| 80265 | Crédit-bail immobilier |
| 8028 | Autres engagements reçus |

### Contrepartie des engagements

| Compte | Libellé |
|---|---|
| 809 | Contrepartie des engagements |
| 8091 | Contrepartie 801 |
| 8092 | Contrepartie 802 |

---

## 88 — Résultat en instance d'affectation

| Compte | Libellé |
|---|---|
| 88 | Résultat en instance d'affectation |

> Utilisé lors de l'assemblée générale pour constater l'affectation du résultat avant écriture définitive en classe 1.

---

## 89 — Bilan

| Compte | Libellé | Usage |
|---|---|---|
| 890 | Bilan d'ouverture | Reprise soldes N-1 au 1er janvier |
| 891 | Bilan de clôture | Arrêté des comptes au 31 décembre |

> Comptes techniques utilisés uniquement lors des opérations de début et fin d'exercice.

---

## Règles d'imputation — Classe 8

| Opération | Débit | Crédit |
|---|---|---|
| Aval donné à tiers | 8011 Avals donnés | 8091 Contrepartie |
| Caution reçue d'un client | 8092 Contrepartie | 8021 Cautions reçues |
| Crédit-bail — engagement restant à courir | 8016x Redevances restantes | 8091 Contrepartie |
| Ouverture exercice | 890 Bilan ouverture | Comptes de bilan actif/passif |
| Clôture exercice | Comptes de bilan | 891 Bilan clôture |

---

## Note d'usage KOS_COMPTA

La classe 8 est **rarement auditée en conformité courante** — elle ne génère pas de flux de trésorerie directs.
Points de vigilance néanmoins :
- Les engagements de crédit-bail (8016x) doivent correspondre aux contrats enregistrés
- Les cautions (8011 / 8021) doivent figurer dans l'annexe des comptes annuels (obligation légale)
- Le compte 88 ne doit pas rester soldé après l'AGO

---

## Références légales

- PCG — Règlement ANC 2014-03 modifié
- Code de Commerce Art. L123-13 — Obligation d'annexe
- Code de Commerce Art. L232-1 — Dépôt des comptes annuels
