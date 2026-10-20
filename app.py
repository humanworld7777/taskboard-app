from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

socketio = SocketIO(app, cors_allowed_origins="*")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), default="todo")

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return jsonify({"status": "success", "message": "Task Board API with WebSockets is running!"})

@socketio.on('update_task')
def handle_task_update(data):
    task_id = data.get("id")
    new_status = data.get("status")

    task = Task.query.get(task_id)
    if task:
        task.status = new_status
        db.session.commit()
        emit('task_updated', {"id": task.id, "status": task.status}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5009)
