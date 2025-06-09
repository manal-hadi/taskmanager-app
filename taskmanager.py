from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

# Create the database tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks, now=datetime.utcnow())

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if not task.completed:
        task.completed = True
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/uncomplete/<int:task_id>')
def uncomplete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.completed:
        task.completed = False
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        deadline = request.form.get('deadline')  # Not used in model, but form provides it
        if title:
            new_task = Task(title=title, description=description)
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for('index'))
    # For GET, just show the tasks (handled by index)
    return index()

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        deadline = request.form.get('deadline')
        if title:
            task.title = title
            task.description = description
            # Store deadline in created_at if you want to use it, since model has no deadline field
            if deadline:
                try:
                    from datetime import datetime
                    task.created_at = datetime.strptime(deadline, '%Y-%m-%d')
                except Exception:
                    pass  # Ignore invalid date
            db.session.commit()
            return redirect(url_for('index'))
    # For GET, render the edit form with current values, including deadline as date string
    deadline_str = task.created_at.strftime('%Y-%m-%d') if task.created_at else ''
    return render_template('edit_task.html', task=task, deadline=deadline_str)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)