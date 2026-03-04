# VIDEO_SCRIPT.md — KOS_COMPTA Demo Video (4 min)

**Audience:** Technical judges — GitLab AI Hackathon 2026 (DevOps / engineering)
**Format:** Screen recording (terminal) + voiceover — no camera needed
**Tool:** OBS Studio or ShareX (free)
**Language:** French voiceover

---

## ÉTAT INITIAL À L'ÉCRAN (avant REC)

```
E3.1_Dropzone_Factures/
├── input/
│   ├── FA_ILEK_domicile_Adam.pdf          ← vrai PDF
│   └── Facture_-_CVM-2025-012558_*.pdf    ← vrai PDF
├── facture_A102.md                        ← champagne REJET
└── facture_B001.md                        ← fournitures CONFORME

archive/  ← vide
```

> Terminal font ≥ 14pt · Dark theme · Fenêtre plein écran

---

## Les 3 Cas de Démo

| # | Document | Nature | Verdict attendu | Accroche |
|---|----------|--------|----------------|----------|
| 1 | `facture_A102.md` | Champagne 120€/coffret × 5 | **REJET** CGI Art.236 | La TVA est non-déductible au-dessus de 73€ — même si c'est "pour les clients" |
| 2 | `facture_B001.md` | Fournitures bureau | **CONFORME** → ERP | 3 écritures comptables générées, zéro humain |
| 3 | `FA_ILEK_domicile_Adam.pdf` | Attestation d'abonnement (faux document) | **REJET** CGI Art.289 | Le système reconnaît que ce n'est pas une facture |

> Cas 3 = moment clé : montrer que l'agent ne se laisse pas tromper par un document qui "ressemble" à quelque chose de comptable.

---

## Séquence Exacte (3 commandes)

```bash
# 1. ETL — PDF → Markdown structuré
python E0_MOTEUR_AGENTIQUE/pdf_extractor.py --batch

# 2. Audit IA — Claude + RAG ChromaDB
python E0_MOTEUR_AGENTIQUE/agent_compliance.py

# 3. Export ERP — CONFORME → CSV CEGID
python E0_MOTEUR_AGENTIQUE/export_erp.py
```

---

## Script (4 min — 240 sec)

---

### [0:00 — 0:20] HOOK (20 sec)

**Screen :** Terminal — afficher le verdict REJET de A102 déjà calculé.

```bash
cat E4_AUDIT_ET_ROUTAGE/E4.1_Rapports_Conformite/RAPPORT_facture_A102_*.json
```

Zoomer sur :
```json
"verdict": "REJET",
"action_erp": "BLOQUER",
"articles_appliques": ["CGI Art. 236"]
```

**Voiceover :**
> "Voilà ce que KOS_COMPTA produit. Une facture entre. Le système l'analyse. Et il répond : **REJET** — avec les articles de loi, les corrections requises, et l'instruction ERP : BLOQUER. Zéro intervention humaine."

**Accroche à dire :**
> *"Ce n'est pas de l'IA qui devine. C'est de l'IA qui lit le Code Général des Impôts."*

---

### [0:20 — 0:50] PROBLÈME (30 sec)

**Screen :** Rester sur terminal, scroller lentement le rapport.

**Voiceover :**
> "Le problème est réel. En France, une facture non conforme qui passe en comptabilité, c'est un risque de redressement fiscal. Le Code de Commerce Art. L123-14 impose : régularité, sincérité, image fidèle. Aujourd'hui, cet audit est manuel — un comptable vérifie à l'œil. KOS_COMPTA l'automatise, à chaque commit, dans le pipeline GitLab CI/CD."

**Accroche à dire :**
> *"Une facture de champagne à 120€ soumise comme 'cadeau client professionnel' — un comptable pressé valide. Claude, lui, connaît CGI Art.236 : 73€ maximum. REJET."*

---

### [0:50 — 1:20] ARCHITECTURE (30 sec)

**Screen :** Arborescence du projet.

```bash
ls -1
ls E0_MOTEUR_AGENTIQUE/
ls E1_CORPUS_LEGAL_ETAT/
```

**Voiceover :**
> "L'architecture en 5 couches. E0 : le moteur — les scripts Python. E1 : le corpus légal — CGI, PCG, BOFiP vectorisés dans ChromaDB. E2 : les procédures internes de l'entreprise cliente. E3 : la dropzone des documents entrants. E4 : les sorties — rapports de rejet et payloads ERP. Cerveau : Claude Sonnet 4.6. Tribunal : pipeline GitLab 4 stages."

**Accroche à dire :**
> *"Le KOS est le législateur. Le LLM est l'exécuteur. Le CI/CD est le tribunal."*

---

### [1:20 — 3:00] DEMO LIVE (100 sec)

#### Commande 1 — ETL : PDF → Markdown (25 sec)

```bash
ls E3_INTERFACES_ACTEURS/E3.1_Dropzone_Factures/input/
python E0_MOTEUR_AGENTIQUE/pdf_extractor.py --batch
```

**Voiceover :**
> "Deux vrais PDFs dans le dossier input. L'ETL les transforme automatiquement en Markdown structuré — frontmatter YAML avec type, montants, date — prêt pour le LLM."

Montrer la sortie du fichier converti :
```bash
head -25 "E3_INTERFACES_ACTEURS/E3.1_Dropzone_Factures/FA_ILEK_domicile_Adam_*.md"
```

---

#### Commande 2 — Audit IA (50 sec)

```bash
python E0_MOTEUR_AGENTIQUE/agent_compliance.py
```

**Voiceover au fil des verdicts :**

*(A102 — champagne)*
> "Facture A102. Coffrets champagne, 120€ l'unité. Seuil légal : 73€. **REJET**. La TVA 100€ est non déductible. ERP : BLOQUER."

*(B001 — fournitures)*
> "Facture B001. Fournitures de bureau. Mentions obligatoires présentes, calcul cohérent, TVA 20% déductible. **CONFORME**. Payload ERP généré — compte 60225."

*(ILEK — attestation)*
> "Document ILEK. Et là, le moment intéressant : c'est une attestation de domicile, pas une facture. Aucun montant, aucun numéro de facture. L'agent le détecte immédiatement — **REJET**, CGI Art.289, document non comptable."

**Accroche à dire sur le cas ILEK :**
> *"On aurait pu soumettre n'importe quel document PDF. Le système reconnaît que ce n'est pas une pièce comptable — et le bloque. C'est ça la robustesse."*

---

#### Commande 3 — Export ERP (25 sec)

```bash
python E0_MOTEUR_AGENTIQUE/export_erp.py
cat E4_AUDIT_ET_ROUTAGE/E4.3_Imports_ERP/IMPORT_CEGID_*.csv
```

Montrer le CSV :
```
DATE;JOURNAL;COMPTE;SENS;MONTANT;LIBELLE;STATUT_KOS
04/03/2026;ACH;60225;D;250.00;Achat - facture_B001;CONFORME
04/03/2026;ACH;44566;D;50.00;Achat - facture_B001;CONFORME
04/03/2026;ACH;401;C;300.00;Achat - facture_B001;CONFORME
```

**Voiceover :**
> "La facture CONFORME est automatiquement transformée en écriture comptable en partie double — prête à importer dans CEGID, Sage ou Pennylane. Trois lignes : la charge, la TVA déductible, le fournisseur. La règle HT + TVA = TTC est vérifiée mathématiquement avant tout export."

**Accroche à dire :**
> *"De la dropzone au fichier ERP : zéro clic humain pour les documents conformes."*

---

### [3:00 — 3:30] ZOOM — Ce que l'œil humain manque (30 sec)

**Screen :** Rapport REJET A102 en entier.

```bash
cat E4_AUDIT_ET_ROUTAGE/E4.1_Rapports_Conformite/RAPPORT_facture_A102_*.json | python -m json.tool
```

**Voiceover :**
> "Ce cas est parlant. La facture champagne était présentée comme 'cadeaux clients professionnels'. Un comptable pressé pourrait valider. Claude, lui, connaît CGI Art.236 : 73€ TTC maximum par bénéficiaire et par an. 120€ > 73€. REJET avec corrections précises. La loi prime toujours sur l'intention déclarée."

---

### [3:30 — 4:00] ÉCONOMIE (30 sec)

**Screen :** ITERATIONS_LOG — chiffres réels.

```bash
python -c "
import json
log = json.load(open('E0_MOTEUR_AGENTIQUE/logs/ITERATIONS_LOG.json'))
total_docs = sum(i['documents_count'] for i in log)
total_cost = sum(i['cout_total_eur'] for i in log)
print(f'{total_docs} documents — coût total : {total_cost:.4f} EUR')
print(f'Soit {total_cost/total_docs*100:.2f} centimes/doc')
"
```

**Voiceover :**
> "13 documents audités. Coût LLM total : 21 centimes. 2 centimes par facture. À 1 000 documents par mois : moins de 20€. Un assistant comptable en France : 2 000 à 3 500€ par mois. À partir de 500 factures, KOS_COMPTA est moins cher qu'une heure de prestation — et il tourne 24h/24, cite les articles, et ne fait jamais d'erreur de fatigue."

**Accroche finale :**
> *"L'IA ne remplace pas le comptable. Elle lui supprime le travail répétitif — pour qu'il se concentre sur les cas complexes que la machine a marqués AVERTISSEMENT."*

**Screen :** Laisser le terminal avec les verdicts visibles.

---

## NOTE — Limites du système (honnêteté intellectuelle)

> Mentionner brièvement — ça renforce la crédibilité technique.

Avec 4 normes E1 actuellement dans ChromaDB, si la norme applicable n'est pas vectorisée, Claude extrapole — et peut produire un verdict partiellement incorrect.

**Garde-fou système :** AVERTISSEMENT par défaut si doute, jamais CONFORME en aveugle. Chaque verdict cite les articles → le reviewer humain vérifie la source.

**Ce qu'il faut dire :**
> *"Le RAG n'est pas une vérité absolue. C'est un premier filtre structuré et traçable. L'humain a toujours le dernier mot sur les AVERTISSEMENT."*

---

## POUR S'ENTRAÎNER — Compta expliquée aux devs

> Ce que tu dois pouvoir expliquer simplement à un jury de devs/DevOps.

### 1. La partie double
Chaque opération = un débit + un crédit. Toujours équilibré.
**Pour un dev :** c'est comme un commit atomique en DB — tu ne peux pas écrire sur un compte sans contre-passer sur un autre.
```
Débit  60225 (Charge fournitures)  250€
Débit  44566 (TVA déductible)       50€
──────────────────────────────────────
Crédit   401 (Fournisseur)         300€   ← HT + TVA = TTC ✓
```

### 2. Le PCG — Plan Comptable Général
C'est le namespace officiel des comptes comptables français.
- **Classe 4** → Tiers (fournisseurs = 401, clients = 411, TVA = 44566)
- **Classe 6** → Charges (fournitures 60225, téléphone 6261, honoraires 6221)
- **Classe 7** → Produits (ventes, prestations)
**Pour un dev :** c'est une enum obligatoire définie par l'État, version 2025. L'agent recommande le bon compte PCG dans chaque verdict.

### 3. La TVA déductible
Quand ton entreprise achète quelque chose pour son activité, elle peut récupérer la TVA qu'elle a payée — à condition que la dépense soit "affectée à des opérations taxées" (CGI Art.271).
**Si la dépense est personnelle → TVA non déductible.**
**Si le cadeau dépasse 73€ → TVA non déductible** (CGI Art.236).
**Pour un dev :** c'est un flag booléen sur chaque dépense. KOS_COMPTA le calcule.

### 4. Les mentions obligatoires (CGI Art.289)
Une facture sans ces champs = pièce comptable invalide :
- Numéro de facture (séquentiel, non réutilisable)
- Date d'émission
- SIRET/numéro TVA du vendeur ET de l'acheteur
- Désignation + quantité des biens/services
- Prix HT, taux TVA, montant TVA, montant TTC
**Pour un dev :** c'est un schéma de validation avec des champs requis. Le système vérifie chaque champ.

### 5. REJET vs AVERTISSEMENT vs CONFORME
- **CONFORME** = toutes les règles passent → injection ERP automatique
- **AVERTISSEMENT** = règle ambiguë, information manquante → revue humaine requise
- **REJET** = violation légale claire → blocage ERP, rapport motivé
**Pour un dev :** c'est un enum de statut de validation, avec un circuit de routage différent pour chaque valeur.

### 6. Accroche pour expliquer l'intérêt à un dev
> "Imagine que ton CI/CD empêche le merge si une dépense viole le Code des Impôts. C'est exactement ce que fait KOS_COMPTA — mais pour la comptabilité de l'entreprise."

---

## Post-Production Checklist

- [ ] Trim les silences entre commandes (> 2 sec)
- [ ] Title card : "KOS_COMPTA — GitLab AI Hackathon 2026"
- [ ] Zoom x1.2 sur les verdicts JSON
- [ ] Export : 1080p, MP4
- [ ] Upload YouTube (non-listé) ou Vimeo → lien Devpost

---

## Messages clés pour les juges

1. **Ça tourne vraiment** — terminal live, pas de mock
2. **Claude API = moteur de conformité légale** — verdict cité avec articles de loi via RAG
3. **Vrai PDF traité** — ETL inclus dans la démo
4. **Vrai droit français** — CGI, PCG, BOFiP, ANC 2014-03
5. **Pipeline complet** — PDF → md → audit → ERP CSV en 3 commandes
6. **Économie réelle** — ~2 centimes/doc vs 2 000€/mois d'assistant

---

*Script mis à jour le 4 mars 2026 — ERGO Capital / Adam*
