---
type: procedure
source: SOP_ENTREPRISE
version: 2026
tags: [entreprise, siret, sasu, tva, regime_fiscal, activite, ergo_capital]
applicable_a: [cycle_achat, cycle_vente, notes_de_frais, tva, is]
---

# SOP ENTREPRISE — ERGO Capital SASU

> ⚠️ DOCUMENT DE SIMULATION — Entreprise fictive créée pour la démonstration KOS_COMPTA.
> Ce fichier est chargé par le RAG (ChromaDB) afin de contextualiser les audits de conformité comptable.

---

## Identité Juridique

| Champ | Valeur |
|-------|--------|
| **Raison sociale** | ERGO Capital |
| **Forme juridique** | SASU (Société par Actions Simplifiée Unipersonnelle) |
| **SIRET** | 987 654 321 00015 |
| **SIREN** | 987 654 321 |
| **N° TVA intracommunautaire** | FR45 987 654 321 |
| **Code NAF / APE** | 6920Z — Activités comptables |
| **Capital social** | 1 000,00 € |
| **Date de création** | 15 janvier 2024 |
| **Siège social** | 2 Rue de Casablanca, 31400 Toulouse |
| **Dirigeant (Président)** | Adam Pieri |

---

## Régime Fiscal

| Champ | Valeur |
|-------|--------|
| **Régime d'imposition des bénéfices** | IS — Impôt sur les Sociétés (taux 15% < 42 500€, 25% au-delà) |
| **Régime TVA** | Régime réel normal — TVA collectée et déductible |
| **Taux TVA standard** | 20% (activités de conseil) |
| **Franchise TVA** | NON (SASU assujettie à TVA dès le 1er euro) |
| **Exercice comptable** | 1er janvier → 31 décembre |

---

## Activité et Objet Social

ERGO Capital est une société de conseil spécialisée dans :
- **Conseil en intelligence artificielle et automatisation comptable**
- **Développement de solutions MLOps et pipelines de données**
- **Formation professionnelle** en IA appliquée à la gestion
- **Implémentation de systèmes ERP** (Sage, CEGID, Pennylane)
- **Audit de conformité réglementaire** assisté par LLM

Clients cibles : TPE, PME, cabinets comptables, directions financières.

---

## Dépenses Professionnelles Déductibles (CONFORME par défaut)

Les dépenses suivantes sont considérées comme **charges professionnelles déductibles** pour ERGO Capital, sous réserve de justificatifs conformes (CGI art.39-1) :

### Informatique et Logiciels
- Abonnements cloud : AWS, GCP, Azure, Anthropic API, OpenAI API
- Licences logicielles : IDE, outils MLOps, solutions BI
- Matériel informatique professionnel (ordinateurs, serveurs, périphériques)
- Hébergement, noms de domaine, services SaaS
- **Compte PCG recommandé : 6064 (fournitures informatiques) / 6156 (abonnements)**

### Fournitures et Équipement Bureau
- Papeterie, cartouches, petit matériel de bureau
- Mobilier de bureau professionnel
- **Compte PCG recommandé : 6064 (fournitures de bureau)**

### Télécommunications
- Abonnement téléphonique professionnel (forfait dédié ou prorata usage pro)
- Abonnement internet (prorata télétravail si domicile — CGI art.39)
- **Compte PCG recommandé : 6261 (frais téléphone) / 6268 (autres frais télécommunications)**

### Énergie — Télétravail Domicile
- Électricité, gaz : déductible au prorata de la surface professionnelle (CGI art.39)
- Règle applicable : surface bureau / surface totale du logement × montant facture
- **Justificatif requis : quittance + plan surface ou bail indiquant surface**
- **Sans justificatif de surface → AVERTISSEMENT obligatoire**
- **Compte PCG recommandé : 6061 (eau, gaz, énergie)**

### Formation et Documentation
- Formations professionnelles (compta, IA, MLOps, RGPD, fiscalité)
- Livres, revues et documentation technique professionnelle
- **Compte PCG recommandé : 6183 (documentation) / 6311 (formation)**

### Déplacements Professionnels
- Transport (train, avion) avec justificatif et objet professionnel
- Hébergement hôtel sur mission client
- **Compte PCG recommandé : 6251 (voyages et déplacements)**

### Repas et Frais de Représentation
- Repas professionnel avec client ou partenaire (avec justificatif + convive noté)
- Plafond raisonnable : < 80€ TTC par couvert (au-delà → AVERTISSEMENT)
- **Compte PCG recommandé : 6257 (réceptions) / 6256 (frais de restauration)**

### Honoraires Externes
- Expert-comptable, commissaire aux comptes, avocat, notaire
- Sous-traitance technique (freelances, ESN)
- **Compte PCG recommandé : 6221 (commissions) / 6226 (honoraires)**

---

## Dépenses NON Déductibles (REJET systématique)

Les dépenses suivantes **ne sont pas déductibles** et doivent être rejetées par l'agent :

| Type de dépense | Motif de rejet | Article applicable |
|-----------------|---------------|-------------------|
| Soins vétérinaires pour animal de compagnie personnel | Dépense personnelle — aucun lien professionnel | CGI art.39-1 |
| Cadeaux clients > 73€ TTC par an et par bénéficiaire | Plafond cadeaux d'affaires dépassé | CGI art.236 |
| Factures au nom d'un particulier (sans SIRET société) | Dépense non engagée au nom de l'entreprise | CGI art.39, L123-22 |
| Documents non comptables (attestations, contrats sans montant) | Absence de mentions obligatoires facture | CGI art.289 |
| Frais de vacances, loisirs personnels | Dépense personnelle | CGI art.39-1 |
| Amendes et pénalités | Expressément exclus | CGI art.39-2 |

---

## Règle TVA Déductible

- TVA déductible sur toutes les dépenses professionnelles affectées à des opérations imposables (CGI art.271)
- TVA **non déductible** sur : dépenses de logement (sauf hôtel mission), véhicules de tourisme, frais personnels
- En cas de doute sur le taux appliqué → **AVERTISSEMENT** + REVUE_HUMAINE

---

## Instructions pour l'Agent KOS_COMPTA

Lorsqu'une facture est émise **au nom d'ERGO Capital** (SIRET 987 654 321 00015) ou adressée à **Adam Pieri en qualité de Président SASU** pour une dépense relevant de l'activité sociale ci-dessus :

1. Vérifier que la dépense figure dans la liste des charges déductibles
2. Vérifier les mentions obligatoires CGI art.289 (numéro facture, date, SIRET fournisseur, montants HT/TVA/TTC)
3. En cas de conformité totale → **CONFORME** + imputation PCG recommandée
4. En cas de doute sur la nature pro/perso → **AVERTISSEMENT** + REVUE_HUMAINE
5. En cas de dépense clairement personnelle ou document non comptable → **REJET** immédiat
