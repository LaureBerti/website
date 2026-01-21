"""
Script Python pour optimiser une page HTML pour mobile
Transforme automatiquement le HTML pour une meilleure expérience mobile
"""

from bs4 import BeautifulSoup
import re
from pathlib import Path
from typing import Optional


class MobileHTMLOptimizer:
    """Optimise les pages HTML pour les écrans de smartphones."""
    
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.mobile_styles = self._get_mobile_styles()
    
    def _get_mobile_styles(self) -> str:
        """Génère les styles CSS pour mobile."""
        return """
/* Mobile Optimization Styles */
* {
    box-sizing: border-box;
}

html {
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
}

body {
    margin: 0;
    padding: 0;
    font-size: 16px;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Responsive images */
img {
    max-width: 100%;
    height: auto;
    display: block;
}

/* Responsive videos */
iframe, video {
    max-width: 100%;
    height: auto;
}

/* Responsive tables */
table {
    width: 100%;
    overflow-x: auto;
    display: block;
    border-collapse: collapse;
}

/* Touch-friendly buttons */
button, a, input[type="submit"], input[type="button"] {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 20px;
    font-size: 16px;
    cursor: pointer;
    -webkit-tap-highlight-color: rgba(0,0,0,0.1);
}

/* Responsive text */
h1 { font-size: 2em; margin: 0.67em 0; }
h2 { font-size: 1.5em; margin: 0.75em 0; }
h3 { font-size: 1.17em; margin: 0.83em 0; }

p {
    margin: 1em 0;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* Responsive containers */
.container, .content, main, article {
    max-width: 100%;
    padding: 15px;
    margin: 0 auto;
}

/* Responsive navigation */
nav {
    width: 100%;
}

nav ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

nav li {
    display: block;
    width: 100%;
}

nav a {
    display: block;
    padding: 15px;
    text-decoration: none;
}

/* Forms optimization */
input, select, textarea {
    width: 100%;
    max-width: 100%;
    padding: 12px;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-bottom: 15px;
}

/* Flexbox layouts */
.flex-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

/* Grid layouts */
.grid-container {
    display: grid;
    grid-template-columns: 1fr;
    gap: 15px;
}

/* Hide desktop-only elements */
.desktop-only, .hidden-mobile {
    display: none !important;
}

/* Media queries for larger phones */
@media (min-width: 375px) {
    body { font-size: 17px; }
    .container { padding: 20px; }
}

@media (min-width: 768px) {
    .grid-container {
        grid-template-columns: repeat(2, 1fr);
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
        
        # Supprimer ancien viewport s'il existe
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
        
        # Créer balise style
        style_tag = self.soup.new_tag('style')
        style_tag.string = self.mobile_styles
        head.append(style_tag)
    
    def optimize_images(self):
        """Optimise les images pour mobile."""
        for img in self.soup.find_all('img'):
            # Ajouter attribut loading lazy
            img['loading'] = 'lazy'
            
            # S'assurer que l'image a un alt
            if not img.get('alt'):
                img['alt'] = 'Image'
            
            # Supprimer les largeurs/hauteurs fixes
            if img.get('width'):
                del img['width']
            if img.get('height'):
                del img['height']
            
            # Ajouter style responsive si absent
            current_style = img.get('style', '')
            if 'max-width' not in current_style:
                img['style'] = f"{current_style}; max-width: 100%; height: auto;"
    
    def optimize_tables(self):
        """Rend les tableaux scrollables sur mobile."""
        for table in self.soup.find_all('table'):
            # Wrapper pour scroll horizontal
            wrapper = self.soup.new_tag('div', attrs={'class': 'table-wrapper'})
            wrapper['style'] = 'overflow-x: auto; -webkit-overflow-scrolling: touch;'
            
            table.wrap(wrapper)
    
    def make_links_touch_friendly(self):
        """Optimise les liens pour les écrans tactiles."""
        for link in self.soup.find_all('a'):
            current_style = link.get('style', '')
            if 'display' not in current_style:
                link['style'] = f"{current_style}; display: inline-block; min-height: 44px; padding: 8px 12px;"
    
    def optimize_fonts(self):
        """Optimise les tailles de police."""
        # Éviter le zoom automatique sur iOS pour les inputs
        for input_tag in self.soup.find_all(['input', 'select', 'textarea']):
            current_style = input_tag.get('style', '')
            if 'font-size' not in current_style:
                input_tag['style'] = f"{current_style}; font-size: 16px;"
    
    def optimize_performance(self):
        """Optimisations de performance pour mobile."""
        head = self.soup.find('head')
        if not head:
            return
        
        # Préconnexion aux domaines externes
        external_domains = set()
        for tag in self.soup.find_all(['link', 'script', 'img']):
            src = tag.get('href') or tag.get('src', '')
            if src.startswith('http'):
                from urllib.parse import urlparse
                domain = urlparse(src).netloc
                if domain:
                    external_domains.add(domain)
        
        for domain in external_domains:
            preconnect = self.soup.new_tag('link', rel='preconnect', href=f'https://{domain}')
            head.append(preconnect)
        
        # Async loading pour scripts non-critiques
        for script in self.soup.find_all('script', src=True):
            if 'async' not in script.attrs and 'defer' not in script.attrs:
                script['defer'] = ''
    
    def add_dark_mode_support(self):
        """Ajoute le support du mode sombre."""
        head = self.soup.find('head')
        if not head:
            return
        
        dark_mode_css = """
/* Dark mode support */
@media (prefers-color-scheme: dark) {
    body {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
    
    a {
        color: #58a6ff;
    }
    
    img {
        opacity: 0.9;
    }
    
    table {
        border-color: #444;
    }
    
    th, td {
        border-color: #444;
    }
}
"""
        style_tag = self.soup.new_tag('style')
        style_tag.string = dark_mode_css
        head.append(style_tag)
    
    def add_pwa_meta(self):
        """Ajoute les métadonnées pour Progressive Web App."""
        head = self.soup.find('head')
        if not head:
            return
        
        # Theme color
        theme_meta = self.soup.new_tag('meta', attrs={
            'name': 'theme-color',
            'content': '#2563eb'
        })
        head.append(theme_meta)
        
        # Apple touch icon placeholder
        apple_icon = self.soup.new_tag('link', attrs={
            'rel': 'apple-touch-icon',
            'href': '/icon-192.png'
        })
        head.append(apple_icon)
        
        # Status bar
        status_meta = self.soup.new_tag('meta', attrs={
            'name': 'apple-mobile-web-app-status-bar-style',
            'content': 'default'
        })
        head.append(status_meta)
    
    def optimize_navigation(self):
        """Optimise la navigation pour mobile."""
        # Améliorer les liens de navigation
        nav = self.soup.find('nav')
        if not nav:
            return
        
        # Ajouter des icônes de navigation
        nav_links = nav.find_all('a')
        for i, link in enumerate(nav_links):
            current_style = link.get('style', '')
            link['style'] = f"{current_style}; display: flex; align-items: center; gap: 8px;"
    
    def add_offline_support_info(self):
        """Ajoute des infos pour le support offline."""
        head = self.soup.find('head')
        if not head:
            return
        
        # Meta pour indiquer l'app peut fonctionner offline
        offline_meta = self.soup.new_tag('meta', attrs={
            'name': 'mobile-web-app-capable',
            'content': 'yes'
        })
        head.append(offline_meta)
    
    def improve_accessibility(self):
        """Améliore l'accessibilité mobile."""
        # Ajouter lang si absent
        html_tag = self.soup.find('html')
        if html_tag and not html_tag.get('lang'):
            html_tag['lang'] = 'en'
        
        # S'assurer que tous les liens ont un texte descriptif
        for link in self.soup.find_all('a'):
            if not link.get_text().strip() and not link.get('aria-label'):
                href = link.get('href', '')
                link['aria-label'] = f"Link to {href}"
        
        # Ajouter skip navigation
        body = self.soup.find('body')
        if body:
            skip_link = self.soup.new_tag('a', attrs={
                'href': '#main-content',
                'class': 'skip-to-main',
                'style': 'position: absolute; left: -9999px; z-index: 999;'
            })
            skip_link.string = 'Skip to main content'
            body.insert(0, skip_link)
    
    def compress_inline_styles(self):
        """Optimise les styles inline."""
        for tag in self.soup.find_all(style=True):
            style = tag.get('style', '')
            # Supprimer les espaces inutiles
            style = ' '.join(style.split())
            tag['style'] = style
    
    def add_touch_gestures_hints(self):
        """Ajoute des indices visuels pour les gestes tactiles."""
        body = self.soup.find('body')
        if not body:
            return
        
        gesture_css = """
/* Touch gesture hints */
.swipeable {
    touch-action: pan-x pan-y;
    user-select: none;
}

.draggable {
    touch-action: none;
    cursor: grab;
}

.draggable:active {
    cursor: grabbing;
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* Remove tap highlight on mobile */
* {
    -webkit-tap-highlight-color: transparent;
}
"""
        style_tag = self.soup.new_tag('style')
        style_tag.string = gesture_css
        self.soup.head.append(style_tag)
    
    def fix_fixed_widths(self):
        """Supprime les largeurs fixes qui cassent le responsive."""
        # Trouver tous les éléments avec largeur fixe en px
        for tag in self.soup.find_all(style=re.compile(r'width:\s*\d+px')):
            style = tag.get('style', '')
            # Remplacer width: XXpx par max-width: 100%
            new_style = re.sub(r'width:\s*\d+px', 'max-width: 100%', style)
            tag['style'] = new_style
    
    def add_hamburger_menu(self):
        """Convertit les menus de navigation en menu hamburger."""
        nav = self.soup.find('nav')
        if not nav:
            return
        
        # Ajouter bouton hamburger
        hamburger = self.soup.new_tag('button', attrs={
            'id': 'mobile-menu-toggle',
            'aria-label': 'Menu',
            'style': 'display: block; background: #333; color: white; border: none; padding: 15px; cursor: pointer;'
        })
        hamburger.string = '☰ Menu'
        
        # Wrapper pour le menu
        menu_wrapper = self.soup.new_tag('div', attrs={
            'id': 'mobile-menu',
            'style': 'display: none;'
        })
        
        # Déplacer le contenu du nav dans le wrapper
        for child in list(nav.children):
            menu_wrapper.append(child)
        
        nav.clear()
        nav.append(hamburger)
        nav.append(menu_wrapper)
        
        # Ajouter JavaScript pour toggle
        script = self.soup.new_tag('script')
        script.string = """
        document.getElementById('mobile-menu-toggle').addEventListener('click', function() {
            var menu = document.getElementById('mobile-menu');
            menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
        });
        """
        self.soup.body.append(script)
    
    def remove_flash_animations(self):
        """Supprime les éléments Flash obsolètes."""
        for tag in self.soup.find_all(['embed', 'object']):
            if 'flash' in str(tag).lower() or 'swf' in str(tag).lower():
                tag.decompose()
    
    def add_mobile_friendly_classes(self):
        """Ajoute des classes utiles pour le responsive."""
        body = self.soup.find('body')
        if body:
            current_class = body.get('class', [])
            if isinstance(current_class, str):
                current_class = [current_class]
            current_class.append('mobile-optimized')
            body['class'] = current_class
    
    def optimize(self) -> str:
        """Exécute toutes les optimisations."""
        print("🔧 Optimisation pour mobile en cours...")
        
        self.add_viewport_meta()
        print("✓ Viewport ajouté")
        
        self.add_mobile_styles()
        print("✓ Styles mobile ajoutés")
        
        self.optimize_images()
        print("✓ Images optimisées")
        
        self.optimize_tables()
        print("✓ Tableaux rendus scrollables")
        
        self.make_links_touch_friendly()
        print("✓ Liens tactiles optimisés")
        
        self.optimize_fonts()
        print("✓ Polices optimisées")
        
        self.fix_fixed_widths()
        print("✓ Largeurs fixes corrigées")
        
        self.add_hamburger_menu()
        print("✓ Menu hamburger ajouté")
        
        self.remove_flash_animations()
        print("✓ Flash supprimé")
        
        self.add_mobile_friendly_classes()
        print("✓ Classes mobile ajoutées")
        
        # Nouvelles optimisations
        self.optimize_performance()
        print("✓ Performance optimisée (preconnect, defer)")
        
        self.add_dark_mode_support()
        print("✓ Mode sombre ajouté")
        
        self.add_pwa_meta()
        print("✓ Métadonnées PWA ajoutées")
        
        self.optimize_navigation()
        print("✓ Navigation optimisée")
        
        self.add_offline_support_info()
        print("✓ Support offline ajouté")
        
        self.improve_accessibility()
        print("✓ Accessibilité améliorée")
        
        self.compress_inline_styles()
        print("✓ Styles compressés")
        
        self.add_touch_gestures_hints()
        print("✓ Gestes tactiles optimisés")
        
        print("✅ Optimisation terminée!")
        
        return str(self.soup.prettify())


def optimize_html_file(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Optimise un fichier HTML pour mobile.
    
    Args:
        input_path: Chemin vers le fichier HTML source
        output_path: Chemin de sortie (optionnel, par défaut: input_mobile.html)
    
    Returns:
        Chemin du fichier de sortie
    """
    # Lire le fichier
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Fichier introuvable: {input_path}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Optimiser
    optimizer = MobileHTMLOptimizer(html_content)
    optimized_html = optimizer.optimize()
    
    # Déterminer le chemin de sortie
    if output_path is None:
        output_path = input_file.stem + '_mobile' + input_file.suffix
    
    # Écrire le résultat
    output_file = Path(output_path)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(optimized_html)
    
    print(f"\n💾 Fichier sauvegardé: {output_file}")
    print(f"📱 Taille originale: {input_file.stat().st_size / 1024:.2f} KB")
    print(f"📱 Taille optimisée: {output_file.stat().st_size / 1024:.2f} KB")
    
    return str(output_file)


def optimize_html_string(html_content: str) -> str:
    """
    Optimise une chaîne HTML pour mobile.
    
    Args:
        html_content: Contenu HTML en chaîne
    
    Returns:
        HTML optimisé
    """
    optimizer = MobileHTMLOptimizer(html_content)
    return optimizer.optimize()


# Exemple d'utilisation
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Optimise une page HTML pour les écrans de smartphones"
    )
    parser.add_argument(
        'input',
        help='Fichier HTML source à optimiser'
    )
    parser.add_argument(
        '-o', '--output',
        help='Fichier HTML de sortie (optionnel)',
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        output_file = optimize_html_file(args.input, args.output)
        print(f"\n🎉 Succès! Ouvrez {output_file} sur votre smartphone pour tester.")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        exit(1)
