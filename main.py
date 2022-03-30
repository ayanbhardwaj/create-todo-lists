# shri ganesh karen
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreateList, RegisterForm, LoginForm, TaskForm, AddMember
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    # This will act like a List of TodoList objects attached to each User.
    # The "owner" refers to the author property in the TodoList class.
    lists = relationship("TodoList", back_populates="owner")
    tasks = relationship("Task", back_populates="owner")
    list = relationship("TodoList", secondary="users_lists", back_populates="user")


class TodoList(db.Model):
    __tablename__ = "todo_lists"
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "lists" refers to the lists property in the User class.
    owner = relationship("User", back_populates="lists")
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    tasks = relationship("Task", back_populates="parent_list")
    user = relationship("User", secondary="users_lists", back_populates="list")


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    list_id = db.Column(db.Integer, db.ForeignKey("todo_lists.id"))
    owner = relationship("User", back_populates="tasks")
    parent_list = relationship("TodoList", back_populates="tasks")
    text = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(100))
    assigned_to = db.Column(db.String(100))


class UserList(db.Model):
    __tablename__ = "users_lists"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    list_id = db.Column(db.Integer, db.ForeignKey('todo_lists.id'))


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def home():
    l_form = LoginForm()
    r_form = RegisterForm()
    if r_form.validate_on_submit():
        email = r_form.email.data
        email_check = User.query.filter_by(email=email).first()
        if email_check:
            flash("The email is already registered. Try log in instead.")
            return redirect(url_for('home'))
        salted_hashed_password = generate_password_hash(password=r_form.password.data, method='pbkdf2:sha256',
                                                        salt_length=8)
        name = r_form.name.data
        new_user = User(
            email=email,
            password=salted_hashed_password,
            name=name
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_lists'))
    if l_form.validate_on_submit():
        email = l_form.email.data
        password = l_form.password.data

        # Find user by email entered.
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email is not registered. Enter correct email or register")
            return redirect(url_for('home'))

        # Check stored password hash against entered password hashed.
        if check_password_hash(pwhash=user.password, password=password):
            login_user(user)
            return redirect(url_for('get_lists'))
        else:
            flash("Password incorrect. Please try again")
            return redirect(url_for('home'))
    return render_template("index.html", l_form=l_form, r_form=r_form)


@login_required
@app.route('/lists', methods=['GET', 'POST'])
def get_lists():
    form = CreateList()
    user_lists = TodoList.query.filter_by(owner=current_user).all()
    other_lists_id = UserList.query.filter_by(user_id=current_user.id).all()
    for uid in other_lists_id:
        assigned_list = TodoList.query.filter_by(id=uid.list_id).first()
        user_lists.append(assigned_list)
    if form.validate_on_submit():
        new_list = TodoList(
            title=form.title.data,
            owner=current_user,
            date=date.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for("get_lists"))
    return render_template("lists.html", user_lists=user_lists, form=form)


@app.route("/show/<int:list_id>", methods=['GET', 'POST'])
@login_required
def show_list(list_id):
    requested_list = TodoList.query.filter_by(id=list_id).first()
    list_tasks = Task.query.filter_by(list_id=list_id).all()
    c_t_form = TaskForm()
    mem_form = AddMember()
    members_id = UserList.query.filter_by(list_id=list_id).all()
    members = []
    for uid in members_id:
        user = User.query.get(uid.user_id)
        members.append(user)
    owner = User.query.get(requested_list.owner_id)
    owner_name = owner.name
    if c_t_form.validate_on_submit():
        new_task = Task(
            text=c_t_form.task.data,
            owner=current_user,
            parent_list=requested_list,
            start_date=c_t_form.start_date.data,
            due_date=c_t_form.due_date.data,
            status=c_t_form.status.data,
            assigned_to=c_t_form.assigned_to.data,
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("show_list", list_id=requested_list.id))
    if mem_form.validate_on_submit():
        if requested_list.owner == current_user:
            email = mem_form.email.data
            user = User.query.filter_by(email=email).first()
            if user:
                requested_list.user.append(user)
                db.session.commit()
                return redirect(url_for("show_list", list_id=requested_list.id))
            else:
                flash("Member not registered. Only registered users can be added.")
                return redirect(url_for("show_list", list_id=requested_list.id))
        else:
            flash("Only list owner can add a member.")
            return redirect(url_for("show_list", list_id=requested_list.id))
    return render_template("show_list.html", tasks=list_tasks, list=requested_list, c_t_form=c_t_form,
                           mem_form=mem_form, members=members, owner=owner_name)


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    task = Task.query.filter_by(id=task_id).first()
    form = TaskForm(
        task=task.text,
        start_date=task.start_date,
        due_date=task.due_date,
        status=task.status,
        assigned_to=task.assigned_to,
    )
    if form.validate_on_submit():
        task.text = form.task.data
        task.start_date = form.start_date.data
        task.due_date = form.due_date.data
        task.status = form.status.data
        task.assigned_to=form.assigned_to.data
        db.session.commit()
        return redirect(url_for("show_list", list_id=task.list_id))
    return render_template('edit_post.html', form=form)


@app.route("/delete/<int:task_id>", methods=['GET'])
@login_required
def delete_task(task_id):
    task_to_delete = Task.query.get(task_id)
    list_id = task_to_delete.list_id
    if task_to_delete.owner_id == current_user.id:
        db.session.delete(task_to_delete)
        db.session.commit()
    else:
        flash("Only owner can delete task.")
    return redirect(url_for('show_list', list_id=list_id))


@app.route("/delete/list/<int:list_id>", methods=['GET'])
@login_required
def delete_list(list_id):
    tasks_to_delete = Task.query.filter_by(list_id=list_id).all()
    for task in tasks_to_delete:
        db.session.delete(task)
    list_to_delete = TodoList.query.get(list_id)
    db.session.delete(list_to_delete)
    if list_to_delete.owner_id == current_user.id:
        db.session.commit()
    else:
        flash("Only owner can delete list.")
    return redirect(url_for('get_lists'))


@app.route("/delete/member/<int:user_id>", methods=['GET'])
@login_required
def delete_member(user_id):
    user_to_delete_from_list = UserList.query.filter_by(user_id=user_id).first()
    list_id = user_to_delete_from_list.list_id
    current_list = TodoList.query.get(list_id)
    if current_list.owner_id == current_user.id:
        db.session.delete(user_to_delete_from_list)
        db.session.commit()
    else:
        flash("Only owner can delete members.")
    return redirect(url_for('show_list', list_id=list_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
