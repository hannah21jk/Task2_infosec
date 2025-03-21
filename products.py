from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import mysql.connector

app = Flask(__name__)

# JWT configuration
app.config['JWT_SECRET_KEY'] = '32b9f145b80dcbf512b665b0f92a9fbe'
jwt = JWTManager(app)

# Database configuration
db_host = 'localhost'
db_user = 'root'
db_password = ''
db_name = 'person'

# Connect to MySQL Database
db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)


# Endpoint to register a new Product
@app.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO Products (pname, description, price, stock) 
                          VALUES (%s, %s, %s, %s)""", 
                       (data['pname'], data['description'], data['price'], data['stock']))
        db.commit()
        cursor.close()
        return jsonify({'message': 'Product created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to get all Products
@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    cursor.close()
    return jsonify(products)

# Endpoint to get a specific Product by ID
@app.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Products WHERE pid=%s", (product_id,))
    product = cursor.fetchone()
    cursor.close()

    if product:
        return jsonify(product)
    else:
        return jsonify({'error': 'Product not found'}), 404

# Endpoint to update a Product by ID
@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    cursor = db.cursor()
    try:
        cursor.execute("""UPDATE Products 
                          SET pname=%s, description=%s, price=%s, stock=%s 
                          WHERE pid=%s""", 
                       (data['pname'], data['description'], data['price'], data['stock'], product_id))
        db.commit()
        cursor.close()
        return jsonify({'message': 'Product updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to delete a Product by ID
@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Products WHERE pid=%s", (product_id,))
        db.commit()
        cursor.close()
        return jsonify({'message': 'Product deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == 'adminpassword':
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
