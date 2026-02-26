# KOS_COMPTA — Compliance Agent for GitLab Duo

  > AI agent that audits accounting documents against French fiscal law      
  > in real time — directly inside your GitLab issues and merge requests.    

  ## The Problem

  Every French company faces the same bottleneck: accounting documents       
  (invoices, expense reports) must be manually checked for compliance        
  before entering the ERP. One missed TVA rule or a wrong PCG account        
  can trigger a fiscal audit. This is slow, error-prone, and expensive.      

  ## The Solution

  KOS_COMPTA is a GitLab Duo Flow that acts as an autonomous compliance      
  officer. Mention `@ai-kos-compliance` in any issue or MR, and the agent    
  instantly audits the document against French law and posts a structured    
  verdict.

  ## How It Works

  @ai-kos-compliance [paste invoice content or attach file]
          ↓
    GitLab Duo Flow triggered
          ↓
    KOS rules applied (CGI + PCG + Code Commerce)
          ↓
    Structured verdict posted as comment

  **Verdict format:**
  - ✅ CONFORME → Ready for ERP injection
  - ❌ REJET → Blocked with legal explanation
  - ⚠️ AVERTISSEMENT → Human review required

  Each verdict includes:
  - Applicable legal articles (CGI, PCG)
  - Required corrections
  - Recommended PCG account mapping (debit/credit)
  - Risk level (FAIBLE / MOYEN / ÉLEVÉ)

  ## Usage

  In any GitLab issue or MR, mention the flow with the document to audit:    

  @ai-kos-compliance

  Facture ACME – 15/02/2026
  Fournisseur: ACME SAS – SIRET 123 456 789 00012
  Montant HT: 100€ – TVA 20%: 20€ – TTC: 120€
  Objet: Bouteilles de champagne pour client

  The agent will respond with a full compliance verdict in seconds.

  ## Architecture

  GitLab Duo Flow (this repo)
      ↓ embeds KOS rules in system prompt
      ↓ reads issue/file content
      ↓ Claude API (claude-sonnet-4-6) — Anthropic Bonus eligible
      ↓ posts structured verdict

  Full Backend (KOS_COMPTA main repo)
      ↓ ChromaDB RAG — French law vectorized (E1 corpus)
      ↓ ETL pipeline — PDF/XML → structured Markdown
      ↓ GitLab CI/CD — 4 stages (detect → audit → route → report)

  **Main repository:**
  [Public-repo-KOS_COMPTABILITE](https://github.com/SCP-User/Public-repo-KOS_COMPTABILITE)

  ## Legal Rules Embedded (KOS)

  | Rule | Article | Coverage |
  |---|---|---|
  | Mandatory invoice fields | CGI Art.289 | Number, date, SIRET, VAT amounts
   |
  | VAT deductibility | CGI Art.271 | Professional use, company name required
   |
  | Business gifts VAT | CGI Art.236 | Non-deductible above €73 TTC |        
  | Reduced VAT rates | CGI Art.278-0 bis | 5.5% / 10% specific categories | 
  | Deductible expenses | CGI Art.39-1 | Business purpose required |
  | Accounting standards | PCG ANC 2014-03 | Accounts 6xx, 4xx mapping |     
  | True and fair view | Code Commerce Art.L123-14 | Regularity, sincerity | 

  ## Stack

  | Component | Technology |
  |---|---|
  | Agent Platform | GitLab Duo Agent Platform |
  | LLM | Claude claude-sonnet-4-6 (Anthropic API) |
  | Rules Engine | KOS — Knowledge Operating System |
  | Full Pipeline | ChromaDB + Python + GitLab CI/CD |

  ## License

  MIT — See LICENSE file.

  ---

  *Built for GitLab AI Hackathon 2026 — ERGO Capital / Adam*
  *Targeting: Most Impactful + Anthropic Bonus ($10K)*

  ---