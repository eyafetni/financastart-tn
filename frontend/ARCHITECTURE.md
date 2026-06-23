# 🏗️ Project Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     AINS DASHBOARD APPLICATION                  │
│                    (React 19 + TailwindCSS)                      │
└─────────────────────────────────────────────────────────────────┘

┌─ ROUTING LAYER ───────────────────────────────────────────────────┐
│                                                                    │
│  App.jsx (Router Setup)                                           │
│    ├─ Route: "/"              → Dashboard.jsx                    │
│    ├─ Route: "/parcours"      → MyPath.jsx                       │
│    └─ Route: "/questionnaire" → Questionnaire.jsx                │
│                                                                    │
│  Navbar.jsx (Navigation Links)                                   │
│    ├─ Dashboard Link          (icon: TrendingUp)                 │
│    ├─ Mon Parcours Link       (icon: Calendar)                   │
│    ├─ Questionnaire Link      (icon: ClipboardList) [NEW]        │
│    ├─ Language Toggle         (🇫🇷/العربية)                     │
│    └─ Context Display         (Secteur + Localisation)           │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─ DATA LAYER ──────────────────────────────────────────────────────┐
│                                                                    │
│  dashboard.json (JSON Source of Truth)                            │
│    ├─ Profile: entrepreneur_id, startup_name, secteur           │
│    ├─ Maturity: stade_reel, stade_percu, gap_detecte            │
│    ├─ Metrics: gaps[], blockers[], scores, roadmap              │
│    └─ Questionnaire: answers { responses[] } [NEW]              │
│                           │                                       │
│                           ↓                                       │
│  dataAdapter.js (Transform Raw → Component Ready)               │
│    └─ getAdaptedData() → Returns adapted object with:           │
│           ├─ maturityIndicators                                 │
│           ├─ scores { market, commercial, etc }                 │
│           ├─ financing_readiness                                │
│           ├─ blockers { by priority }                           │
│           └─ roadmap { by horizon }                             │
│                           │                                       │
│  questionnaireService.js [NEW] (Business Logic)                 │
│    ├─ getApplicableQuestions(data)                              │
│    │    └─ Filters by condition: (data) => boolean              │
│    ├─ saveAnswer(questionId, answer)                            │
│    │    └─ Stores to localStorage                               │
│    ├─ getStoredAnswers()                                        │
│    │    └─ Retrieves from localStorage                          │
│    └─ exportAnswersForJSON()                                    │
│         └─ Formats for file download                            │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─ COMPONENT LAYER ─────────────────────────────────────────────────┐
│                                                                    │
│  Dashboard.jsx (Main View)                                       │
│    ├─ Receives: adaptedData, lang                               │
│    └─ Composes:                                                 │
│        ├─ MaturityIndicator      (stade_reel vs stade_percu)   │
│        ├─ Context Card           (secteur + localisation)       │
│        ├─ ScoreBars              (5 dimension scores)           │
│        ├─ FinancingReadiness     (financing gauge)             │
│        ├─ PriorityBlockers       (blockers by priority)        │
│        └─ RoadmapTimeline        (action items by horizon)     │
│                                                                    │
│  Questionnaire.jsx [NEW] (Questionnaire View)                   │
│    ├─ Receives: lang                                            │
│    ├─ Uses: questionnaireService functions                      │
│    ├─ State:                                                    │
│    │   ├─ questions[]            (filtered by conditions)       │
│    │   ├─ currentIndex           (question navigation)          │
│    │   ├─ answers{}              (user responses)               │
│    │   └─ completed              (form completion status)       │
│    └─ Features:                                                 │
│        ├─ Progress bar           (% complete)                   │
│        ├─ Category badges        (visual grouping)              │
│        ├─ Question navigation    (Prev/Next/Reset)             │
│        ├─ Input types            (radio/checkbox/text)         │
│        ├─ Completion screen      (summary + export)            │
│        └─ Export to JSON         (file download)               │
│                                                                    │
│  MyPath.jsx (Historical View)                                   │
│    └─ Currently: Informational placeholder                      │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌─ STATE FLOW ──────────────────────────────────────────────────────┐
│                                                                    │
│  1. User Action (Answer Question)                                │
│      ↓                                                            │
│  2. handleAnswer(questionId, value)                              │
│      ↓                                                            │
│  3. saveAnswer() → localStorage.setItem()                        │
│      ↓                                                            │
│  4. State Update: answers[questionId] = {answer, timestamp}     │
│      ↓                                                            │
│  5. Component Re-render with Updated Progress                   │
│      ↓                                                            │
│  6. On Export: exportAnswersForJSON() → Download                │
│      ↓                                                            │
│  7. (Future) Backend API: POST /api/questionnaire/save          │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌─ CONDITIONAL LOGIC FLOW ──────────────────────────────────────────┐
│                                                                    │
│  Questionnaire Component Mounts                                  │
│      ↓                                                            │
│  useEffect: Load entrepreneur data                               │
│      ↓                                                            │
│  Call: getApplicableQuestions(entrepreneurData)                  │
│      ↓                                                            │
│  Service: Filter allQuestions by condition                       │
│      ├─ Question.condition(data) === true  ✓ Include            │
│      └─ Question.condition(data) === false ✗ Exclude            │
│      ↓                                                            │
│  Return: Filtered questions[] based on:                          │
│      ├─ data.secteur                (agri-food filter)          │
│      ├─ data.stade_reel             (structuration filter)      │
│      ├─ data.stade_percu            (fundraising filter)        │
│      ├─ data.gap_detecte            (divergence filter)         │
│      └─ custom conditions           (complex logic)             │
│      ↓                                                            │
│  Render: Only applicable questions shown to user                 │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌─ BILINGUAL ARCHITECTURE ──────────────────────────────────────────┐
│                                                                    │
│  1. Data Structure (EVERYWHERE):                                 │
│     label: { fr: 'Texte français', ar: 'النص العربي' }          │
│                                                                    │
│  2. Component Receives lang Prop:                                │
│     function Component({ lang }) { ... }                        │
│                                                                    │
│  3. Display with Language:                                       │
│     <span>{label[lang]}</span>                                  │
│     → Output: "Texte français" or "النص العربي"                 │
│                                                                    │
│  4. RTL Handling (in parent):                                    │
│     if (lang === 'ar') {                                        │
│       document.documentElement.dir = 'rtl'                      │
│     }                                                            │
│     → HTML becomes right-to-left                                │
│                                                                    │
│  5. Language Toggle in Navbar:                                  │
│     Click: 🇫🇷 ↔ العربية                                        │
│     Effect: lang state updates → all components re-render      │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌─ DATA PERSISTENCE LAYER ──────────────────────────────────────────┐
│                                                                    │
│  ⚡ IMMEDIATE (Session):                                          │
│  └─ React Component State                                        │
│                                                                    │
│  💾 SHORT-TERM (Browser):                                        │
│  ├─ localStorage.questionnaire_answers                          │
│  │   └─ { questionId: { answer, timestamp } }                  │
│  └─ Persists across: Page refresh, Tab close/reopen             │
│                                                                    │
│  📁 MANUAL EXPORT (File):                                        │
│  └─ exportAnswersForJSON()                                      │
│     └─ Downloads file with answers                              │
│                                                                    │
│  🗄️ LONG-TERM (Backend) [Future]:                               │
│  ├─ Backend API: POST /api/questionnaire/save                  │
│  ├─ Database: Stores responses                                  │
│  └─ Sync: localStorage → Backend → dashboard.json              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌─ TECH STACK ──────────────────────────────────────────────────────┐
│                                                                    │
│  Frontend:                                                       │
│    ├─ React 19.2.6          (UI framework)                       │
│    ├─ React Router 7.18.0   (Client-side routing)               │
│    ├─ TailwindCSS 4.3.1     (Styling)                           │
│    └─ Lucide React 1.20.0   (Icons)                             │
│                                                                    │
│  Build:                                                          │
│    ├─ Vite 8.0.12           (Dev server + build)                │
│    └─ ESLint                (Code linting)                       │
│                                                                    │
│  Storage:                                                        │
│    ├─ JSON (dashboard.json) (Source of truth)                   │
│    ├─ localStorage          (Session persistence)               │
│    └─ Future: Database      (Long-term storage)                 │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌─ KEY METRICS ─────────────────────────────────────────────────────┐
│                                                                    │
│  7 Questions Available                                           │
│  6 Questions Show for Current Entrepreneur (ENT-001)            │
│  2 Conditional Questions:                                        │
│    ├─ Agri-food specifics (question 3)                          │
│    └─ Legal structure details (question 5)                      │
│  100% Bilingual (FR + AR)                                       │
│  3 Question Types Supported (radio/checkbox/text)               │
│  Responsive: Mobile, Tablet, Desktop                            │
│  Storage: localStorage + JSON export                            │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: "User Answers Question"

```
User clicks radio button for "Statut légal: SARL"
            ↓
Component: handleAnswer('legal_status', 'sarl')
            ↓
Service: saveAnswer('legal_status', 'sarl')
            ↓
localStorage.setItem('questionnaire_answers', {
  'legal_status': {
    'answer': 'sarl',
    'timestamp': '2026-06-16T10:30:00.000Z'
  }
})
            ↓
Component State Updates: answers.legal_status = 'sarl'
            ↓
Progress Bar Recalculates: 1 of 6 answered = 16%
            ↓
Component Re-renders with:
  - Updated progress
  - Visual feedback (checkmark)
  - Next button enabled (if last question)
            ↓
User sees: Progress updated, answer saved ✓
```

## Conditional Question Example: "Agri-Food Question"

```
Dashboard Data:
{
  "secteur": "agri-food",           ← ✓ Matches condition
  "stade_reel": "Structuration"     ← Data loaded
}
            ↓
Questionnaire Mounts:
  getApplicableQuestions(data)
            ↓
Check Question 3 (agri_specifics):
  condition: (data) => data.secteur === 'agri-food'
  condition(data) = true             ← ✓ Include!
            ↓
Check Question 4 (funding_readiness):
  condition: (data) => data.stade_percu === 'Fundraising' && 
                        data.stade_reel !== 'Fundraising'
  condition(data) = false            ← ✗ Exclude (stade_percu is "Fundraising" but condition also checks other fields)
            ↓
Result: Question 3 appears, Question 4 hidden
            ↓
User only sees relevant questions for their profile ✓
```

---

## Summary

**The AINS Dashboard is built on these principles:**

1. ✅ **Single Source of Truth**: dashboard.json
2. ✅ **Service Layer Pattern**: Separates business logic from UI
3. ✅ **Conditional Components**: Questions adapt to entrepreneur data
4. ✅ **Bilingual Architecture**: FR/AR from start
5. ✅ **State Management**: localStorage for persistence
6. ✅ **Responsive Design**: Works on all screen sizes
7. ✅ **Export Capability**: Manual JSON export for data portability
8. ✅ **Future-Ready**: Easy to add backend API for auto-sync

All components work together to provide a seamless, data-driven experience that automatically adapts to each entrepreneur's unique situation.
