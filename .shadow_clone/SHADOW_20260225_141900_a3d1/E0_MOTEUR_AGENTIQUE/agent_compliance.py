# ERGO_ID: COMPLIANCE_AGENT
"""
agent_compliance.py
===================
ERGO KOS_COMPTA — Compliance ERP Middleware
Hackathon GitLab AI 2026

Pipeline d'audit de conformité comptable en 5 étapes :
    1. lire_facture         : lecture et extraction frontmatter YAML depuis E3.1
    2. charger_normes       : RAG vectoriel ChromaDB (multilingual-e5-base) sur E1 + E2
    3. analyser_avec_claude : audit LLM via Anthropic API (claude-sonnet-4-6)
    4. router_verdict       : routage vers E4.1 (rejet/avert.) ou E4.2 (conforme)
    5. log_iteration        : journal structuré dans ITERATIONS_LOG.json

ERGO_REGISTRY:
    role         : Pipeline principal d'audit de conformite comptable (5 etapes)
    version      : 1.1.0
    auteur       : ERGO Capital / Adam
    dependances  : KOS_COMPTA_Taxonomie.json, KOS_COMPTA_Agentique.json, E1_CORPUS_LEGAL_ETAT,
                   chromadb, sentence-transformers (intfloat/multilingual-e5-base), KOS_DB/
    entrees      : E3_INTERFACES_ACTEURS/E3.1_Dropzone_Factures/*.md
    sorties      : E4_AUDIT_ET_ROUTAGE/E4.1_Rapports_Conformite/RAPPORT_*.json
                   E4_AUDIT_ET_ROUTAGE/E4.2_Payloads_ERP/PAYLOAD_*.json
                   E0_MOTEUR_AGENTIQUE/logs/ITERATIONS_LOG.json
    variable_env : ANTHROPIC_API_KEY (obligatoire)
"""

import os
import json
import glob
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
import anthropic


BASE_DIR        = Path(__file__).parent.parent
E1_LEGAL        = BASE_DIR / "E1_CORPUS_LEGAL_ETAT"
E2_SOP          = BASE_DIR / "E2_SOP_INTERNE_ET_ERP"
E3_DROPZONE     = BASE_DIR / "E3_INTERFACES_ACTEURS" / "E3.1_Dropzone_Factures"
E4_RAPPORTS     = BASE_DIR / "E4_AUDIT_ET_ROUTAGE" / "E4.1_Rapports_Conformite"
E4_PAYLOADS     = BASE_DIR / "E4_AUDIT_ET_ROUTAGE" / "E4.2_Payloads_ERP"
ITERATIONS_LOG  = BASE_DIR / "E0_MOTEUR_AGENTIQUE" / "logs" / "ITERATIONS_LOG.json"


def lire_facture(chemin: Path) -> dict:
    """Lit un document Markdown et extrait le frontmatter YAML et le corps.

    Args:
        chemin: Chemin absolu vers le fichier .md à lire.

    Returns:
        Dictionnaire contenant :
            - fichier (str)      : nom du fichier
            - frontmatter (dict) : paires clé/valeur extraites du bloc YAML
            - corps (str)        : contenu Markdown hors frontmatter
            - tags (str)         : valeur brute du champ 'tags' du frontmatter
    """
    contenu = chemin.read_text(encoding="utf-8")
    fm: dict = {}
    match = re.search(r"^---\n(.*?)\n---", contenu, re.DOTALL)
    if match:
        for ligne in match.group(1).split("\n"):
            if ":" in ligne:
                cle, _, val = ligne.partition(":")
                fm[cle.strip()] = val.strip()
    corps = re.sub(r"^---\n.*?\n---\n", "", contenu, flags=re.DOTALL).strip()
    return {
        "fichier": chemin.name,
        "frontmatter": fm,
        "corps": corps,
        "tags": fm.get("tags", "[]"),
    }


def charger_normes(tags_facture: str) -> str:
    """Recherche les normes légales et SOP pertinentes via ChromaDB (RAG vectoriel).

    Se connecte au client ChromaDB persistant (./KOS_DB) et interroge la collection
    "kos_knowledge_base" par similarité cosinus. La requête est vectorisée avec le
    modèle intfloat/multilingual-e5-base, préfixée "query: " conformément à
    l'entraînement asymétrique E5. Retourne les 3 chunks les plus pertinents sous
    forme de texte structuré pour le prompt LLM.

    Mode dégradé : si KOS_DB est absent ou la collection inaccessible, bascule sur
    la recherche substring dans les fichiers .md après logging.warning explicite.

    Args:
        tags_facture: Chaîne brute du champ 'tags' du frontmatter (ex: "[tva, cadeau, achat]").

    Returns:
        Contexte structuré des normes les plus similaires (RAG) ou résultat du fallback substring.
    """
    kos_db = BASE_DIR / "KOS_DB"

    if kos_db.exists():
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            client     = chromadb.PersistentClient(path=str(kos_db))
            collection = client.get_collection("kos_knowledge_base")
            model      = SentenceTransformer("intfloat/multilingual-e5-base")
            tags_str   = tags_facture.replace("[", "").replace("]", "").strip()
            vecteur    = model.encode([f"query: {tags_str}"], normalize_embeddings=True).tolist()
            resultats  = collection.query(query_embeddings=vecteur, n_results=3)
            docs       = resultats.get("documents", [[]])[0]
            metas      = resultats.get("metadatas", [[]])[0]
            if docs:
                blocs: list[str] = []
                for i, (doc, meta) in enumerate(zip(docs, metas), start=1):
                    blocs.append(
                        f"\n\n### NORME {i} — {meta.get('source', 'N/A')} "
                        f"[{meta.get('fichier', 'inconnu')}]\n"
                        f"Type : {meta.get('type', '')} | "
                        f"Tags : {meta.get('tags', '')} | "
                        f"Applicable : {meta.get('applicable_a', '')}\n\n"
                        f"{doc}"
                    )
                logging.info("charger_normes() — RAG ChromaDB : %d chunks retenus.", len(docs))
                return "".join(blocs)
        except Exception as exc:
            logging.warning(
                "charger_normes() — KOS_DB inaccessible (%s), bascule sur fallback substring.",
                exc,
            )
    else:
        logging.warning(
            "charger_normes() — KOS_DB absent (%s). "
            "Lancer ingest_kos.py pour initialiser la base vectorielle. "
            "Bascule sur fallback substring.",
            kos_db,
        )

    normes_trouvees: list[dict] = []
    tags = [t.strip().strip("[]'\"") for t in tags_facture.split(",")]

    for dossier in [E1_LEGAL, E2_SOP]:
        for fichier in glob.glob(str(dossier / "**/*.md"), recursive=True):
            contenu = Path(fichier).read_text(encoding="utf-8")
            for tag in tags:
                if tag and tag.lower() in contenu.lower():
                    normes_trouvees.append({"source": Path(fichier).name, "contenu": contenu})
                    break

    if not normes_trouvees:
        return "Aucune norme spécifique trouvée. Appliquer règles générales PCG."

    return "".join(
        f"\n\n### SOURCE : {n['source']}\n{n['contenu']}"
        for n in normes_trouvees
    )


def analyser_avec_claude(facture: dict, normes: str) -> dict:
    """Soumet le document et les normes KOS à Claude pour un audit de conformité.

    Appelle l'API Anthropic (claude-sonnet-4-6) avec un prompt structuré et extrait
    le verdict JSON de la réponse. Enrichit le résultat avec les métadonnées LLM.

    Args:
        facture: Dictionnaire produit par lire_facture().
        normes:  Contexte textuel des normes applicables produit par charger_normes().

    Returns:
        Dictionnaire JSON du verdict contenant :
            - verdict (str)                : CONFORME | REJET | AVERTISSEMENT
            - motif (str)                  : explication du verdict
            - articles_appliques (list)    : références légales citées
            - corrections_requises (list)  : actions correctives si applicable
            - imputation_recommandee (dict): écriture comptable suggérée
            - niveau_risque (str)          : FAIBLE | MOYEN | ELEVE
            - action_erp (str)             : INJECTER | BLOQUER | REVUE_HUMAINE
            - _meta (dict)                 : llm, tokens, coût estimé

    Raises:
        KeyError: Si la variable d'environnement ANTHROPIC_API_KEY est absente.
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"].strip())

    system_prompt = (
        "Tu es un agent de conformité comptable expert en droit fiscal français.\n\n"
        "Tu reçois un corpus de normes légales (KOS) et une facture à auditer.\n"
        "Réponds UNIQUEMENT en JSON pur selon ce format exact :\n\n"
        "{\n"
        '  "verdict": "CONFORME" | "REJET" | "AVERTISSEMENT",\n'
        '  "motif": "explication courte et précise",\n'
        '  "articles_appliques": ["référence légale"],\n'
        '  "corrections_requises": ["correction si applicable"],\n'
        '  "imputation_recommandee": {\n'
        '    "compte_debit": "XXXXX",\n'
        '    "compte_credit": "XXXXX",\n'
        '    "montant_ht": 0.00,\n'
        '    "tva_deductible": 0.00,\n'
        '    "tva_non_deductible": 0.00,\n'
        '    "montant_ttc": 0.00\n'
        "  },\n"
        '  "niveau_risque": "FAIBLE" | "MOYEN" | "ELEVE",\n'
        '  "action_erp": "INJECTER" | "BLOQUER" | "REVUE_HUMAINE"\n'
        "}"
    )

    user_message = (
        f"## NORMES KOS\n{normes}\n\n"
        f"## DOCUMENT\n"
        f"Fichier : {facture['fichier']}\n"
        f"Tags : {facture['tags']}\n"
        f"Montant TTC : {facture['frontmatter'].get('montant_ttc', 'N/A')}\n\n"
        f"{facture['corps']}\n\n"
        "Audite et réponds en JSON."
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    reponse_brute = message.content[0].text.strip()
    try:
        verdict = json.loads(reponse_brute)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", reponse_brute, re.DOTALL)
        verdict = (
            json.loads(match.group())
            if match
            else {"verdict": "ERREUR", "motif": reponse_brute}
        )

    verdict["_meta"] = {
        "llm": "claude-sonnet-4-6",
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "cout_estime_eur": round(
            (message.usage.input_tokens * 0.000003)
            + (message.usage.output_tokens * 0.000015),
            5,
        ),
    }
    return verdict


def router_verdict(facture: dict, verdict: dict) -> Optional[str]:
    """Route le document vers E4.1 (rejet/avertissement) ou E4.2 (conforme).

    Args:
        facture: Dictionnaire produit par lire_facture().
        verdict: Dictionnaire produit par analyser_avec_claude().

    Returns:
        Nom du fichier généré dans E4 (str), ou None si aucun fichier produit.
    """
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_base    = facture["fichier"].replace(".md", "")
    fichier_sorti: Optional[str] = None

    if verdict.get("verdict") in ["REJET", "AVERTISSEMENT"]:
        rapport = {
            "document_source": facture["fichier"],
            "date_audit": timestamp,
            "verdict": verdict,
        }
        sortie = E4_RAPPORTS / f"RAPPORT_{nom_base}_{timestamp}.json"
        sortie.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
        fichier_sorti = sortie.name
        print(f"  → RAPPORT REJET  : {sortie.name}")

    if verdict.get("verdict") == "CONFORME":
        imp = verdict.get("imputation_recommandee", {})
        payload = {
            "ergo_pgi_export_v1": {
                "document_source": facture["fichier"],
                "date_export": timestamp,
                "compliance_status": "conforme",
                "analyse_par": verdict["_meta"]["llm"],
                "cout_eur": verdict["_meta"]["cout_estime_eur"],
                "ecriture": {
                    "journal": "ACH",
                    "libelle": f"Import auto — {facture['fichier']}",
                    "lignes": [
                        {"compte": imp.get("compte_debit"),  "debit": imp.get("montant_ht"),      "credit": 0},
                        {"compte": "44566",                  "debit": imp.get("tva_deductible"),   "credit": 0},
                        {"compte": imp.get("compte_credit"), "debit": 0, "credit": imp.get("montant_ttc")},
                    ],
                },
            }
        }
        sortie = E4_PAYLOADS / f"PAYLOAD_{nom_base}_{timestamp}.json"
        sortie.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        fichier_sorti = sortie.name
        print(f"  → PAYLOAD ERP    : {sortie.name}")

    return fichier_sorti


def _lire_iterations() -> list[dict]:
    """Charge le contenu existant de ITERATIONS_LOG.json.

    Returns:
        Liste des itérations précédentes, ou liste vide si le fichier est absent ou corrompu.
    """
    if not ITERATIONS_LOG.exists():
        return []
    try:
        return json.loads(ITERATIONS_LOG.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _prochain_iteration_id(existantes: list[dict]) -> str:
    """Génère l'identifiant séquentiel de la prochaine itération.

    Args:
        existantes: Liste des itérations déjà enregistrées.

    Returns:
        Identifiant au format "ITER_XXXX" (ex: "ITER_0003").
    """
    return f"ITER_{len(existantes) + 1:04d}"


def log_iteration(
    pipeline_id: str,
    timestamp_start: str,
    documents_resultats: list[dict],
) -> None:
    """Enregistre une itération complète du pipeline dans ITERATIONS_LOG.json.

    Une itération correspond à un run complet (un appel à main()), pouvant couvrir
    plusieurs documents. Chaque itération est ajoutée à la liste cumulative.

    Schema d'une entrée :
        iteration_id          : identifiant séquentiel "ITER_XXXX"
        pipeline_id           : identifiant CI/CD ou "local"
        timestamp_start       : ISO 8601 — début du run
        timestamp_end         : ISO 8601 — fin du run
        duration_seconds      : durée totale en secondes
        documents_count       : nombre de documents traités
        resume                : comptage par verdict {CONFORME, REJET, AVERTISSEMENT, ERREUR}
        cout_total_eur        : coût LLM total de l'itération
        tokens_total_input    : tokens en entrée cumulés
        tokens_total_output   : tokens en sortie cumulés
        documents             : liste détaillée par document (voir ci-dessous)

    Schema documents[i] :
        fichier, type, verdict, motif, articles_appliques, niveau_risque,
        action_erp, llm, tokens_input, tokens_output, cout_eur, fichier_sorti

    Args:
        pipeline_id:          Identifiant du pipeline CI/CD ou "local".
        timestamp_start:      Horodatage ISO 8601 du début du run.
        documents_resultats:  Liste des résultats par document, chacun contenant
                              les clés 'facture', 'verdict', 'fichier_sorti'.
    """
    timestamp_end = datetime.now().isoformat()
    debut = datetime.fromisoformat(timestamp_start)
    fin   = datetime.fromisoformat(timestamp_end)
    duree = round((fin - debut).total_seconds(), 2)

    resume: dict[str, int] = {"CONFORME": 0, "REJET": 0, "AVERTISSEMENT": 0, "ERREUR": 0}
    cout_total  = 0.0
    tokens_in   = 0
    tokens_out  = 0
    docs_detail: list[dict] = []

    for item in documents_resultats:
        v      = item["verdict"]
        meta   = v.get("_meta", {})
        verd   = v.get("verdict", "ERREUR")
        resume[verd] = resume.get(verd, 0) + 1
        cout_total  += meta.get("cout_estime_eur", 0.0)
        tokens_in   += meta.get("input_tokens", 0)
        tokens_out  += meta.get("output_tokens", 0)

        docs_detail.append({
            "fichier":            item["facture"]["fichier"],
            "type":               item["facture"]["frontmatter"].get("type", "inconnu"),
            "verdict":            verd,
            "motif":              v.get("motif", ""),
            "articles_appliques": v.get("articles_appliques", []),
            "niveau_risque":      v.get("niveau_risque", ""),
            "action_erp":         v.get("action_erp", ""),
            "llm":                meta.get("llm", ""),
            "tokens_input":       meta.get("input_tokens", 0),
            "tokens_output":      meta.get("output_tokens", 0),
            "cout_eur":           meta.get("cout_estime_eur", 0.0),
            "fichier_sorti":      item.get("fichier_sorti"),
        })

    existantes = _lire_iterations()
    entree = {
        "iteration_id":        _prochain_iteration_id(existantes),
        "pipeline_id":         pipeline_id,
        "timestamp_start":     timestamp_start,
        "timestamp_end":       timestamp_end,
        "duration_seconds":    duree,
        "documents_count":     len(documents_resultats),
        "resume":              resume,
        "cout_total_eur":      round(cout_total, 5),
        "tokens_total_input":  tokens_in,
        "tokens_total_output": tokens_out,
        "documents":           docs_detail,
    }
    existantes.append(entree)
    ITERATIONS_LOG.write_text(
        json.dumps(existantes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  ✓ Itération loguée : {entree['iteration_id']}")


def main() -> None:
    """Point d'entrée du pipeline de conformité.

    Orchestre les 5 étapes pour chaque document présent dans E3.1_Dropzone_Factures,
    puis enregistre l'itération complète dans ITERATIONS_LOG.json.
    """
    print("\n╔══════════════════════════════════════╗")
    print("║  ERGO KOS_COMPTA — Compliance Agent  ║")
    print("╚══════════════════════════════════════╝\n")

    pipeline_id      = os.environ.get("CI_PIPELINE_ID", "local")
    timestamp_start  = datetime.now().isoformat()
    documents_resultats: list[dict] = []

    factures = list(E3_DROPZONE.glob("*.md"))
    if not factures:
        print("  Aucune facture en attente dans E3.1.")
        return

    for chemin in factures:
        print(f"  ► Traitement : {chemin.name}")
        facture       = lire_facture(chemin)
        normes        = charger_normes(facture["tags"])
        verdict       = analyser_avec_claude(facture, normes)
        fichier_sorti = router_verdict(facture, verdict)

        print(f"  ✓ Verdict    : {verdict.get('verdict')}")
        print(f"  ✓ Motif      : {verdict.get('motif')}")
        print(f"  ✓ Risque     : {verdict.get('niveau_risque')}")
        print(f"  ✓ Action ERP : {verdict.get('action_erp')}")
        print(f"  ✓ Coût LLM   : {verdict.get('_meta', {}).get('cout_estime_eur')} EUR\n")

        documents_resultats.append({
            "facture": facture,
            "verdict": verdict,
            "fichier_sorti": fichier_sorti,
        })

    log_iteration(pipeline_id, timestamp_start, documents_resultats)
    print("  Pipeline terminé.\n")


if __name__ == "__main__":
    main()
