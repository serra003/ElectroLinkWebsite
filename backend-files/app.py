from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os
from datetime import datetime

# Initialize Flask app with explicit folder paths
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JSON_SORT_KEYS'] = False

# -------------------- Helper Functions --------------------

def load_products():
    """Load products from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'products.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading products: {e}")
        return []

def save_products(products):
    """Save products to JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'products.json')
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

def load_translations():
    """Load translations from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'translations.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# -------------------- Main Routes --------------------

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/products')
def products_page():
    """Products listing page"""
    return render_template('products.html')

@app.route('/product/<int:product_id>')
def product_detail_page(product_id):
    """Product detail page"""
    return render_template('product-detail.html', product_id=product_id)

@app.route('/cart')
def cart_page():
    """Shopping cart page"""
    return render_template('cart.html')

@app.route('/about')
def about_page():
    """About us page"""
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    """Contact page"""
    return render_template('contact.html')

@app.route('/faq')
def faq_page():
    """FAQ page"""
    return render_template('faq.html')

@app.route('/warranty')
def warranty_page():
    """Warranty and returns page"""
    return render_template('warranty.html')

@app.route('/blog')
def blog_page():
    """Blog listing page"""
    return render_template('blog.html')

@app.route('/blog/<int:post_id>')
def blog_detail_page(post_id):
    """Blog post detail page"""
    return render_template('blog-detail.html', post_id=post_id)

# -------------------- API Endpoints --------------------

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering and sorting"""
    products = load_products()

    # Get query parameters
    category = request.args.get('category', 'all')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort', 'default')
    visible_only = request.args.get('visible', 'true').lower() == 'true'

    # Filter by visibility
    if visible_only:
        products = [p for p in products if p.get('visible', True)]

    # Filter by category
    if category != 'all':
        products = [p for p in products if p.get('category') == category]

    # Filter by price range
    if min_price is not None:
        products = [p for p in products if p.get('price', 0) >= min_price]
    if max_price is not None:
        products = [p for p in products if p.get('price', 0) <= max_price]

    # Sort products
    if sort_by == 'name-asc':
        products.sort(key=lambda x: x.get('name', '').lower())
    elif sort_by == 'name-desc':
        products.sort(key=lambda x: x.get('name', '').lower(), reverse=True)
    elif sort_by == 'price-asc':
        products.sort(key=lambda x: x.get('price', 0))
    elif sort_by == 'price-desc':
        products.sort(key=lambda x: x.get('price', 0), reverse=True)

    return jsonify({
        'success': True,
        'count': len(products),
        'products': products
    }), 200

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID"""
    products = load_products()
    product = next((p for p in products if p.get('id') == product_id), None)
    
    if product:
        return jsonify({
            'success': True,
            'product': product
        }), 200
    
    return jsonify({
        'success': False,
        'error': 'Product not found'
    }), 404

@app.route('/api/products/featured', methods=['GET'])
def get_featured_products():
    """Get featured products for home page"""
    products = load_products()
    
    # Filter visible products
    visible_products = [p for p in products if p.get('visible', True)]
    
    # Get first 8 products (or limit from query param)
    limit = request.args.get('limit', 8, type=int)
    featured = visible_products[:limit]
    
    return jsonify({
        'success': True,
        'count': len(featured),
        'products': featured
    }), 200

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all unique product categories"""
    products = load_products()
    categories = sorted(list(set(p.get('category', 'other') for p in products if p.get('visible', True))))
    
    return jsonify({
        'success': True,
        'categories': categories
    }), 200

@app.route('/api/search', methods=['GET'])
def search_products():
    """Search products by name, code, or description"""
    query = request.args.get('q', '').lower().strip()
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Search query is required'
        }), 400

    products = load_products()
    results = []
    
    for p in products:
        # Skip invisible products
        if not p.get('visible', True):
            continue
            
        # Search in name, code, and description
        name_match = query in p.get('name', '').lower()
        code_match = query in p.get('code', '').lower()
        desc_match = query in p.get('description', '').lower()
        
        if name_match or code_match or desc_match:
            results.append(p)
    
    return jsonify({
        'success': True,
        'query': query,
        'count': len(results),
        'results': results
    }), 200

@app.route('/api/translations', methods=['GET'])
def get_translations():
    """Get translations for a specific language"""
    lang = request.args.get('lang', 'az')
    translations = load_translations()
    
    if lang in translations:
        return jsonify({
            'success': True,
            'language': lang,
            'translations': translations[lang]
        }), 200
    
    return jsonify({
        'success': False,
        'error': f'Language {lang} not supported',
        'available_languages': list(translations.keys())
    }), 404

# -------------------- Static File Serving --------------------

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (images, etc.)"""
    return send_from_directory('static', filename)

# -------------------- Error Handlers --------------------

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    # For API requests, return JSON
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    # For page requests, render a 404 template (optional)
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

# -------------------- Health Check --------------------

@app.route('/health')
def health_check():
    """Health check endpoint for deployment platforms"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# -------------------- Run App --------------------

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Run the Flask development server
    print("Starting ElectroLink.az Flask Server...")
    print("Server running at: http://localhost:5000")
    print("Press CTRL+C to stop the server")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )