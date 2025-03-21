from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import mysql.connector

app = Flask(__name__)

# JWT configuration
app.config['JWT_SECRET_KEY'] = '3fddf30a7412407b4176c07a23fb16c7'
jwt = JWTManager(app)

# Database configuration
db_host = 'localhost'
db_user = 'root'
db_password = ''
db_name = 'person'

# Connect to MySQL Database
db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)

# Endpoint to register a new Identifications Record
@app.route('/identifications', methods=['POST'])
@jwt_required()
def create_identification():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO identifications(
           firstname, lastname, gender, status, country, city, telephone) 
           VALUES(%s, %s, %s, %s, %s, %s, %s)""", 
           (data['firstname'], data['lastname'], data['gender'], data['status'], 
            data['country'], data['city'], data['telephone']
            ))
        db.commit()
        cursor.close()
        return jsonify({'message': 'Identification created successfully'}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Duplicate telephone entry'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint to get all Identifications Records
@app.route('/identifications', methods=['GET'])
@jwt_required()
def get_identifications():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM identifications")
    identifications = cursor.fetchall()
    cursor.close()
    return jsonify(identifications)


# Endpoint to get a specific Identifications Record by ID
@app.route('/identifications/<int:identification_id>', methods=['GET'])
@jwt_required()
def get_identification(identification_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM identifications WHERE id=%s", (identification_id,))
    identification = cursor.fetchone()
    cursor.close()
    
    if identification:
        return jsonify(identification)
    else:
        return jsonify({'error': 'Identification not found'}), 404


# Endpoint to get Identifications Record by telephone
@app.route('/identifications/telephone', methods=['GET'])
@jwt_required()
def get_identification_by_telephone():
    telephone = request.args.get('telephone')
    
    if not telephone:
        return jsonify({"error": "Telephone number is required"}), 400

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM identifications WHERE telephone=%s", (telephone,))
    identification = cursor.fetchall()
    cursor.close()

    if identification:
        return jsonify(identification)
    else:
        return jsonify({'error': 'Identification record not found for this telephone number'}), 404


# Endpoint to update a Identifications Record by ID
@app.route('/identifications/<int:identification_id>', methods=['PUT'])
@jwt_required()
def update_identification(identification_id):
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    cursor = db.cursor()
    try:
        cursor.execute("""
          UPDATE identifications 
          SET firstname=%s, lastname=%s, gender=%s, status=%s, country=%s, city=%s, telephone=%s 
          WHERE id=%s
          """, 
             (
                data['firstname'], data['lastname'], data['gender'], data['status'],
                data['country'], data['city'], data['telephone'], identification_id
            ))
        db.commit()
        cursor.close()
        return jsonify({'message': 'Identification updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint to delete a Identifications Record by ID
@app.route('/identifications/<int:identification_id>', methods=['DELETE'])
@jwt_required()
def delete_identification(identification_id):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM identifications WHERE id=%s", (identification_id,))
        db.commit()
        cursor.close()
        return jsonify({'message': 'Identification deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint of user login
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
