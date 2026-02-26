# ERGO_ID: PUBLISH_REPORT
"""
publish_report.py
=================
ERGO KOS_COMPTA — Stage REPORT

Lit les résultats d'audit produits dans E4 et publie un commentaire Markdown
structuré sur la Merge Request GitLab via l'API REST v4.
Fonctionne aussi en mode local (affichage console) si aucun contexte MR n'est détecté.

ERGO_REGISTRY:
    role         : Stage REPORT - publie le verdict de conformite sur GitLab MR
    version      : 1.0.0
    auteur       : ERGO Capital / Adam
    dependances  : requests
    entrees      : E4_AUDIT_ET_ROUTAGE/E4.1_Rapports_Conformite/RAPPORT_*.json
                   E4_AUDIT_ET_ROUTAGE/E4.2_Payloads_ERP/PAYLOAD_*.json
    sorties      : Commentaire GitLab MR (API REST)
    variable_env : GITLAB_TOKEN, CI_MERGE_REQUEST_IID, CI_PROJECT_ID
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("[ERROR] Module 'requests' manquant — pip install requests", file=sys.stderr)
    sys.exit(1)

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


ICONE: dict[str, str] = {
    "REJET": "🔴",
    "AVERTISSEMENT": "🟡",
    "CONFORME": "🟢",
    "ERREUR": "⚫",
}

RISQUE_ICONE: dict[str, str] = {
    "ELEVE": "🔴",
    "MOYEN": "🟡",
    "FAIBLE": "🟢",
}


def lire_rapports(report_dir: Path) -> list[dict]:
    """Charge tous les rapports JSON depuis E4.1_Rapports_Conformite.

    Args:
        report_dir: Chemin vers le dossier E4.1.

    Returns:
        Liste de dictionnaires {'fichier': str, 'data': dict} par rapport trouvé.
    """
    rapports: list[dict] = []
    for fichier in sorted(report_dir.glob("RAPPORT_*.json")):
        try:
            data = json.loads(fichier.read_text(encoding="utf-8"))
            rapports.append({"fichier": fichier.name, "data": data})
        except (json.JSONDecodeError, IOError) as e:
            print(f"  [WARN] Impossible de lire {fichier.name} : {e}")
    return rapports


def lire_payloads(payload_dir: Path) -> list[dict]:
    """Charge tous les payloads ERP JSON depuis E4.2_Payloads_ERP.

    Args:
        payload_dir: Chemin vers le dossier E4.2.

    Returns:
        Liste de dictionnaires {'fichier': str, 'data': dict} par payload trouvé.
    """
    payloads: list[dict] = []
    for fichier in sorted(payload_dir.glob("PAYLOAD_*.json")):
        try:
            data = json.loads(fichier.read_text(encoding="utf-8"))
            payloads.append({"fichier": fichier.name, "data": data})
        except (json.JSONDecodeError, IOError) as e:
            print(f"  [WARN] Impossible de lire {fichier.name} : {e}")
    return payloads


def formater_rapport(rapport: dict) -> str:
    """Formate un rapport de rejet ou avertissement en Markdown GitLab.

    Args:
        rapport: Dictionnaire {'fichier': str, 'data': dict} produit par lire_rapports().

    Returns:
        Bloc Markdown formaté pour la Merge Request.
    """
    data       = rapport["data"]
    verdict_obj = data.get("verdict", {})
    v          = verdict_obj.get("verdict", "INCONNU")
    risque     = verdict_obj.get("niveau_risque", "?")
    articles   = ", ".join(verdict_obj.get("articles_appliques", [])) or "—"
    corrections = verdict_obj.get("corrections_requises", [])
    imputation  = verdict_obj.get("imputation_recommandee", {})
    meta        = verdict_obj.get("_meta", {})

    blocs = [
        f"### {ICONE.get(v, '⚪')} `{v}` — {data.get('document_source', rapport['fichier'])}",
        "",
        f"**Motif :** {verdict_obj.get('motif', '—')}",
        f"**Articles appliqués :** `{articles}`",
        f"**Niveau de risque :** {RISQUE_ICONE.get(risque, '')} {risque}",
        f"**Action ERP :** `{verdict_obj.get('action_erp', '—')}`",
    ]

    if corrections:
        blocs += ["", "**Corrections requises :**"]
        blocs += [f"- {c}" for c in corrections]

    if imputation:
        blocs += ["", "**Imputation recommandée :**", "| Champ | Valeur |", "|---|---|"]
        blocs += [f"| {k} | `{v}` |" for k, v in imputation.items()]

    if meta:
        blocs += ["", f"*Analysé par `{meta.get('llm', '?')}` — coût estimé : {meta.get('cout_estime_eur', 0)} EUR*"]

    return "\n".join(blocs)


def formater_payload(payload: dict) -> str:
    """Formate un payload ERP CONFORME en Markdown GitLab.

    Args:
        payload: Dictionnaire {'fichier': str, 'data': dict} produit par lire_payloads().

    Returns:
        Bloc Markdown formaté pour la Merge Request.
    """
    data     = payload["data"]
    export   = data.get("ergo_pgi_export_v1", {})
    ecriture = export.get("ecriture", {})
    lignes   = ecriture.get("lignes", [])

    blocs = [
        f"### 🟢 `CONFORME` — {export.get('document_source', payload['fichier'])}",
        "",
        f"**Statut :** {export.get('compliance_status', '—')}",
        f"**Journal :** `{ecriture.get('journal', '—')}`",
        f"**Libellé :** {ecriture.get('libelle', '—')}",
        "",
        "**Écriture comptable :**",
        "| Compte | Débit | Crédit |",
        "|---|---|---|",
    ]
    blocs += [f"| `{l.get('compte', '?')}` | {l.get('debit', 0)} | {l.get('credit', 0)} |" for l in lignes]
    blocs += [
        "",
        f"*Analysé par `{export.get('analyse_par', '?')}` — coût estimé : {export.get('cout_eur', 0)} EUR*",
        f"✅ **Payload prêt pour injection ERP** — `{payload['fichier']}`",
    ]
    return "\n".join(blocs)


def construire_commentaire(rapports: list[dict], payloads: list[dict]) -> str:
    """Assemble le commentaire Markdown global pour la Merge Request.

    Args:
        rapports: Liste produite par lire_rapports().
        payloads: Liste produite par lire_payloads().

    Returns:
        Commentaire Markdown complet prêt à poster sur GitLab.
    """
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(rapports) + len(payloads)

    lignes = [
        "## 🤖 ERGO KOS_COMPTA — Rapport de Conformité Comptable",
        "",
        f"> Audit automatique · {ts} · {total} document(s) analysé(s)",
        f"> *The KOS is the legislator. The LLM is the executor. The CI/CD is the tribunal.*",
        "",
        "---",
        "",
    ]

    if not rapports and not payloads:
        lignes.append("⚠️ **Aucun document trouvé dans E3.1_Dropzone_Factures.**")
        return "\n".join(lignes)

    n_rejets = sum(1 for r in rapports if r["data"].get("verdict", {}).get("verdict") == "REJET")
    n_avert  = sum(1 for r in rapports if r["data"].get("verdict", {}).get("verdict") == "AVERTISSEMENT")

    lignes += [
        "| 🔴 REJETS | 🟡 AVERTISSEMENTS | 🟢 CONFORMES |",
        "|---|---|---|",
        f"| {n_rejets} | {n_avert} | {len(payloads)} |",
        "",
        "---",
        "",
    ]

    for r in rapports:
        lignes += [formater_rapport(r), "", "---", ""]

    for p in payloads:
        lignes += [formater_payload(p), "", "---", ""]

    lignes += ["", "*Powered by ERGO KOS_COMPTA · Anthropic Claude API · GitLab CI/CD*"]
    return "\n".join(lignes)


def poster_commentaire_mr(project_id: str, mr_iid: str, token: str, body: str) -> bool:
    """Poste un commentaire sur une Merge Request via l'API REST GitLab v4.

    Args:
        project_id: ID numérique du projet GitLab.
        mr_iid:     IID de la Merge Request (numéro interne au projet).
        token:      Personal Access Token GitLab (PRIVATE-TOKEN).
        body:       Corps Markdown du commentaire.

    Returns:
        True si le commentaire a été publié avec succès, False sinon.
    """
    url     = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes"
    headers = {"PRIVATE-TOKEN": token, "Content-Type": "application/json"}

    print(f"  → POST {url}")
    try:
        response = requests.post(url, headers=headers, json={"body": body}, timeout=30)
        if response.status_code in (200, 201):
            print(f"  ✓ Commentaire publié (note_id={response.json().get('id', '?')})")
            return True
        print(f"  [ERROR] GitLab API {response.status_code} : {response.text[:300]}", file=sys.stderr)
        return False
    except requests.RequestException as e:
        print(f"  [ERROR] Requête GitLab échouée : {e}", file=sys.stderr)
        return False


def afficher_commentaire_local(body: str) -> None:
    """Affiche le commentaire en mode local (aucun contexte MR détecté).

    Args:
        body: Corps Markdown du commentaire.
    """
    print("\n" + "═" * 60)
    print("  RAPPORT (mode local — pas de MR GitLab détectée)")
    print("═" * 60)
    print(body)
    print("═" * 60 + "\n")


def main() -> None:
    """Point d'entrée CLI du stage REPORT."""
    parser = argparse.ArgumentParser(
        description="ERGO KOS_COMPTA — Stage REPORT : publie le verdict de conformité sur GitLab MR"
    )
    parser.add_argument("--report-dir",  type=str)
    parser.add_argument("--payload-dir", type=str)
    parser.add_argument("--mr-iid",      type=str)
    parser.add_argument("--project-id",  type=str)
    parser.add_argument("--token",       type=str)
    args = parser.parse_args()

    report_dir  = Path(args.report_dir)  if args.report_dir  else Path("E4_AUDIT_ET_ROUTAGE/E4.1_Rapports_Conformite")
    payload_dir = Path(args.payload_dir) if args.payload_dir else Path("E4_AUDIT_ET_ROUTAGE/E4.2_Payloads_ERP")
    mr_iid      = args.mr_iid     or os.environ.get("CI_MERGE_REQUEST_IID", "")
    project_id  = args.project_id or os.environ.get("CI_PROJECT_ID", "")
    token       = args.token      or os.environ.get("GITLAB_TOKEN", "")

    print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] [REPORT] Lecture des résultats d'audit")

    rapports = lire_rapports(report_dir)
    payloads = lire_payloads(payload_dir)

    print(f"  → {len(rapports)} rapport(s) de rejet/avertissement")
    print(f"  → {len(payloads)} payload(s) ERP conforme(s)")

    commentaire = construire_commentaire(rapports, payloads)

    if mr_iid and project_id and token:
        print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] [REPORT] Publication sur MR !{mr_iid} (projet {project_id})")
        sys.exit(0 if poster_commentaire_mr(project_id, mr_iid, token, commentaire) else 1)
    else:
        print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] [REPORT] Pas de contexte MR — affichage local")
        afficher_commentaire_local(commentaire)
        sys.exit(0)


if __name__ == "__main__":
    main()
