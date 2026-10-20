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
    # Broadcast new task creation via WebSocket to all connected clients
    socketio.emit('task_created', {"id": new_task.id, "title": new_task.title, "status": new_task.status})
    return jsonify({"id": new_task.id, "title": new_task.title, "status": new_task.status}), 201
