# VIDEO_SCRIPT.md — KOS_COMPTA Demo Video (4 min)

**Audience:** Technical judges — GitLab AI Hackathon 2026 (DevOps / engineering)
**Format:** Screen recording (terminal) + voiceover — no camera needed
**Tool:** OBS Studio or ShareX (free)
**Language:** French voiceover

---

## Les 3 Factures de Démo

| # | Fichier | Contexte | Verdict attendu |
|---|---------|----------|----------------|
| 1 | `facture_A102.md` | 5 coffrets champagne 120€/unit — cadeaux clients | **REJET** — CGI Art.236 |
| 2 | `facture_B001.md` | Fournitures de bureau — facture complète | **CONFORME** |
| 3 | `CVM-2025-012558_*.md` | Vraie facture PDF — clinique vétérinaire | **AVERTISSEMENT** |

> **Cas 3 = le moment PDF.** C'est sur cette vraie facture qu'on montre la transformation PDF → Markdown avant l'audit.

---

## Technical Setup (before recording)

- Terminal font size: **14pt minimum**
- Theme: dark background
- Pré-charger les 3 factures dans `E3.1_Dropzone_Factures/`
- Avoir le PDF original de la facture vétérinaire dans `E3.1_Dropzone_Factures/input/`
- Faire un run test complet avant l'enregistrement

---

## Script (4 min — 240 sec)

---

### [0:00 — 0:20] HOOK (20 sec)

**Screen:** Terminal — afficher le verdict REJET de facture_A102

```bash
cat E4_AUDIT_ET_ROUTAGE/E4.1_Rapports_Conformite/RAPPORT_facture_A102_*.json
```

Montrer à l'écran :
```
"verdict": "REJET"
"action_erp": "BLOQUER"
"articles_appliques": ["CGI Art. 236 ..."]
```

**Voiceover :**
> "Voilà ce que KOS_COMPTA produit. Une facture entre. Le système l'analyse. Et il répond : REJET — avec les articles de loi cités, les corrections requises, et l'instruction ERP : BLOQUER. Aucune intervention humaine."

---

### [0:20 — 0:50] PROBLÈME (30 sec)

**Screen :** Rester sur le terminal, scroller le rapport REJET.

**Voiceover :**
> "Le problème est réel. En France, le Code de Commerce Art. L123-14 impose que chaque document entrant en comptabilité respecte trois principes : régularité, sincérité, image fidèle. Aujourd'hui cet audit est manuel — et une facture non conforme qui passe, c'est un risque de redressement fiscal. KOS_COMPTA automatise cet audit, à chaque commit, dans le pipeline GitLab CI/CD."

---

### [0:50 — 1:20] ARCHITECTURE (30 sec)

**Screen :** Arborescence du projet en terminal.

```bash
ls -la
ls E0_MOTEUR_AGENTIQUE/
ls E1_CORPUS_LEGAL_ETAT/
ls E3_INTERFACES_ACTEURS/E3.1_Dropzone_Factures/
```

**Voiceover :**
> "L'architecture est en 5 couches. E0 : le moteur agentique — les scripts Python. E1 : le corpus légal — CGI, PCG, BOFiP vectorisés dans ChromaDB. E3 : la dropzone des documents entrants. E4 : les sorties — rapports de rejet et payloads ERP. Le cerveau : Claude Sonnet 4.6. Le tribunal : le pipeline GitLab en 4 stages."

---

### [1:20 — 3:00] DEMO LIVE — 3 Factures (100 sec)

#### 1. PDF → Markdown (20 sec)

**Screen :** Montrer le PDF dans `input/`, lancer l'extraction.

```bash
ls E3_INTERFACES_ACTEURS/E3.1_Dropzone_Factures/input/
python E0_MOTEUR_AGENTIQUE/pdf_extractor.py --batch
cat E3_INTERFACES_ACTEURS/E3.1_Dropzone_Factures/Facture_-_CVM-2025-012558_*.md | head -30
```

**Voiceover :**
> "D'abord, un vrai PDF de facture — ici une facture de clinique vétérinaire. L'ETL le transforme automatiquement en Markdown structuré avec frontmatter YAML. C'est cette structure que Claude va auditer."

#### 2. Charger le KOS (10 sec)

```bash
python E0_MOTEUR_AGENTIQUE/ingest_kos.py
```

**Voiceover :**
> "Les 4 normes légales sont vectorisées dans ChromaDB. Le RAG est prêt."

#### 3. Lancer l'audit sur les 3 factures (70 sec)

```bash
python E0_MOTEUR_AGENTIQUE/agent_compliance.py
```

**Voiceover (au fil des verdicts qui apparaissent) :**

*(Facture A102)*
> "Facture A102 — coffrets champagne, 120€ l'unité. Le seuil légal CGI Art.236 est 73€. REJET. La TVA 100€ n'est pas déductible. Action ERP : BLOQUER."

*(Facture B001)*
> "Facture B001 — fournitures de bureau. Mentions obligatoires présentes, TVA 20% déductible, montants corrects. CONFORME. Payload ERP généré."

*(Facture vétérinaire — vraie facture)*
> "Facture clinique vétérinaire. Taux TVA 20% appliqué — mais les médicaments vétérinaires sont à 10% en France, CGI art.278-0 bis. Anomalie détectée. Plus : le document est au nom d'un particulier, lien professionnel non démontré. AVERTISSEMENT — REVUE HUMAINE requise."

---

### [3:00 — 3:30] ZOOM — Ce que Claude voit et l'œil humain manque (30 sec)

**Screen :** Afficher le rapport REJET de A102 en entier.

```bash
cat E4_AUDIT_ET_ROUTAGE/E4.1_Rapports_Conformite/RAPPORT_facture_A102_*.json
```

**Voiceover :**
> "Ce cas est parlant. La facture champagne a été soumise avec la mention 'usage professionnel — cadeaux clients'. Un comptable pressé pourrait valider. Claude, lui, croise avec CGI Art.236 : seuil 73€ TTC. 120€ > 73€. TVA non déductible. Rejet automatique avec corrections précises. C'est ça le KOS : la loi prime toujours sur l'intention déclarée."

---

### [3:30 — 4:00] ÉCONOMIE (30 sec)

**Screen :** `ITERATIONS_LOG.json` — les chiffres réels.

```bash
cat E0_MOTEUR_AGENTIQUE/logs/ITERATIONS_LOG.json | python -m json.tool | grep -E "documents_count|cout_total_eur"
```

**Voiceover :**
> "11 documents audités. Coût LLM total : 21 centimes. Soit environ 2 centimes par facture. À 1 000 factures par mois : 19€ de coût LLM. Un assistant comptable en France : 2 000 à 3 500€ par mois. À partir de 500 factures par mois, KOS_COMPTA est moins cher qu'une heure de prestation comptable — et il tourne 24h/24, cite les articles de loi, et ne fait jamais d'erreur de fatigue."

---

### [3:50 — 4:00] CLÔTURE (10 sec)

**Screen :** Laisser le terminal avec les verdicts visibles.

**Voiceover :**
> "Claude API est le juge. Le KOS est la loi. Le CI/CD est le tribunal. Aucun document non conforme n'entre en comptabilité."

---

## Post-Production Checklist

- [ ] Trim les silences entre commandes
- [ ] Title card au début : "KOS_COMPTA — GitLab AI Hackathon 2026"
- [ ] Export : 1080p, MP4
- [ ] Upload YouTube (non-listé) ou Vimeo
- [ ] Lien dans la soumission Devpost

---

## Messages clés pour les juges

1. **Ça tourne vraiment** — terminal live, pas de mock
2. **Claude API = moteur de conformité** — chaque verdict cite les articles que Claude a identifiés via RAG
3. **Vrai PDF traité** — pas que du Markdown manuel
4. **Vrai droit français** — CGI, PCG, BOFiP, ANC 2014-03
5. **Économie réelle** — 2 centimes/doc vs 2000€/mois d'assistant

---

*Script mis à jour le 2 mars 2026 — ERGO Capital / Adam*
