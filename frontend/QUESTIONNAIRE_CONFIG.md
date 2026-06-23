# ⚙️ Configuration des Questions - Guide du Développeur

## 📍 Fichier Principal : `src/data/questionnaireService.js`

Ce fichier centralise la configuration de toutes les questions et la logique conditionnelle.

## 🔧 Anatomie d'une Question

```javascript
{
  id: 'unique_id',                    // Identifiant unique
  category: 'category_name',          // Catégorie pour regroupement
  type: 'radio' | 'checkbox' | 'text', // Type d'entrée
  label: { fr: '...', ar: '...' },   // Libellé bilingue
  options: [                          // (Optionnel, requis pour radio/checkbox)
    { 
      value: 'value_key', 
      label: { fr: '...', ar: '...' } 
    }
  ],
  description: { fr: '...', ar: '...' }, // (Optionnel)
  placeholder: { fr: '...', ar: '...' }, // (Optionnel, pour text)
  condition: (data) => boolean        // Fonction de condition
}
```

## 🎯 Logique Conditionnelle

Les questions apparaissent si leur `condition` retourne `true`.

### Exemples de Conditions

```javascript
// Question posée à TOUS les entrepreneurs
condition: (data) => true

// Question spécifique au secteur agri-food
condition: (data) => data.secteur === 'agri-food'

// Question pour ceux en divergence perçu/réel
condition: (data) => data.stade_percu === 'Fundraising' && data.stade_reel !== 'Fundraising'

// Question pour stade de structuration
condition: (data) => data.stade_reel === 'Structuration' || data.stade_reel === 'Ideation'

// Question combinée complexe
condition: (data) => {
  const hasMarketBlocker = data.blockers?.some(b => b.domaine === 'marché');
  return data.secteur === 'agri-food' && hasMarketBlocker;
}
```

## 📝 Ajouter une Nouvelle Question

### Étape 1 : Définir la question dans `allQuestions`

```javascript
const allQuestions = {
  // ... questions existantes
  
  ma_nouvelle_question: {
    id: 'ma_nouvelle_question',
    category: 'sector',
    type: 'radio',
    label: { 
      fr: 'Quel est votre volume de production actuel?',
      ar: 'ما هو حجم الإنتاج الحالي لديك؟'
    },
    options: [
      { value: 'small', label: { fr: 'Petit', ar: 'صغير' } },
      { value: 'medium', label: { fr: 'Moyen', ar: 'متوسط' } },
      { value: 'large', label: { fr: 'Grand', ar: 'كبير' } }
    ],
    condition: (data) => data.secteur === 'agri-food'
  }
};
```

### Étape 2 : Consulter la réponse dans les composants

```javascript
import { getStoredAnswers } from '../data/questionnaireService';

export default function MyComponent({ lang }) {
  const answers = getStoredAnswers();
  const productionVolume = answers.ma_nouvelle_question?.answer;
  
  if (productionVolume === 'large') {
    // Afficher du contenu spécifique
  }
}
```

## 🎨 Catégories Disponibles

| Catégorie | Badge | Couleur | Cas d'usage |
|-----------|-------|--------|------------|
| `legal` | Légal / قانوني | Violet | Questions légales/structure |
| `market` | Marché / السوق | Bleu | Validation marché, clients |
| `sector` | Secteur / القطاع | Cyan | Questions spécifiques au secteur |
| `financing` | Financement / التمويل | Or | Prêtitude au financement |
| `commercial` | Commercial / تجاري | Rose | Modèle économique |
| `timeline` | Chronologie / الجدول | Vert | Délais, planning |

Pour ajouter une nouvelle catégorie, mettre à jour le badge dans `Questionnaire.jsx`.

## 🔄 Flux de Sauvegarde

```
Utilisateur répond → handleAnswer() → saveAnswer(questionId, value)
                                        ↓
                              localStorage.setItem()
                                        ↓
                              Réponse persistée ✓
```

### Structure de localStorage

```javascript
localStorage.questionnaire_answers = {
  "legal_status": {
    "answer": "sarl",
    "timestamp": "2026-06-16T10:30:00.000Z"
  },
  "market_validation": {
    "answer": ["interviews", "prototype_test"],
    "timestamp": "2026-06-16T10:31:00.000Z"
  }
}
```

## 📊 Types de Questions Détaillés

### 1. Radio Buttons (Réponse unique)

```javascript
type: 'radio',
options: [
  { value: 'option1', label: { fr: 'Option 1', ar: 'الخيار 1' } },
  { value: 'option2', label: { fr: 'Option 2', ar: 'الخيار 2' } }
]
```

**Stockage** : `string` (ex: `"option1"`)

### 2. Checkboxes (Réponses multiples)

```javascript
type: 'checkbox',
options: [
  { value: 'check1', label: { fr: 'Vérif 1', ar: 'فحص 1' } },
  { value: 'check2', label: { fr: 'Vérif 2', ar: 'فحص 2' } }
]
```

**Stockage** : `array` (ex: `["check1", "check2"]`)

### 3. Texte Libre

```javascript
type: 'text',
placeholder: { 
  fr: 'Entrez votre réponse...', 
  ar: 'أدخل إجابتك...' 
}
```

**Stockage** : `string`

## 🔗 Intégration avec Dashboard

Pour mettre à jour automatiquement le dashboard selon les réponses :

```javascript
// Dans dataAdapter.js - après charger les réponses
import { getStoredAnswers } from './questionnaireService';

export function getAdaptedData() {
  const answers = getStoredAnswers();
  
  // Enrichir les gaps selon les réponses
  if (answers.legal_status?.answer === 'none') {
    // Ajouter un gap légal
  }
  
  // Mettre à jour les scores
  if (answers.market_validation?.answer?.length === 0) {
    // Réduire le score marché
  }
}
```

## 🚀 Bonnes Pratiques

1. **IDs uniques** : Utiliser des snake_case descriptifs
2. **Conditions claires** : Tester la logique conditionnelle
3. **Traductions** : Toujours remplir FR et AR
4. **Catégories logiques** : Regrouper par domaine
5. **Options mutuelles** : Inclure "Aucun/Autre" quand approprié

## 🐛 Déboguer

### Voir les questions générées
```javascript
// Dans la console du navigateur
const { getApplicableQuestions } = await import('./src/data/questionnaireService.js');
console.log(getApplicableQuestions());
```

### Voir les réponses stockées
```javascript
// Console du navigateur
console.log(JSON.parse(localStorage.questionnaire_answers));
```

### Réinitialiser
```javascript
// Console du navigateur
localStorage.removeItem('questionnaire_answers');
```

## 📦 Export & Persistance

Le bouton "Exporter JSON" génère :
```json
{
  "last_updated": "2026-06-16",
  "responses": [
    {
      "question_id": "legal_status",
      "answer": "sarl",
      "timestamp": "2026-06-16T10:30:00.000Z"
    }
  ]
}
```

Pour **synchroniser avec le backend** :
```javascript
// Ajouter dans Questionnaire.jsx
const handleSync = async () => {
  const answers = exportAnswersForJSON();
  await fetch('/api/questionnaire/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(answers)
  });
};
```

---

**Documentation** ✅ | **Conditionnelles robustes** ✅ | **Bilingue** ✅ | **Extensible** ✅
