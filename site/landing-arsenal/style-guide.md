# Arsenal Landing — Style Guide

## Цветовая палитра

### Основные цвета
```css
--bg-primary: #1a1a2e;      /* Тёмный фон */
--bg-secondary: #16213e;    /* Карточки */
--text-primary: #eee;       /* Основной текст */
--text-secondary: #bbb;     /* Вторичный текст */
--text-muted: #888;         /* Приглушённый текст */
--border: #333;             /* Границы */
```

### Акцентные цвета
```css
--accent: #4ecdc4;          /* Основной акцент (бирюзовый) */
--accent-dark: #45b7aa;     /* Тёмный вариант акцента */
--warning: #ff6b6b;         /* Предупреждение/Атака (красный) */
--yellow: #f9ca24;          /* Жёлтый акцент */
--purple: #a29bfe;          /* Фиолетовый акцент */
--purple-dark: #6c5ce7;     /* Тёмный фиолетовый */
```

## Типография

### Шрифты
```css
/* Основной шрифт */
font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;

/* Заголовок (логотип) */
font-family: 'Orbitron', sans-serif;
```

### Размеры заголовков
```css
h1 { font-size: 52px; font-weight: 300; }
h2 { font-size: 40px; font-weight: 300; }
h3 { font-size: 28px; font-weight: 400; }

/* Intro слайд */
.intro-slide h1 {
    font-size: 80px;
    font-weight: 700;
    letter-spacing: 8px;
    text-transform: uppercase;
}

/* Подзаголовок */
.subtitle { font-size: 28px; color: #888; }
```

## Структура слайдов

### Базовый слайд
```css
.slide {
    min-height: 100vh;
    max-width: 1180px;
    margin: 0 auto;
    padding: 60px 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-bottom: 1px solid #333;
}
```

### Нумерация слайдов
```css
.slide-number {
    position: absolute;
    top: 30px;
    right: 40px;
    font-size: 16px;
    color: #666;
}
```

## Компоненты

### Карточка (Card)
```css
.card {
    background: #16213e;
    border-radius: 12px;
    padding: 25px;
    border-left: 4px solid #4ecdc4;
}

/* Варианты */
.card.warning-card { border-left-color: #ff6b6b; }
.card.yellow-card { border-left-color: #f9ca24; }
.card.purple-card { border-left-color: #a29bfe; }
```

### Stat Box (Статистика)
```css
.stat-box {
    text-align: center;
    padding: 30px 15px;
    background: #16213e;
    border-radius: 12px;
}

.stat-box .number {
    font-size: 48px;
    font-weight: 700;
    color: #4ecdc4;
}

.stat-box .label {
    font-size: 16px;
    color: #888;
    margin-top: 8px;
}
```

### Теги (Tags)
```css
.tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 16px;
}

.tag-green { background: rgba(78, 205, 196, 0.2); color: #4ecdc4; }
.tag-red { background: rgba(255, 107, 107, 0.2); color: #ff6b6b; }
.tag-yellow { background: rgba(249, 202, 36, 0.2); color: #f9ca24; }
```

### Tooltip
```css
.tooltip {
    cursor: help;
    border-bottom: 1px dotted #4ecdc4;
    color: #4ecdc4;
}

.tooltip::after {
    content: attr(data-tip);
    position: absolute;
    bottom: 100%;
    background: #0f0f23;
    padding: 12px 16px;
    border-radius: 8px;
    width: 320px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    border: 1px solid #333;
}
```

### Pricing Card
```css
.pricing-card {
    background: #16213e;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    border: 2px solid #333;
}

.pricing-card.featured {
    border-color: #4ecdc4;
    transform: scale(1.02);
}

.pricing-card .price {
    font-size: 54px;
    font-weight: 700;
}
```

## Сетки (Grids)

```css
.grid-2 { grid-template-columns: 1fr 1fr; gap: 40px; }
.grid-3 { grid-template-columns: 1fr 1fr 1fr; gap: 30px; }
.grid-4 { grid-template-columns: repeat(4, 1fr); gap: 25px; }
```

## Эффекты

### Aurora Borealis (Северное сияние)
```css
.aurora {
    position: fixed;
    inset: 0;
    overflow: hidden;
    z-index: 0;
    pointer-events: none;
}

.aurora::before {
    opacity: 0.25;
    background-image:
        repeating-linear-gradient(100deg,
            #1a1a2e 0%, #1a1a2e 5%,
            transparent 8%, transparent 10%,
            #1a1a2e 18%, #1a1a2e 22%,
            transparent 24%, transparent 25%,
            #1a1a2e 35%
        ),
        repeating-linear-gradient(100deg,
            #4ecdc4 8%, #45b7aa 12%,
            #a29bfe 22%, #6c5ce7 28%,
            transparent 32%, #4ecdc4 45%
        );
    filter: blur(30px);
    animation: aurora 90s linear infinite;
}

@keyframes aurora {
    from { background-position: 50% 50%, 50% 50%; }
    to { background-position: 350% 50%, 350% 50%; }
}
```

### Shooting Stars (Падающие звёзды)
```css
.shooting-star {
    height: 2px;
    background: linear-gradient(to right,
        transparent,
        rgba(255, 107, 107, 0.4),
        rgba(255, 107, 107, 0.8),
        #fff
    );
    animation: shoot-star linear infinite;
}

@keyframes shoot-star {
    0% { transform: translateX(0); opacity: 1; }
    70% { opacity: 1; }
    100% { transform: translateX(350px); opacity: 0; }
}
```

### Анимация появления
```css
.animate-on-scroll {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s ease, transform 0.5s ease;
}

.animate-on-scroll.visible {
    opacity: 1;
    transform: translateY(0);
}

/* Каскадная задержка */
.grid-4 .animate-on-scroll:nth-child(1) { transition-delay: 0s; }
.grid-4 .animate-on-scroll:nth-child(2) { transition-delay: 0.1s; }
.grid-4 .animate-on-scroll:nth-child(3) { transition-delay: 0.2s; }
.grid-4 .animate-on-scroll:nth-child(4) { transition-delay: 0.3s; }
```

## JavaScript

### Навигация по слайдам
```javascript
// Определение текущего слайда
function updateActiveNav() {
    slides.forEach(slide => {
        const rect = slide.getBoundingClientRect();
        if (rect.top <= window.innerHeight / 2 &&
            rect.bottom >= window.innerHeight / 2) {
            current = slide.id;
        }
    });
}
```

### Клавиатурная навигация
```javascript
document.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
        navigateSlide(1);
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
        navigateSlide(-1);
    }
});
```

### Intersection Observer для анимаций
```javascript
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.card, .stat-box').forEach(el => {
    el.classList.add('animate-on-scroll');
    observer.observe(el);
});
```

## Принципы дизайна

1. **Тёмная тема** — фон `#1a1a2e`, комфортный для глаз
2. **Цветовое кодирование** — красный для атаки, бирюзовый для защиты, фиолетовый для аналитики
3. **Левая граница карточек** — визуальный якорь и цветовая маркировка
4. **Tooltips** — дополнительная информация без перегрузки интерфейса
5. **Полноэкранные слайды** — фокус на одной идее за раз
6. **Каскадные анимации** — элементы появляются последовательно
7. **Навигация клавиатурой** — стрелки для перемещения между слайдами
8. **Responsive** — адаптация сеток под мобильные устройства

## Responsive Breakpoints

```css
@media (max-width: 1024px) {
    .slide-nav { display: none; }
    h1 { font-size: 36px; }
    .grid-2 { grid-template-columns: 1fr; }
    .grid-3, .grid-4 { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 640px) {
    h1 { font-size: 28px; }
    .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
}
```
