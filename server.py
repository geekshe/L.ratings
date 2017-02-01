"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db
import sqlalchemy


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    a = jsonify([1,3])
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/register', methods=["GET"])
def display_registration():
    """Display register form"""

    return render_template("register_form.html")

@app.route('/register', methods=["POST"])
def process_registration():
    """Process a new user from registration form"""

    # Grab inputs from registration form
    username = request.form.get('username')
    password = request.form.get('password')

    # If user doesn't exist, add them to the database
    if len(User.query.filter_by(email=username).all()) == 0:
        user = User(email=username,
                    password=password)

        # Add user to the session
        db.session.add(user)

        # Commit transaction to db
        db.session.commit()

        print "user %s added to db" % (username)

        flash("New account created")

    return redirect("/login")

@app.route('/login', methods=["GET"])
def display_login():
    """Display login form"""

    return render_template('login_form.html')

@app.route('/login', methods=["POST"])
def log_in():
    """Log user in"""

    # Grab username and password from form
    username = request.form.get('username')
    password = request.form.get('password')

    # Query for user in database
    user = User.query.filter_by(email=username)

    # user.all()

    # If user in database and if password matches, login
    try:
        login_user = user.one()
    # Throws an exception if user.one does not return an item from the database
    except sqlalchemy.orm.exc.NoResultFound:
        flash("No User with username %s" % (username))
        return redirect("/login")

    if login_user.password == password:
        # Add user to session cookie
        session['username'] = username
        flash("Logged in")
        return redirect("/")
    else:
        flash("Incorrect password")
        return redirect("/login")


@app.route('/logout')
def log_out():
    """Log user out"""

    # Remove user from session
    del session['username']

    flash("Logged out")
    return redirect("/")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')
