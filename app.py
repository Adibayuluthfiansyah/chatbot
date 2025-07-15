from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import datetime
from typing import List, Dict, Optional
import re

app = Flask(__name__)
CORS(app)  # Untuk mengizinkan request dari frontend

class ProductManager:
    def __init__(self):
        self.products = {
            "laptop": {"name": "Laptop Gaming ASUS ROG", "price": 15000000, "stock": 5, "description": "Laptop gaming Intel i7, RAM 16GB, VGA GTX 1650"},
            "smartphone": {"name": "Samsung Galaxy S24", "price": 12000000, "stock": 8, "description": "Smartphone flagship kamera 108MP, RAM 8GB, Storage 256GB"},
            "headphone": {"name": "Sony WH-1000XM5", "price": 4500000, "stock": 12, "description": "Headphone noise cancelling premium battery 30 jam"},
            "smartwatch": {"name": "Apple Watch Series 9", "price": 6000000, "stock": 3, "description": "Smartwatch GPS, health monitoring, water resistant"},
            "tablet": {"name": "iPad Pro 11 inch", "price": 13000000, "stock": 0, "description": "Tablet professional chip M2, display Liquid Retina"},
            "mouse": {"name": "Logitech MX Master 3", "price": 1200000, "stock": 15, "description": "Mouse wireless premium productivity dan gaming"},
            "keyboard": {"name": "Mechanical Keyboard RGB", "price": 800000, "stock": 7, "description": "Keyboard mechanical RGB lighting switch blue"}
        }
    
    def search_product(self, query: str) -> List[Dict]:
        query = query.lower()
        results = []
        for key, product in self.products.items():
            if query in key.lower() or query in product['name'].lower() or query in product['description'].lower():
                results.append({"key": key, **product})
        return results
    
    def get_all_products(self) -> Dict:
        return self.products

class CustomerServiceBot:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.conversation_log = []
        self.product_manager = ProductManager()
        
        self.base_context = """
        Anda adalah asisten customer service TechStore Indonesia.
        
        Info perusahaan:
        - Nama: TechStore Indonesia
        - Jam operasional: 08:00-17:00 WIB
        - Pengiriman: 1-3 hari kerja
        - Garansi: 1 tahun
        - Return: 7 hari setelah pembelian
        - Contact: support@techstore.id / WA: 0812-3456-7890
        
        Instruksi: 
        - Jawab ramah dan informatif, berikan info produk yang akurat.
        - Gunakan HTML formatting untuk response (seperti <br>, <strong>, dll).
        - JANGAN gunakan markdown code blocks seperti ```html atau ```.
        - Langsung berikan response dalam format HTML tanpa wrapper markdown.
        """
    
    def extract_product_query(self, user_message: str) -> Optional[str]:
        keywords = ['stok', 'stock', 'tersedia', 'ready', 'ada', 'jual', 'beli', 'harga', 'produk']
        user_message_lower = user_message.lower()
        
        if any(keyword in user_message_lower for keyword in keywords):
            for key in self.product_manager.products.keys():
                if key in user_message_lower:
                    return key
        return None
    
    def format_product_info(self, products: List[Dict]) -> str:
        if not products:
            return "Maaf, produk yang Anda cari tidak tersedia."
        
        response = "Berikut informasi produk yang tersedia:<br><br>"
        for product in products:
            stock_status = "✅ Tersedia" if product['stock'] > 0 else "❌ Stok Habis"
            response += f"📱 <strong>{product['name']}</strong><br>"
            response += f"💰 Harga: Rp {product['price']:,}<br>"
            response += f"📦 Stok: {product['stock']} unit ({stock_status})<br>"
            response += f"📝 Deskripsi: {product['description']}<br><br>"
        return response
    
    def clean_response(self, response_text: str) -> str:
        """Membersihkan response dari markdown formatting"""
        response_text = re.sub(r'```html\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)  
        response_text = re.sub(r'^\s*```.*?\n', '', response_text, flags=re.MULTILINE)
        
        return response_text.strip()
    
    def generate_response(self, user_message: str) -> str:
        try:
            product_query = self.extract_product_query(user_message)
            
            if product_query:
                products = self.product_manager.search_product(product_query)
                if products:
                    product_info = self.format_product_info(products)
                    prompt = f"{self.base_context}\n\nINFO PRODUK:\n{product_info}\n\nPertanyaan: {user_message}\n\nJawaban:"
                else:
                    prompt = f"{self.base_context}\n\nProduk tidak tersedia. Pertanyaan: {user_message}\n\nJawaban:"
            else:
                prompt = f"{self.base_context}\n\nPertanyaan: {user_message}\n\nJawaban:"
            
            response = self.model.generate_content(prompt)
            
            # Bersihkan response dari markdown formatting
            cleaned_response = self.clean_response(response.text)
            
            return cleaned_response
            
        except Exception as e:
            return f"Maaf, terjadi kesalahan. Hubungi support: 0812-3456-7890. Error: {str(e)}"
    
    def log_conversation(self, user_message: str, bot_response: str):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_message": user_message,
            "bot_response": bot_response
        }
        self.conversation_log.append(log_entry)


API_KEY = "AIzaSyAtpJpSf-uPFVbYO3zNvIQqgFL0uFXTMEk"  # API KEY
bot = CustomerServiceBot(API_KEY)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Generate response menggunakan Gemini
        response = bot.generate_response(user_message)
        
        # Log conversation
        bot.log_conversation(user_message, response)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(bot.product_manager.get_all_products())

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(bot.conversation_log)

if __name__ == '__main__':
    print("🚀 TechStore Customer Service API started!")
    print("📡 Backend running on http://localhost:5000")
    print("🔗 API endpoints:")
    print("   POST /api/chat - Send message")
    print("   GET /api/products - Get all products")
    print("   GET /api/logs - Get conversation logs")
    app.run(debug=True, port=5000)