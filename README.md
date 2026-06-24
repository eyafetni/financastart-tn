# FinançaStart TN 🇹🇳

### *La première plateforme IA qui révèle à l'entrepreneur tunisien la vérité sur sa bancabilité — pas celle qu'il imagine.*

> **AINS Hackathon 2026** · PNUD · GEWEET · ODC · IEEE · APII · AINS 4.0

---

## Le Problème

97,8% des entreprises tunisiennes sont des PME. Les banques débordent de liquidités (138% de ratio réglementaire). Et pourtant, l'encours crédit aux PME **recule**.

La raison : un entrepreneur sur deux croit être prêt pour un financement. Il ne l'est pas. Et aucun outil ne lui dit pourquoi.

**FinançaStart TN est le pont entre ces deux réalités.**

---

## La Solution

Un **Intelligent Financing Readiness Engine** — 3 modules IA intégrés qui interagissent autour d'un profil projet unifié :

```
[Entrepreneur]
      ↓
[F1 — Diagnostic Adaptatif]
      Questionnaire piloté par LLM · Stade réel · Gap perception/réalité · Blockers
      ↓
[F2 — Scoring Multi-Dimensionnel]
      5 scores AHP · Financing Readiness Index · Anomalies · Explications
      ↓
[F3 — RAG + Roadmap Tunisienne]
      40+ ressources réelles · Plan d'action personnalisé · Zéro hallucination
      ↓
[L'entrepreneur sait exactement ce qui le sépare du financement]
```

> ⚡ Un gap F1 déclenche automatiquement F3. Un sous-score faible F2 remonte des ressources ciblées. Les 3 modules interagissent — ils ne coexistent pas.

---

## Structure du Projet

```
financastart-tn/
│
├── README.md
│
├── /presentation/
│   └── FinancaStart_TN_Submission1.pptx    # Slides 1ère soumission
│
├── /ai/
│   ├── /f1_diagnostic/                     # Feature 1 — Diagnostic Adaptatif
│   ├── /f2_scoring/                        # Feature 2 — Scoring AHP
│   └── /f3_rag/                            # Feature 3 — RAG + Roadmap
│       └── /knowledge_base/               # 40+ ressources tunisiennes (JSON)
│
└── /app/                                   # Frontend — Dashboard bilingue FR/AR
```

---

## Les 3 Features

### F1 — Diagnostic Adaptatif

Questionnaire piloté par LLM — les questions s'adaptent en temps réel selon les réponses.

**6 stades de maturité :**

| # | Stade | Financement associé |
|---|-------|-------------------|
| 1 | Idéation | Concours / Love money |
| 2 | Market Validation | Microfinance BTS |
| 3 | Structuration | APII / ANPE |
| 4 | Fundraising | BFPME / Startup Act |
| 5 | Launch Planning | Capital risque / ANAVA |
| 6 | Growth | Lignes bancaires / AFD |

**Gap Detection — 3 cas documentés :**

| Auto-évaluation entrepreneur | Diagnostic réel | Écart |
|------------------------------|-----------------|-------|
| "Je suis prêt BFPME" | Structuration | 2 stades |
| "J'ai de la traction marché" | Idéation | 3 stades |
| "Mon projet est innovant" | Innovation Score < 30 | Score critique |

---

### F2 — Scoring Multi-Dimensionnel (AHP)

5 scores composites calculés via **Analytic Hierarchy Process (Saaty)** · Tous CR < 0.10 ✅

| Score | Poids FRI | Sous-dimensions |
|-------|-----------|-----------------|
| Market Score | 32% | TAM · Concurrence · Validation · Revenus |
| Commercial Score | 22% | Valeur · Produit · Pricing · Alignement |
| Innovation Score | 20% | Nouveauté · Tech · Barrière · Rupture |
| Scalability Score | 16% | Réplicabilité · Coûts · Géo · Manuel |
| Green Score | 10% | Climat · Eau · Sols · Ressources (PNUD) |

**Financing Readiness Index (FRI) :**
> ⚠️ Les scores ne sont pas des moyennes. Un Market Score < 30 plafonne le FRI à 40/100 — même si tous les autres scores sont excellents.

**Anomalies détectées automatiquement :**
- `Validation ≥ 70 ET Revenus ≤ 20` → −8 pts Market *(Stiglitz & Weiss 1981)*
- `Réplicabilité ≥ 70 ET Revenus ≤ 20` → −10 pts Scalability
- `Tous scores ≥ 70 ET Stade F1 = Idéation` → −15 pts global

**Ancrages théoriques :** Stiglitz & Weiss (1981) · WB Enterprise Survey 2024 · Startup Act Art. 3§4, Art. 12, Art. 17 · PNUD 4 piliers Green

---

### F3 — RAG + Roadmap Tunisienne

**Knowledge Base : 40+ ressources tunisiennes réelles, structurées et indexées**

| Catégorie | Ressources |
|-----------|-----------|
| Financement public | BFPME · BTS · FOPRODI · FTI · ANPE |
| Capital & incubateurs | ANAVA · Smart Capital · Flat6Labs |
| Programmes EU / AFD | EU4Business · AFD Tunisie · UNDP |
| Procédures administratives | RNE · APII · Startup Act · Formes juridiques |
| Acteurs écosystème | Mentors · Réseaux · Associations |

**🚫 Règle absolue :** Toute recommandation non tracée à une ressource KB réelle est rejetée automatiquement. Zéro hallucination.

**Roadmap personnalisée :**
```
Immédiat   (0–2 sem.)  →  Enregistrement RNE          [source : registre-entreprises.tn]
Court terme (1–2 mois) →  3 lettres d'intention clients [source : Programme APII]
Moyen terme (3–6 mois) →  Dossier BFPME                [source : bfpme.com.tn]
```

---

## Évaluation

| Feature | Métrique | Protocole |
|---------|----------|-----------|
| F1 Diagnostic | Accuracy · F1-score · Matrice de confusion | 10 profils synthétiques labellisés |
| F3 RAG | RAGAS : Faithfulness · Relevancy · Precision | 10 profils × questions types |

---

## Stack Technique

| Composant | Technologie |
|-----------|-------------|
| F1 Diagnostic | LLM (branchement dynamique adaptatif) |
| F2 Scoring | Python (calcul AHP matriciel + règles anomalies) |
| F3 RAG | Pipeline RAG (retrieval vectoriel + LLM grounded) |
| KB Ingestion | Python · requests · BeautifulSoup |
| Frontend | React · TailwindCSS · Bilingue FR/AR |
| Évaluation | RAGAS · Classification metrics |

---

## Timeline

| Jours | Objectif |
|-------|----------|
| J1–J3 | Knowledge Base JSON · Taxonomie F1 · Matrices AHP F2 |
| J4–J6 | Prototype F1 + F2 + F3 · Intégration cross-module |
| J7 | Demo Day · Soumission finale · 26 juin 2026 |

---

## Équipe

| Rôle | Responsabilité |
|------|---------------|
| Chef de projet + F1 | Taxonomie · Branchement · Gap detection |
| F2 Scoring Engine | AHP · Pondération · Anomalies · FRI |
| F3 KB + RAG | Scraping · Indexation · Retrieval |
| Frontend | Dashboard · Mon Parcours · UI/UX bilingue |
| Intégration + Évaluation | API · RAGAS · Cross-module |

---

## Pourquoi Maintenant

- **824 593** entreprises en Tunisie — 97,8% sont des PME *(IACE 2025)*
- **138%** ratio de liquidité des banques privées *(BCT 2025)*
- **167%** de garanties exigées pour un prêt PME *(Banque Mondiale)*
- **40,5%** de chômage chez les jeunes *(Trésor France 2024)*

> FinançaStart TN ne répond pas aux questions. Il dit la vérité.

---

*AINS Hackathon 2026 · Demo Day 26 juin 2026*
