"""
Script Python pour optimiser une page HTML pour mobile avec détection de plateforme
Transforme automatiquement le HTML pour une meilleure expérience mobile
"""

from bs4 import BeautifulSoup
import re
from pathlib import Path
from typing import Optional, Literal


class MobileHTMLOptimizer:
    """Optimise les pages HTML pour les écrans de smartphones avec détection de plateforme."""
    
    def __init__(self, html_content: str, target_platform: Literal['auto', 'mobile', 'desktop'] = 'auto'):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.target_platform = target_platform
        self.is_mobile = self._detect_platform()
        self.mobile_styles = self._get_mobile_styles()
    
    def _detect_platform(self) -> bool:
        """Détecte si on doit optimiser pour mobile."""
        if self.target_platform == 'mobile':
            return True
        elif self.target_platform == 'desktop':
            return False
        
        # Mode auto: injecter du JavaScript pour détection
        return True  # Par défaut, on optimise pour mobile
    
    def _get_mobile_styles(self) -> str:
        """Génère les styles CSS adaptatifs pour mobile."""
        return """
/* ========================================
   RESPONSIVE STYLES - ADAPTIVE TO SCREEN SIZE
   ======================================== */

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
    font-size: 16px;
}

/* ========================================
   1) IMAGES & LOGOS - PROPORTIONAL SIZING
   ======================================== */
   
img, .logo, [class*="logo"], [id*="logo"] {
    max-width: 100% !important;
    height: auto !important;
    width: auto !important;
    display: block;
    object-fit: contain;
}

/* Logos spécifiques - taille réduite sur mobile */
@media (max-width: 768px) {
    img[src*="logo"], 
    img[src*="icon"],
    .logo,
    [class*="logo"] {
        max-width: 60vw !important;
        max-height: 15vh !important;
    }
    
    /* Images dans le contenu */
    img:not([src*="logo"]):not([src*="icon"]) {
        max-width: 100vw !important;
        width: 100% !important;
        height: auto !important;
        margin: 0.5rem 0;
    }
}

@media (min-width: 769px) {
    img[src*="logo"], 
    img[src*="icon"],
    .logo {
        max-width: 200px !important;
    }
}

/* ========================================
   2) PLATFORM DETECTION & ADAPTATION
   ======================================== */

/* Desktop-only elements */
@media (max-width: 768px) {
    .desktop-only,
    .hide-mobile,
    [class*="desktop-only"] {
        display: none !important;
    }
}

/* Mobile-only elements */
@media (min-width: 769px) {
    .mobile-only,
    .hide-desktop,
    [class*="mobile-only"] {
        display: none !important;
    }
}

/* ========================================
   3) MOBILE NAVIGATION MENU
   ======================================== */

nav {
    width: 100%;
    position: relative;
}

/* Mobile menu button */
.mobile-menu-toggle {
    display: none;
    background: #2563eb;
    color: white;
    border: none;
    padding: 1rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    text-align: left;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
}

@media (max-width: 768px) {
    .mobile-menu-toggle {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .mobile-menu-toggle::after {
        content: '▼';
        transition: transform 0.3s;
    }
    
    .mobile-menu-toggle.active::after {
        transform: rotate(180deg);
    }
    
    nav ul, nav ol {
        list-style: none;
        padding: 0;
        margin: 0;
        display: none;
        flex-direction: column;
        gap: 0;
    }
    
    nav ul.show, nav ol.show {
        display: flex;
    }
    
    nav li {
        display: block;
        width: 100%;
        border-bottom: 1px solid #e5e7eb;
    }
    
    nav li:last-child {
        border-bottom: none;
    }
    
    nav a {
        display: block;
        padding: 1rem 1.5rem !important;
        text-decoration: none;
        color: #1f2937;
        font-size: 1rem !important;
        min-height: 44px;
        transition: background-color 0.2s;
    }
    
    nav a:hover, nav a:active {
        background-color: #f3f4f6;
    }
}

@media (min-width: 769px) {
    nav ul, nav ol {
        display: flex !important;
        flex-direction: row;
        gap: 1rem;
    }
    
    nav a {
        padding: 0.5rem 1rem;
    }
}

/* ========================================
   4) READ MORE BUTTONS - MOBILE OPTIMIZED
   ======================================== */

button, 
a[class*="read"], 
a[class*="more"],
a[class*="button"],
.btn,
[class*="btn-"],
input[type="submit"],
input[type="button"] {
    min-height: 44px !important;
    min-width: 44px !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 1rem !important;
    cursor: pointer;
    border-radius: 0.5rem;
    border: none;
    background: #2563eb;
    color: white;
    text-decoration: none;
    display: inline-block;
    text-align: center;
    transition: all 0.2s;
    -webkit-tap-highlight-color: rgba(0,0,0,0.1);
}

button:hover,
a[class*="button"]:hover,
.btn:hover {
    background: #1d4ed8;
    transform: translateY(-1px);
}

button:active,
a[class*="button"]:active,
.btn:active {
    transform: translateY(0);
}

@media (max-width: 768px) {
    button, 
    a[class*="read"], 
    a[class*="more"],
    a[class*="button"],
    .btn {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0.5rem 0 !important;
        font-size: 1.1rem !important;
        padding: 1rem 1.5rem !important;
    }
}

/* ========================================
   5) FONT SIZES - REDUCED & UNIFIED
   ======================================== */

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Mobile font sizes - reduced and unified */
@media (max-width: 768px) {
    body {
        font-size: 0.9rem !important;
    }
    
    h1 {
        font-size: 1.5rem !important;
        line-height: 1.3;
        margin: 0.5rem 0 !important;
    }
    
    h2 {
        font-size: 1.25rem !important;
        line-height: 1.3;
        margin: 0.5rem 0 !important;
    }
    
    h3 {
        font-size: 1.1rem !important;
        line-height: 1.3;
        margin: 0.4rem 0 !important;
    }
    
    h4, h5, h6 {
        font-size: 1rem !important;
        line-height: 1.3;
        margin: 0.4rem 0 !important;
    }
    
    p, li, td, th {
        font-size: 0.9rem !important;
        line-height: 1.5;
    }
    
    small, .small {
        font-size: 0.8rem !important;
    }
}

/* Desktop font sizes */
@media (min-width: 769px) {
    body {
        font-size: 1rem;
    }
    
    h1 { font-size: 2rem; margin: 1rem 0; }
    h2 { font-size: 1.5rem; margin: 0.875rem 0; }
    h3 { font-size: 1.25rem; margin: 0.75rem 0; }
    h4 { font-size: 1.125rem; margin: 0.625rem 0; }
    h5 { font-size: 1rem; margin: 0.5rem 0; }
    h6 { font-size: 0.875rem; margin: 0.5rem 0; }
}

/* ========================================
   6) SPACING - PROPORTIONAL TO SCREEN
   ======================================== */

/* Mobile spacing - reduced */
@media (max-width: 768px) {
    body {
        margin: 0 !important;
        padding: 0.5rem !important;
    }
    
    .container, 
    .content, 
    main, 
    article,
    section,
    div[class*="container"],
    div[class*="wrapper"] {
        padding: 0.5rem !important;
        margin: 0.25rem 0 !important;
    }
    
    p {
        margin: 0.5rem 0 !important;
    }
    
    ul, ol {
        padding-left: 1rem !important;
        margin: 0.5rem 0 !important;
    }
    
    li {
        margin: 0.25rem 0 !important;
    }
    
    table {
        margin: 0.5rem 0 !important;
    }
    
    th, td {
        padding: 0.5rem !important;
    }
    
    /* Sections spacing */
    section, article {
        margin-bottom: 1rem !important;
        padding: 0.75rem !important;
    }
    
    /* Header/Footer reduced spacing */
    header, footer {
        padding: 0.75rem !important;
        margin: 0.5rem 0 !important;
    }
}

/* Tablet spacing */
@media (min-width: 769px) and (max-width: 1024px) {
    body {
        padding: 1rem;
    }
    
    .container, main, article, section {
        padding: 1rem;
        margin: 0.75rem 0;
    }
}

/* Desktop spacing */
@media (min-width: 1025px) {
    body {
        padding: 1.5rem;
    }
    
    .container, main, article, section {
        padding: 1.5rem;
        margin: 1rem 0;
    }
}

/* ========================================
   ADDITIONAL OPTIMIZATIONS
   ======================================== */

/* Responsive tables */
table {
    width: 100%;
    overflow-x: auto;
    display: block;
    border-collapse: collapse;
}

@media (max-width: 768px) {
    table {
        font-size: 0.85rem !important;
    }
    
    .table-wrapper {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin: 0.5rem 0;
    }
}

/* Forms optimization */
input, select, textarea {
    width: 100%;
    max-width: 100%;
    padding: 0.75rem;
    font-size: 1rem !important;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    margin-bottom: 0.75rem;
}

@media (max-width: 768px) {
    input, select, textarea {
        padding: 0.875rem;
        font-size: 1rem !important;
    }
}

/* Flexbox & Grid layouts */
.flex-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

@media (min-width: 769px) {
    .flex-container {
        flex-direction: row;
        gap: 1rem;
    }
}

/* Videos responsive */
iframe, video {
    max-width: 100% !important;
    height: auto !important;
}

/* Touch-friendly */
* {
    -webkit-tap-highlight-color: rgba(0,0,0,0.05);
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* Print styles */
@media print {
    .mobile-menu-toggle,
    nav,
    button {
        display: none !important;
    }
}
"""
    
    def add_viewport_meta(self):
        """Ajoute ou met à jour la balise viewport."""
        head = self.soup.find('head')
        if not head:
            head = self.soup.new_tag('head')
            if self.soup.html:
                self.soup.html.insert(0, head)
            else:
                self.soup.insert(0, head)
        
        # Supprimer ancien viewport
        old_viewport = head.find('meta', attrs={'name': 'viewport'})
        if old_viewport:
            old_viewport.decompose()
        
        # Ajouter nouveau viewport
        viewport = self.soup.new_tag(
            'meta',
            attrs={
                'name': 'viewport',
                'content': 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes'
            }
        )
        head.insert(0, viewport)
        
        # Ajouter charset si absent
        if not head.find('meta', attrs={'charset': True}):
            charset = self.soup.new_tag('meta', attrs={'charset': 'UTF-8'})
            head.insert(0, charset)
    
    def add_mobile_styles(self):
        """Ajoute les styles CSS pour mobile."""
        head = self.soup.find('head')
        if not head:
            return
        
        style_tag = self.soup.new_tag('style', id='mobile-optimization-styles')
        style_tag.string = self.mobile_styles
        head.append(style_tag)
    
    def optimize_images_and_logos(self):
        """1) Optimise images et logos proportionnellement à la taille d'écran."""
        for img in self.soup.find_all('img'):
            # Lazy loading
            img['loading'] = 'lazy'
            
            # Alt text
            if not img.get('alt'):
                src = img.get('src', '')
                img['alt'] = src.split('/')[-1].split('.')[0] or 'Image'
            
            # Supprimer largeurs/hauteurs fixes
            for attr in ['width', 'height']:
                if img.get(attr):
                    del img[attr]
            
            # Classes pour logos
            src = img.get('src', '').lower()
            if 'logo' in src or 'icon' in src:
                current_class = img.get('class', [])
                if isinstance(current_class, str):
                    current_class = [current_class]
                current_class.append('logo')
                img['class'] = current_class
    
    def add_platform_detection(self):
        """2) Ajoute la détection de plateforme dynamique."""
        if not self.is_mobile:
            return  # Ne rien faire si desktop
        
        head = self.soup.find('head')
        if not head:
            return
        
        # Script de détection
        detection_script = self.soup.new_tag('script')
        detection_script.string = """
(function() {
    // Détection de plateforme
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
                     || window.innerWidth <= 768;
    
    // Ajouter classe au body
    document.addEventListener('DOMContentLoaded', function() {
        document.body.classList.add(isMobile ? 'mobile-platform' : 'desktop-platform');
        
        // Logger pour debug
        console.log('Platform detected:', isMobile ? 'Mobile' : 'Desktop');
    });
})();
"""
        head.append(detection_script)
    
    def optimize_mobile_menu(self):
        """3) Adapte le menu pour mobile avec hamburger fonctionnel."""
        nav = self.soup.find('nav')
        if not nav:
            return
        
        # Créer bouton hamburger
        toggle_btn = self.soup.new_tag('button', attrs={
            'class': 'mobile-menu-toggle',
            'aria-label': 'Toggle navigation menu',
            'aria-expanded': 'false'
        })
        toggle_btn.string = '☰ Menu'
        
        # Trouver la liste du menu
        menu_list = nav.find(['ul', 'ol'])
        if menu_list:
            menu_list['class'] = menu_list.get('class', []) + ['mobile-menu']
            menu_list['id'] = 'main-navigation-menu'
            
            # Insérer le bouton avant la liste
            menu_list.insert_before(toggle_btn)
        
        # Script pour toggle
        script = self.soup.new_tag('script')
        script.string = """
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.querySelector('.mobile-menu-toggle');
    const menu = document.querySelector('.mobile-menu');
    
    if (toggleBtn && menu) {
        toggleBtn.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
            this.classList.toggle('active');
            menu.classList.toggle('show');
        });
    }
});
"""
        self.soup.body.append(script)
    
    def optimize_read_more_buttons(self):
        """4) Optimise les boutons 'read more' pour mobile."""
        # Patterns de recherche pour boutons
        button_patterns = ['read', 'more', 'voir', 'lire', 'button', 'btn']
        
        for tag in self.soup.find_all(['a', 'button']):
            # Vérifier si c'est un bouton "read more"
            text = tag.get_text().lower()
            classes = ' '.join(tag.get('class', [])).lower()
            
            is_button = any(pattern in text or pattern in classes for pattern in button_patterns)
            
            if is_button:
                # Ajouter classe button
                current_class = tag.get('class', [])
                if isinstance(current_class, str):
                    current_class = [current_class]
                current_class.append('btn-mobile-optimized')
                tag['class'] = current_class
    
    def unify_and_reduce_fonts(self):
        """5) Réduit et uniformise les tailles de police."""
        # Les styles CSS gèrent déjà cela, mais on peut ajouter des classes
        for tag in self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
            current_class = tag.get('class', [])
            if isinstance(current_class, str):
                current_class = [current_class]
            current_class.append('unified-typography')
            tag['class'] = current_class
    
    def reduce_spacing_proportionally(self):
        """6) Réduit les espacements proportionnellement."""
        # Supprimer les marges/paddings inline excessifs
        for tag in self.soup.find_all(style=True):
            style = tag.get('style', '')
            # Supprimer les marges/paddings fixes
            style = re.sub(r'margin:\s*\d+px', 'margin: 0', style)
            style = re.sub(r'padding:\s*\d+px', 'padding: 0', style)
            tag['style'] = style if style.strip() else None
    
    def optimize_tables(self):
        """Rend les tableaux scrollables."""
        for table in self.soup.find_all('table'):
            wrapper = self.soup.new_tag('div', attrs={'class': 'table-wrapper'})
            table.wrap(wrapper)
    
    def add_mobile_classes(self):
        """Ajoute des classes utiles."""
        body = self.soup.find('body')
        if body:
            current_class = body.get('class', [])
            if isinstance(current_class, str):
                current_class = [current_class]
            current_class.append('mobile-optimized')
            body['class'] = current_class
    
    def optimize(self) -> str:
        """Exécute toutes les optimisations."""
        print(f"🔧 Optimisation pour {self.target_platform}...")
        print(f"📱 Mode mobile: {'OUI' if self.is_mobile else 'NON'}")
        
        if not self.is_mobile:
            print("⏭️  Plateforme desktop détectée - aucune modification")
            return str(self.soup.prettify())
        
        print("\n🚀 Application des optimisations mobile:")
        
        self.add_viewport_meta()
        print("✓ 1. Viewport configuré")
        
        self.add_mobile_styles()
        print("✓ 2. Styles responsive ajoutés")
        
        self.optimize_images_and_logos()
        print("✓ 3. Images/logos proportionnels")
        
        self.add_platform_detection()
        print("✓ 4. Détection plateforme ajoutée")
        
        self.optimize_mobile_menu()
        print("✓ 5. Menu mobile avec hamburger")
        
        self.optimize_read_more_buttons()
        print("✓ 6. Boutons 'read more' optimisés")
        
        self.unify_and_reduce_fonts()
        print("✓ 7. Polices réduites et uniformisées")
        
        self.reduce_spacing_proportionally()
        print("✓ 8. Espacements réduits proportionnellement")
        
        self.optimize_tables()
        print("✓ 9. Tableaux scrollables")
        
        self.add_mobile_classes()
        print("✓ 10. Classes mobile ajoutées")
        
        print("\n✅ Optimisation terminée!")
        
        return str(self.soup.prettify())


def optimize_html_file(
    input_path: str, 
    output_path: Optional[str] = None,
    platform: Literal['auto', 'mobile', 'desktop'] = 'auto'
) -> str:
    """
    Optimise un fichier HTML pour mobile.
    
    Args:
        input_path: Chemin vers le fichier HTML source
        output_path: Chemin de sortie (optionnel)
        platform: 'auto', 'mobile', ou 'desktop'
    
    Returns:
        Chemin du fichier de sortie
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Fichier introuvable: {input_path}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Optimiser
    optimizer = MobileHTMLOptimizer(html_content, target_platform=platform)
    optimized_html = optimizer.optimize()
    
    # Déterminer le chemin de sortie
    if output_path is None:
        suffix = '_mobile' if optimizer.is_mobile else '_desktop'
        output_path = input_file.stem + suffix + input_file.suffix
    
    # Écrire le résultat
    output_file = Path(output_path)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(optimized_html)
    
    print(f"\n💾 Fichier sauvegardé: {output_file}")
    print(f"📊 Taille originale: {input_file.stat().st_size / 1024:.2f} KB")
    print(f"📊 Taille optimisée: {output_file.stat().st_size / 1024:.2f} KB")
    
    return str(output_file)


def optimize_html_string(
    html_content: str,
    platform: Literal['auto', 'mobile', 'desktop'] = 'auto'
) -> str:
    """Optimise une chaîne HTML."""
    optimizer = MobileHTMLOptimizer(html_content, target_platform=platform)
    return optimizer.optimize()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Optimise une page HTML pour mobile avec détection de plateforme"
    )
    parser.add_argument('input', help='Fichier HTML source')
    parser.add_argument('-o', '--output', help='Fichier de sortie (optionnel)', default=None)
    parser.add_argument(
        '-p', '--platform',
        choices=['auto', 'mobile', 'desktop'],
        default='auto',
        help='Plateforme cible (auto=détection automatique)'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = optimize_html_file(args.input, args.output, args.platform)
        print(f"\n🎉 Succès! Fichier optimisé: {output_file}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        exit(1)
