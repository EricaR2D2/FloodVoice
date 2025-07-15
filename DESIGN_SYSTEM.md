# 🎨 NYC Public Health MVP - Visual Design System

## Executive Summary
This document defines the complete visual design system for the NYC Public Health MVP, ensuring consistent, professional presentation across all components and templates.

## 🎯 Design Principles
- **Professional Healthcare Aesthetic**: Clean, trustworthy, and accessible
- **Consistent User Experience**: Uniform interactions and visual patterns
- **Real-time Data Focus**: Clear hierarchy for live surveillance data
- **Accessibility First**: High contrast ratios and readable typography

---

## 🎨 Color Palette

### Primary Colors
```css
--primary-color: #667eea;     /* Professional blue-purple */
--primary-dark: #5a6fd8;      /* Darker variant for hover states */
--secondary-color: #764ba2;   /* Complementary purple */
--secondary-dark: #6a4190;    /* Darker variant for hover states */
```

### Status Colors (Bootstrap Standard)
```css
--success-color: #28a745;     /* Green for positive states */
--info-color: #17a2b8;        /* Cyan for informational states */
--warning-color: #ffc107;     /* Yellow for warning states */
--danger-color: #dc3545;      /* Red for error/alert states */
```

### Neutral Colors
```css
--white: #ffffff;
--black: #000000;
--light-color: #f8f9fa;
--dark-color: #343a40;
--gray-100: #f8f9fa;
--gray-200: #e9ecef;
--gray-300: #dee2e6;
--gray-400: #ced4da;
--gray-500: #adb5bd;
--gray-600: #6c757d;
--gray-700: #495057;
--gray-800: #343a40;
--gray-900: #212529;
```

### Usage Guidelines
- **Primary Gradient**: Used for main CTAs, navigation, and key UI elements
- **Status Colors**: Used for alerts, badges, and state indicators
- **Gray Scale**: Used for text hierarchy and subtle UI elements

---

## ✍️ Typography System

### Font Stack
```css
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
```

### Base Typography
```css
body {
    font-size: 14px;
    line-height: 1.5;
}
```

### Heading Hierarchy
```css
h1, .h1 { font-size: 2.25rem; margin-bottom: 1rem; }      /* 36px */
h2, .h2 { font-size: 1.875rem; margin-bottom: 0.875rem; } /* 30px */
h3, .h3 { font-size: 1.5rem; margin-bottom: 0.75rem; }    /* 24px */
h4, .h4 { font-size: 1.25rem; margin-bottom: 0.625rem; }  /* 20px */
h5, .h5 { font-size: 1.125rem; margin-bottom: 0.5rem; }   /* 18px */
h6, .h6 { font-size: 1rem; margin-bottom: 0.5rem; }       /* 16px */
```

### Specialized Typography
```css
.page-title { font-size: 2rem; font-weight: 600; }
.page-subtitle { font-size: 1rem; font-weight: 400; }
.section-title { font-size: 1.5rem; font-weight: 600; }
.subsection-title { font-size: 1.25rem; font-weight: 600; }
.card-title { font-size: 1.125rem; font-weight: 600; }
.card-subtitle { font-size: 0.875rem; }
.lead { font-size: 1.25rem; font-weight: 300; line-height: 1.6; }
.small, small { font-size: 0.875rem; }
```

### Font Weights
- **300**: Light (display headings)
- **400**: Regular (body text)
- **500**: Medium (buttons, labels, links)
- **600**: Semi-bold (headings, card titles)

---

## 📏 Spacing System

### Spacing Scale
```css
.section-spacing { margin-bottom: 2rem; }      /* 32px - Between major sections */
.card-spacing { margin-bottom: 1.5rem; }       /* 24px - Between cards */
.content-padding { padding: 1.5rem; }          /* 24px - Standard content padding */
.header-spacing {                               /* Standard header spacing */
    padding-top: 1rem;
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
}
```

### Component Spacing
```css
/* Cards */
.card-header { padding: 1rem 1.5rem; }
.card-body { padding: 1.5rem; }

/* Forms */
.form-group, .mb-3 { margin-bottom: 1rem; }
.form-label { margin-bottom: 0.5rem; }

/* Navigation */
.sidebar .nav-link { padding: 0.75rem 1rem; margin: 0.25rem 0; }

/* Tables */
.table td, .table th { padding: 0.75rem; }

/* Buttons */
.btn-toolbar .btn-group { margin-right: 0.5rem; }
```

---

## 🔘 Button System

### Base Button Styling
```css
.btn {
    font-weight: 500;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    transition: all 0.3s ease;
}
```

### Button Sizes
```css
.btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: 0.8125rem;
    border-radius: 6px;
}

.btn-lg {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    border-radius: 10px;
}
```

### Button Variants
```css
.btn-primary {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    border: none;
    color: var(--white);
}

.btn-primary:hover {
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary-dark) 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-outline-primary {
    border: 2px solid var(--primary-color);
    color: var(--primary-color);
    background: transparent;
}
```

### Interactive States
```css
.btn:focus { box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25); }
.btn:active { transform: translateY(1px); }
```

---

## 🃏 Card System

### Base Card Styling
```css
.card {
    border: none;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    background-color: var(--white);
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}
```

### Card Components
```css
.card-header {
    padding: 1rem 1.5rem;
    font-weight: 600;
    border-bottom: 1px solid var(--gray-200);
    background-color: var(--gray-100);
}

.card-body {
    padding: 1.5rem;
}

.card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--gray-800);
    margin-bottom: 0.5rem;
}

.card-subtitle {
    font-size: 0.875rem;
    color: var(--gray-600);
    margin-bottom: 0.75rem;
}

.card-text {
    color: var(--gray-700);
    line-height: 1.6;
}
```

---

## 📝 Form System

### Form Controls
```css
.form-control, .form-select {
    border-radius: 8px;
    border: 2px solid var(--gray-200);
    font-size: 0.875rem;
    transition: all 0.3s ease;
}

.form-control:focus, .form-select:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}
```

### Form Labels
```css
.form-label {
    margin-bottom: 0.5rem;
    font-weight: 500;
}
```

### Form Spacing
```css
.form-group, .mb-3 {
    margin-bottom: 1rem;
}
```

---

## 🏷️ Badge & Alert System

### Badges
```css
.badge {
    font-weight: 500;
    border-radius: 6px;
}
```

### Alerts
```css
.alert {
    border-radius: 8px;
    border: none;
    font-weight: 500;
}

.alert-item {
    border-left: 4px solid;
    margin-bottom: 1rem;
    padding: 1rem;
    border-radius: 0 8px 8px 0;
}
```

### Pattern-Specific Alerts
```css
.alert-spike { 
    border-left-color: var(--danger-color); 
    background-color: rgba(220, 53, 69, 0.1); 
}
.alert-drop { 
    border-left-color: var(--info-color); 
    background-color: rgba(23, 162, 184, 0.1); 
}
.alert-high { 
    border-left-color: var(--warning-color); 
    background-color: rgba(255, 193, 7, 0.1); 
}
```

---

## 🧭 Navigation System

### Sidebar Navigation
```css
.sidebar {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
}

.sidebar .nav-link {
    color: rgba(255,255,255,0.8);
    padding: 0.75rem 1rem;
    margin: 0.25rem 0;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.sidebar .nav-link:hover, .sidebar .nav-link.active {
    color: var(--white);
    background-color: rgba(255,255,255,0.15);
    transform: translateX(5px);
}
```

---

## 📊 Data Visualization Colors

### Illness Type Colors (Advanced Dashboard)
```css
COVID-19: #FF6B6B
Flu Surveillance: #4ECDC4
Foodborne Illness: #45B7D1
Air Quality: #96CEB4
Hospital ER: #DDA0DD
Tick Disease: #FFEAA7
```

### Risk Level Colors
```css
Low Risk: #2ECC71
Medium Risk: #F39C12
High Risk: #E74C3C
Hazardous: #8E44AD
```

---

## 🎭 Animation & Transitions

### Standard Transitions
```css
transition: all 0.3s ease;
```

### Hover Effects
```css
/* Cards */
transform: translateY(-2px);
box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);

/* Buttons */
transform: translateY(-1px);
box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);

/* Navigation */
transform: translateX(5px);
```

### Focus States
```css
box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
```

### Active States
```css
transform: translateY(1px);
```

---

## 📱 Responsive Considerations

### Breakpoints (Bootstrap Standard)
- **xs**: <576px
- **sm**: ≥576px
- **md**: ≥768px
- **lg**: ≥992px
- **xl**: ≥1200px

### Mobile Adaptations
- Sidebar collapses to full-width on mobile
- Card spacing reduces on smaller screens
- Button sizes adjust appropriately
- Typography scales down for mobile readability

---

## ✅ Implementation Checklist

### For New Components:
- [ ] Use CSS custom properties for colors
- [ ] Apply consistent border-radius values
- [ ] Include proper hover/focus states
- [ ] Use standard spacing scale
- [ ] Follow typography hierarchy
- [ ] Include smooth transitions
- [ ] Test on all screen sizes

### For Existing Components:
- [ ] Verify color consistency
- [ ] Check spacing alignment
- [ ] Ensure interactive states work
- [ ] Validate accessibility contrast
- [ ] Test responsive behavior

---

## 🔧 Maintenance Guidelines

1. **Always use CSS custom properties** instead of hardcoded colors
2. **Follow the spacing scale** for consistent layouts
3. **Use standard border-radius values** (6px, 8px, 12px)
4. **Include hover/focus states** for all interactive elements
5. **Test on multiple screen sizes** before deployment
6. **Maintain consistent animation timing** (0.3s ease)

---

*Last Updated: July 14, 2025*
*Version: 1.0*
