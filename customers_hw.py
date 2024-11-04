# This is the homework for the lesson. For the Building Restful APIs assignment, see main.py

# run pip install Flask.marshmallow
# run pip install mysql-connector-python

import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError

app = Flask(__name__)
ma = Marshmallow(app)

class CustomerSchema(ma.Schema):
    id = fields.Integer(required=False)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

def get_db_connection():
    db_name = "e_commerce_db"
    user = "root"
    password = "password"
    host = "localhost"
    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )
        print("Connection successful.")
        return conn
    
    except Error as e:
        print(f"Error: {e}")
        return None


@app.route('/')
def home():
    return "Welcome to the Flask Music Festival"

@app.route('/customers', methods=["GET"])
def get_customers():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM customers"

        cursor.execute(query)

        customers = cursor.fetchall()

        return customers_schema.jsonify(customers)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/customers', methods=["POST"])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        new_customer = (customer_data['name'], customer_data['email'], customer_data['phone'])

        query = "INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)"

        cursor.execute(query, new_customer)
        conn.commit()

        return jsonify({"message": "New customer added successfully."}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/customers/<int:id>', methods=["PUT"])
def update_customer(id):
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_customer = (customer_data['name'], customer_data['email'], customer_data['phone'], id)

        query = "UPDATE Customers SET name = %s, email = %s, phone = %s WHERE id = %s"

        cursor.execute(query, updated_customer)
        conn.commit()

        return jsonify({"message": "Customer updated successfully."}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/customers/<int:id>', methods=["DELETE"])
def delete_customer(id):
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        customer_to_remove = (id,)

        cursor.execute("SELECT * FROM customers WHERE id = %s", customer_to_remove)
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        query = "DELETE FROM customers WHERE id = %s"
        cursor.execute(query, customer_to_remove)
        conn.commit()

        return jsonify({"message": "Customer deleted successfully."}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == '__main__':
   app.run(debug=True)