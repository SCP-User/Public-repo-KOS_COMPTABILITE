---
type: norme_fiscale
source: CGI_Art_256_a_283
version: 2026
tags: [tva, taux, deductibilite, collecte, regime, assujetti, facture, 44566, 44571]
applicable_a: [cycle_achat, cycle_vente, facture_fournisseur, note_de_frais]
---

# TVA — Règles Générales de Déductibilité

## Taux de TVA applicables en France (2026)

| Taux | Nature | Exemples |
|---|---|---|
| **20%** | Taux normal | Prestations de services, biens non listés |
| **10%** | Taux intermédiaire | Restauration, travaux de rénovation, transport |
| **5,5%** | Taux réduit | Produits alimentaires, livres, médicaments non remboursés |
| **2,1%** | Taux super-réduit | Médicaments remboursables, presse |
| **0%** | Exonéré | Exportations, certaines opérations intracommunautaires |

## Conditions de déductibilité de la TVA (CGI Art. 271)

La TVA est déductible si et seulement si :

1. **L'entreprise est assujettie à la TVA** (régime réel normal ou simplifié)
2. **La dépense est affectée à l'activité taxée** (pas à des activités exonérées)
3. **La facture est conforme** (mentions obligatoires — CGI Art. 289)
4. **La TVA figure sur la facture** (taux et montant explicites)
5. **La dépense n'est pas exclue** par une disposition spéciale (CGI Art. 206 et suivants)

## Principales exclusions du droit à déduction

| Nature de la dépense | Déductible | Référence |
|---|---|---|
| Véhicules de tourisme (achat) | NON | CGI Art. 206 IV |
| Carburant voiture de tourisme | 20% seulement | CGI Art. 206 IV |
| Cadeaux ≥ 73 € TTC/bénéficiaire/an | NON | CGI Art. 236 |
| Cadeaux < 73 € TTC/bénéficiaire/an | OUI | CGI Art. 236 |
| Repas d'affaires (justifiés) | OUI | BOFiP TVA-DED |
| Repas personnels | NON | |
| Logement dirigeants | NON | CGI Art. 206 IV |

## Comptes de TVA (Plan Comptable Général)

| Compte | Libellé | Usage |
|---|---|---|
| 44566 | TVA déductible sur autres biens et services | TVA récupérable sur achats |
| 44562 | TVA déductible sur immobilisations | TVA récupérable sur investissements |
| 44571 | TVA collectée | TVA facturée aux clients |
| 44551 | TVA à décaisser | Solde dû à l'État |
| 44567 | Crédit de TVA | TVA à reporter ou rembourser |

## Comptabilisation d'un achat avec TVA déductible

```
D 60XXXX  Achats        [montant HT]
D 44566   TVA déduc.    [montant TVA]
  C 401   Fournisseur                [montant TTC]
```

## Comptabilisation d'un achat avec TVA NON déductible

```
D 60XXXX  Achats        [montant TTC entier — HT + TVA non récupérée]
  C 401   Fournisseur                [montant TTC]
```

## Références légales

- CGI Art. 256 à 283 — Champ d'application TVA
- CGI Art. 271 — Droit à déduction
- CGI Art. 206 IV — Exclusions du droit à déduction
- CGI Art. 236 — TVA sur cadeaux
- BOFiP TVA-DED — Doctrine fiscale déductibilité
