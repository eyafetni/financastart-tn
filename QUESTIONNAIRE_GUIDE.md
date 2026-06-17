# 📋 Questionnaire - Guide d'utilisation

## 🎯 Vue d'ensemble

Le module Questionnaire est un formulaire interactif qui pose des questions adaptées à l'entrepreneur en fonction de ses données actuelles (secteur, stade, etc.).

## ✨ Fonctionnalités principales

### 1. **Questions Conditionnelles**
Les questions s'adaptent automatiquement selon :
- **Secteur** : Questions spécifiques à `agri-food`
- **Stade de maturité** : Questions sur la structuration si `stade_reel = "Structuration"`
- **Divergence perçu/réel** : Questions sur le financement si `stade_percu = "Fundraising"` mais `stade_reel ≠ "Fundraising"`

### 2. **Types de Questions**
- **Radio buttons** : Réponse unique (ex: statut légal)
- **Checkboxes** : Réponses multiples (ex: validations effectuées)
- **Texte libre** : Descriptions détaillées

### 3. **Sauvegarde des Réponses**
Les réponses sont stockées dans **localStorage** (navigateur) pour :
- Persistance entre les sessions
- Export en JSON
- Intégration future avec le backend

### 4. **Support Bilingue**
- Interface complète en FR/AR
- RTL automatique pour l'arabe

## 📝 Questions Disponibles

| ID | Question | Conditions | Type |
|---|---|---|---|
| `legal_status` | Statut légal de l'entreprise | Toujours | Radio |
| `market_validation` | Validations client effectuées | Toujours | Checkbox |
| `agri_specifics` | Type de chaîne de valeur (agriculture) | Si secteur = `agri-food` | Radio |
| `funding_readiness` | Prêt pour le financement? | Si divergence perçu/réel **et** stade_percu = Fundraising | Radio |
| `legal_structure_details` | Détails structuration juridique | Si stade_reel = Structuration ou Ideation | Texte |
| `revenue_model` | Modèle de revenu principal | Toujours | Radio |
| `time_to_market` | Délai avant lancement commercial | Toujours | Radio |

## 🔄 Flux Utilisateur

1. **Accès** : Cliquer sur "Questionnaire" dans la navbar
2. **Navigation** : 
   - Bouton "Suivant" pour avancer
   - Bouton "Précédent" pour revenir
   - Bouton "Réinitialiser" pour effacer toutes les réponses
3. **Suivi** : La barre de progression affiche % complété
4. **Completion** : À la fin, écran de résumé avec :
   - Liste de toutes les réponses
   - Bouton "Exporter JSON" pour télécharger
   - Bouton "Revoir" pour modifier les réponses
   - Bouton "Réinitialiser" pour recommencer

## 💾 Sauvegarde des Réponses

### localStorage (côté navigateur)
```javascript
// Structure stockée
localStorage.questionnaire_answers = {
  "legal_status": {
    "answer": "sarl",
    "timestamp": "2026-06-16T10:30:00.000Z"
  },
  "market_validation": {
    "answer": ["interviews", "prototype_test"],
    "timestamp": "2026-06-16T10:31:00.000Z"
  }
  // ... plus de réponses
}
```

### Export JSON
Le bouton "Exporter JSON" génère un fichier au format :
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

## 🔌 Integration avec dashboard.json

La section `answers` dans `dashboard.json` a été ajoutée pour accueillir les réponses :
```json
{
  "answers": {
    "last_updated": "2026-06-16",
    "responses": []
  }
}
```

**Pour synchroniser** les réponses localStorage → dashboard.json, vous pouvez :
1. Créer un endpoint API backend pour recevoir les réponses
2. Implémenter un bouton "Synchroniser" qui envoie les données
3. Ou copier-coller manuellement le JSON exporté

## 🎨 Style & UX

- Thème **sombre** cohérent avec le dashboard
- **Barre de progression** visuelle
- **Badges de catégorie** pour chaque question
- **Indicateurs visuels** pour les réponses saisies
- **Design responsif** (mobile, tablette, desktop)

## 🌍 Support Multilingue

Tous les textes sont bilingues :
- Labels des questions
- Options de réponse
- Boutons et messages

Basculer avec le sélecteur langue 🇫🇷/العربية en haut à droite

## 🚀 Prochaines Étapes (Optional)

1. **Backend API** : POST `/api/save-answers` pour persister les réponses
2. **Analytics** : Tracker les tendances des réponses
3. **Auto-Update Dashboard** : Mettre à jour les gaps/blockers basé sur les réponses
4. **Validation** : Ajouter des règles de validation (champs requis, etc.)
5. **Recommandations** : Générer des suggestions basées sur les réponses

## 📱 Tests en Local

1. **Accéder au questionnaire** : http://localhost:5173/questionnaire
2. **Répondre aux questions** : Les réponses se sauvegardent automatiquement
3. **Exporter** : Télécharger le JSON à la fin
4. **DevTools** : Ouvrir F12 → Application → localStorage pour voir `questionnaire_answers`

---

**Support bilingue FR/AR** ✅ | **Responsive Design** ✅ | **localStorage Persistence** ✅ | **Export JSON** ✅
