# This is the file for my Building Restful APIs assignment. The other file is just for the homework from the lesson.

from flask import Flask, jsonify, request
from mysql.connector import Error
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector

app = Flask(__name__)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields = ("name", "age")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class WorkoutSessionsSchema(ma.Schema):
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ("member_id", "session_date", "session_time", "activity")

workoutsession_schema = WorkoutSessionsSchema()
workoutsessions_schema = WorkoutSessionsSchema(many=True)


def get_db_connection():
    db_name = "fitness_center"
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
    return "Welcome to the Fitness Center database"

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM members WHERE id = %s"

        member_id = (id, )
        cursor.execute(query, member_id)

        members = cursor.fetchone()

        return member_schema.jsonify(members)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        new_member = (member_data['name'], member_data['age'])

        query = "INSERT INTO members (name, age) VALUES (%s, %s)"

        cursor.execute(query, new_member)
        conn.commit()

        return jsonify({"message": "New member added successfully."}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/members/<int:id>', methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_member = (member_data['name'], member_data['age'], id)

        query = "UPDATE members SET name = %s, age = %s WHERE id = %s"

        cursor.execute(query, updated_member)
        conn.commit()

        return jsonify({"message": "Member updated successfully."}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/members/<int:id>', methods=["DELETE"])
def delete_member(id):
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        member_to_remove = (id,)

        cursor.execute("SELECT * FROM members WHERE id = %s", member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "Member not found"}), 404

        query = "DELETE FROM members WHERE id = %s"
        cursor.execute(query, member_to_remove)
        conn.commit()

        return jsonify({"message": "Member deleted successfully."}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/workoutsessions/<int:member_id>', methods=['GET'])
def get_workoutsessions_by_member(member_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM workoutsessions WHERE member_id = %s"

        member_id = (member_id, )
        cursor.execute(query, member_id)

        workouts = cursor.fetchall()

        return workoutsessions_schema.jsonify(workouts)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/workoutsessions/', methods=['GET'])
def get_all_workoutsessions():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM workoutsessions"

        cursor.execute(query)

        workouts = cursor.fetchall()

        return workoutsessions_schema.jsonify(workouts)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/workoutsessions', methods=['POST'])
def add_workout_session():
    try:
        workout_session_data = workoutsession_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        new_workout_session = (workout_session_data['member_id'], workout_session_data['session_date'], \
workout_session_data['session_time'], workout_session_data['activity'])

        query = "INSERT INTO workoutsessions (member_id, session_date, session_time, activity) VALUES (%s, %s, %s, %s)"

        cursor.execute(query, new_workout_session)
        conn.commit()

        return jsonify({"message": "New workout added successfully."}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/workoutsessions/<int:session_id>', methods=["PUT"])
def update_workout_session(session_id):
    try:
        workout_session_data = workoutsession_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_workout_session = (workout_session_data['member_id'], workout_session_data['session_date'], \
workout_session_data['session_time'], workout_session_data['activity'], session_id)

        query = "UPDATE workoutsessions SET member_id = %s, session_date = %s, session_time = %s, activity = %s WHERE session_id = %s"

        cursor.execute(query, updated_workout_session)
        conn.commit()

        return jsonify({"message": "Workout updated successfully."}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == '__main__':
   app.run(debug=True)