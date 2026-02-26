---
type: norme_fiscale
source: CGI_Art_289
version: 2026
tags: [facture, mentions_obligatoires, tva, fournisseur, numero_facture, siret, tva_intracommunautaire]
applicable_a: [cycle_achat, cycle_vente, facture_fournisseur]
---

# Mentions Obligatoires sur les Factures — CGI Art. 289

## Règle principale

Toute facture doit comporter des mentions obligatoires pour être juridiquement valide et permettre la déduction de TVA. L'absence d'une mention obligatoire entraîne le rejet de la déduction de TVA et peut constituer une infraction fiscale.

## Liste des mentions obligatoires (CGI Art. 289 II)

| Mention | Obligatoire | Remarque |
|---|---|---|
| Date d'émission de la facture | OUI | |
| Numéro de facture (séquentiel) | OUI | Unique, basé sur une séquence chronologique |
| Numéro de TVA intracommunautaire du vendeur | OUI | Format FR + 11 chiffres |
| Numéro de TVA intracommunautaire de l'acheteur | OUI | Si assujetti à la TVA |
| Nom et adresse du vendeur | OUI | |
| Nom et adresse de l'acheteur | OUI | |
| Numéro SIRET du vendeur | OUI | 14 chiffres |
| Désignation précise des biens/services | OUI | |
| Quantité | OUI | |
| Prix unitaire HT | OUI | |
| Taux de TVA applicable | OUI | Par ligne si taux différents |
| Montant de TVA par taux | OUI | |
| Montant total HT | OUI | |
| Montant total TTC | OUI | |
| Date de la livraison ou de la prestation | OUI | Si différente de la date de facture |
| Mentions spéciales (autoliquidation, franchise de TVA…) | SI applicable | |

## Conséquences de l'absence de mentions

- **TVA non déductible** si numéro de TVA fournisseur absent
- **Facture nulle** si numéro de facture absent ou non séquentiel
- **Risque de redressement** en cas de contrôle fiscal
- Imputation comptable : les charges restent déductibles IS, mais la TVA est rejetée

## Imputation comptable en cas de facture incomplète

| Situation | Compte débit | Compte crédit |
|---|---|---|
| Facture sans numéro TVA fournisseur | 6XXXX (HT + TVA) | 401 |
| Facture complète | 6XXXX (HT) + 44566 (TVA) | 401 |

## Références légales

- CGI Art. 289 — Obligations de facturation
- BOFiP TVA-DECLA-30-10-20
- Directive TVA 2006/112/CE Art. 226
- Code de Commerce Art. L123-14 (régularité)
