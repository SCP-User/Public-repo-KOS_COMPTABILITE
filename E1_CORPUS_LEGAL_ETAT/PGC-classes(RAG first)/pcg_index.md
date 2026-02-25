---
type: index_corpus
source: PCG_ANC_2014-03
version: 2025
tags: [pcg, index, navigation, rag]
rag_chunk: PCG_INDEX
---

# PCG — Index de Navigation KOS_COMPTA

> Ce fichier est le point d'entrée RAG pour le corpus PCG.
> L'agent doit charger CE fichier en premier, puis cibler la classe pertinente.

---

## Carte des classes

| Classe | Intitulé | Fichier | Usage principal |
|---|---|---|---|
| 1 | Comptes de Capitaux | `pcg_classe_1_capitaux.md` | Bilan passif — financement, réserves, emprunts, provisions |
| 2 | Comptes d'Immobilisations | `pcg_classe_2_immobilisations.md` | Bilan actif — immobilisations, amortissements, dépréciations |
| 3 | Comptes de Stocks et d'En-Cours | `pcg_classe_3_stocks.md` | Bilan actif — stocks, en-cours, dépréciations stocks |
| 4 | Comptes de Tiers | `pcg_classe_4_tiers.md` | Fournisseurs, clients, TVA, État, personnel — ⚠️ zone haute conformité |
| 5 | Comptes Financiers | `pcg_classe_5_financiers.md` | Trésorerie, banque, caisse, VMP |
| 6 | Comptes de Charges | `pcg_classe_6_charges.md` | Achats, services ext., personnel, taxes, dotations — ⚠️ déductibilité fiscale |
| 7 | Comptes de Produits | `pcg_classe_7_produits.md` | Ventes, CA, subventions, produits financiers, reprises |
| 8 | Comptes Spéciaux | `pcg_classe_8_speciaux.md` | Hors bilan, engagements, bilan ouverture/clôture |

---

## Routing par type de document entrant

| Type de document | Classes prioritaires à charger |
|---|---|
| Facture fournisseur | 4 (401, 44566) + 6 (60x, 61x, 62x) |
| Facture client | 4 (411, 44571) + 7 (70x) |
| Note de frais | 6 (625x, 6234) + 4 (44566) |
| Bulletin de paie | 6 (641x, 645x) + 4 (421, 431) |
| Acquisition immobilisation | 2 (21x, 28x) + 4 (404, 44562) |
| Déclaration TVA (CA3) | 4 (44566, 44571, 44551) |
| Opération bancaire | 5 (512) + 4 (401 ou 411) |
| Dotation amortissement | 6 (681x) + 2 (28x) |
| Cession immobilisation | 2 (21x, 28x) + 7 (775) + 6 (675) |

---

## Comptes critiques KOS_COMPTA — vigilance maximale

| Compte | Règle | Référence |
|---|---|---|
| 6234 | Cadeau ≥ 73€ TTC → pas de déduction TVA, imputation TTC | CGI Art. 236 |
| 44566 | TVA déductible uniquement si facture conforme | CGI Art. 289 |
| 44571 | TVA collectée — doit figurer sur chaque vente soumise | CGI Art. 256 |
| 401 | Fournisseur — facture obligatoire pour tout achat | Code Commerce Art. L441-9 |
| 625x | Notes de frais — justificatifs obligatoires + caractère professionnel | CGI Art. 39-1 |
| 512 | Banque — paiement espèces > 1 000€ interdit entre pro | CMF Art. L112-6 |

---

## Source officielle

- **PCG Nathan 2025** — Liste intégrale des comptes (document physique — usage BTS + hackathon)
- Règlement ANC 2014-03 modifié
- Version numérique : ANC (Autorité des Normes Comptables) — https://www.anc.gouv.fr
