# Système de Thème Clair/Sombre - Documentation

## Vue d'ensemble

Le système de thème permet aux utilisateurs de basculer entre les modes clair, sombre et système (auto-détection). Il utilise des variables CSS personnalisées et respecte les préférences utilisateur avec des transitions fluides.

## Architecture

### Variables CSS
Toutes les couleurs sont définies via des variables CSS dans `src/styles/premium-theme.css` :

```css
:root {
  /* Mode sombre par défaut */
  --background: #000000;
  --card: rgba(0, 41, 107, 0.15);
  --text: #ffffff;
  --accent: #fdc500;
  /* ... */
}

:root.light {
  /* Mode clair */
  --background: #f8fafc;
  --card: rgba(255, 255, 255, 0.9);
  --text: #1e293b;
  --accent: #00296b;
  /* ... */
}
```

### Hook useTheme
Le hook `src/hooks/useTheme.ts` gère l'état du thème :

```typescript
const { theme, resolvedTheme, setTheme, toggleTheme, mounted } = useTheme();
```

- `theme`: 'light' | 'dark' | 'system'
- `resolvedTheme`: 'light' | 'dark' (thème effectif)
- `setTheme`: Fonction pour changer le thème
- `toggleTheme`: Cycle entre les 3 modes
- `mounted`: Évite l'hydration mismatch

## Composants

### ThemeToggle
Bouton de basculement de thème avec icônes et tooltip :
- Position fixe en haut à droite
- Icônes adaptées au mode actuel
- Tooltip informatif
- Transitions fluides

### StarConstellation
Arrière-plan animé adaptatif :
- Étoiles dorées en mode sombre
- Étoiles bleues en mode clair
- Réactivité aux changements de thème

## Palette de Couleurs

### Mode Sombre (Premium)
- **Arrière-plan** : Noir profond (#000000)
- **Cartes** : Bleu royal transparent
- **Texte** : Blanc (#ffffff)
- **Accent** : Jaune Mikado (#fdc500)
- **Bordures** : Bleu polynésien transparent

### Mode Clair (Élégant)
- **Arrière-plan** : Gris clair (#f8fafc)
- **Cartes** : Blanc transparent
- **Texte** : Ardoise foncé (#1e293b)
- **Accent** : Bleu royal (#00296b)
- **Bordures** : Bleu royal transparent

## Utilisation

### Classes CSS Recommandées
```tsx
// Utiliser les classes premium qui s'adaptent automatiquement
<div className="premium-card">
  <h2 className="premium-section-title">Titre</h2>
  <p className="premium-text">Contenu</p>
</div>
```

### Classes Tailwind Thématiques
```tsx
// Utiliser les couleurs thématiques
<div className="bg-theme-background text-theme-text border-theme-border">
  <span className="text-theme-accent">Accent</span>
</div>
```

### Hook dans les Composants
```tsx
import { useTheme } from '@/hooks/useTheme';

const MyComponent = () => {
  const { resolvedTheme, toggleTheme } = useTheme();
  
  return (
    <div className={`component ${resolvedTheme === 'dark' ? 'dark-specific' : 'light-specific'}`}>
      <button onClick={toggleTheme}>Changer le thème</button>
    </div>
  );
};
```

## Fonctionnalités

### Persistance
- Sauvegarde automatique dans localStorage
- Restauration au rechargement de page
- Mode système par défaut

### Détection Système
- Respect de `prefers-color-scheme`
- Mise à jour automatique si l'utilisateur change ses préférences système
- Fallback gracieux

### Transitions
- Transitions fluides de 0.3s sur tous les éléments
- Animations préservées entre les thèmes
- Performance optimisée

### Accessibilité
- Contrastes respectés dans les deux modes
- Focus visible adapté au thème
- Support des préférences utilisateur

## Structure des Fichiers

```
src/
├── hooks/
│   └── useTheme.ts              # Hook de gestion du thème
├── components/ui/
│   ├── ThemeToggle.tsx          # Bouton de basculement
│   └── StarConstellation.tsx    # Arrière-plan adaptatif
├── styles/
│   └── premium-theme.css        # Variables et styles thématiques
├── app/
│   ├── globals.css              # Styles globaux avec transitions
│   └── layout.tsx               # Layout avec ThemeToggle
└── tailwind.config.js           # Configuration Tailwind étendue
```

## Configuration Tailwind

Les couleurs thématiques sont disponibles via :

```javascript
theme: {
  extend: {
    colors: {
      theme: {
        background: 'var(--background)',
        text: 'var(--text)',
        accent: 'var(--accent)',
        // ...
      }
    }
  }
}
```

## Bonnes Pratiques

### 1. Utiliser les Variables CSS
```css
/* ✅ Bon */
.my-component {
  background: var(--card);
  color: var(--text);
}

/* ❌ Éviter */
.my-component {
  background: #ffffff;
  color: #000000;
}
```

### 2. Classes Premium
```tsx
{/* ✅ Bon - S'adapte automatiquement */}
<div className="premium-card premium-text">

{/* ❌ Éviter - Couleurs fixes */}
<div className="bg-white text-black">
```

### 3. Conditions Thématiques
```tsx
// ✅ Bon - Utiliser le hook
const { resolvedTheme } = useTheme();
const iconColor = resolvedTheme === 'dark' ? 'gold' : 'blue';

// ❌ Éviter - Détection manuelle
const isDark = document.documentElement.classList.contains('dark');
```

## Performance

### Optimisations
- Variables CSS natives (pas de re-render React)
- Transitions hardware-accelerated
- Lazy loading du thème initial
- Debouncing des changements système

### Métriques
- Temps de basculement : < 300ms
- Impact bundle : +2KB gzippé
- Compatibilité : Tous navigateurs modernes

## Maintenance

### Ajouter une Nouvelle Couleur
1. Définir dans `:root` et `:root.light`
2. Ajouter à Tailwind config si nécessaire
3. Créer une classe premium si réutilisable
4. Tester dans les deux modes

### Déboguer les Thèmes
```javascript
// Console browser
console.log('Thème actuel:', document.documentElement.className);
console.log('Variables CSS:', getComputedStyle(document.documentElement));
```

Ce système garantit une expérience utilisateur cohérente et accessible avec des transitions fluides entre les modes clair et sombre.