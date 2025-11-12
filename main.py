from flask import Flask, request, jsonify
from db_config import get_db_connection, init_db

app = Flask(__name__)


init_db()



@app.route('/todos', methods=["GET"])
def get_todos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM todo")
    todos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(todos)


@app.route('/todos/<path:identifier>', methods=["GET"])
def get_todo_by_identifier(identifier):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if identifier.startswith("id="):
        try:
            todo_id = int(identifier.split("=", 1)[1])
            cursor.execute("SELECT * FROM todo WHERE id = %s", (todo_id,))
        except ValueError:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid ID format"}), 400
    else:
        cursor.execute("SELECT * FROM todo WHERE task LIKE %s", (f"%{identifier}%",))

    todos = cursor.fetchall()
    cursor.close()
    conn.close()

    if not todos:
        return jsonify({"message": "No matching todo found"}), 404

    return jsonify(todos)


@app.route('/todos', methods=["POST"])
def create_todo():
    data = request.get_json()
    task = data.get("task")
    status = data.get("status", False)

    if not task:
        return jsonify({"error": "Task is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todo (task, status) VALUES (%s, %s)", (task, status))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": new_id, "task": task, "status": status}), 201



@app.route('/todos/updatetask/<path:identifier>', methods=["PUT"])
def update_task(identifier):
    data = request.get_json()
    new_task = data.get("task")

    if not new_task:
        return jsonify({"error": "New task name is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    if identifier.startswith("id="):
        try:
            todo_id = int(identifier.split("=", 1)[1])
            cursor.execute("UPDATE todo SET task = %s WHERE id = %s", (new_task, todo_id))
        except ValueError:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid ID format"}), 400
    else:
        cursor.execute("UPDATE todo SET task = %s WHERE task LIKE %s", (new_task, f"%{identifier}%"))

    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"message": "No matching todo found"}), 404

    cursor.close()
    conn.close()
    return jsonify({"message": f"Task updated to '{new_task}'"}), 200


@app.route('/todos/updatestatus/<path:identifier>', methods=["PUT"])
def update_status(identifier):
    data = request.get_json()
    status = data.get("status")

    if status is None:
        return jsonify({"error": "Status (true/false) is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    if identifier.startswith("id="):
        try:
            todo_id = int(identifier.split("=", 1)[1])
            cursor.execute("UPDATE todo SET status = %s WHERE id = %s", (status, todo_id))
        except ValueError:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid ID format"}), 400
    else:
        cursor.execute("UPDATE todo SET status = %s WHERE task LIKE %s", (status, f"%{identifier}%"))

    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"message": "No matching todo found"}), 404

    cursor.close()
    conn.close()
    return jsonify({"message": f"Todo status updated to {status}"}), 200



@app.route('/todos/delete/<path:identifier>', methods=["DELETE"])
def delete_todo(identifier):
    conn = get_db_connection()
    cursor = conn.cursor()

    if identifier.startswith("id="):
        try:
            todo_id = int(identifier.split("=", 1)[1])
            cursor.execute("DELETE FROM todo WHERE id = %s", (todo_id,))
        except ValueError:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid ID format"}), 400
    else:
        cursor.execute("DELETE FROM todo WHERE task LIKE %s", (f"%{identifier}%",))

    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"message": "No matching todo found"}), 404

    cursor.close()
    conn.close()
    return jsonify({"message": f"Todo '{identifier}' deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
