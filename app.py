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

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), default="todo")

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{"id": t.id, "title": t.title, "status": t.status} for t in tasks])

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.json
    new_task = Task(title=data.get("title"), status=data.get("status", "todo"))
    db.session.add(new_task)
    db.session.commit()
    socketio.emit('task_created', {"id": new_task.id, "title": new_task.title, "status": new_task.status})
    return jsonify({"id": new_task.id, "title": new_task.title, "status": new_task.status}), 201

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
    # Get the port from Render environment variables, default to 5009 locally
    port = int(os.environ.get("PORT", 5009))
    socketio.run(app, host="0.0.0.0", port=port)
