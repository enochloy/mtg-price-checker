import os
import json
from flask import Flask, session, redirect, render_template, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        with sqlite3.connect("users.db") as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            rows = cur.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        with sqlite3.connect("users.db") as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            rows = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()

        if not username:
            return apology("must provide username")
        elif len(rows) > 0:
            return apology("username already taken")
        elif not password or not confirmation:
            return apology("must provide password")
        elif password != confirmation:
            return apology("passwords must match")
        
        with sqlite3.connect("users.db") as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, hash) VALUES (?, ?);", (username, generate_password_hash(password)))
            row = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        
        session["user_id"] = row["id"]

        return redirect("/")
    else:
        return render_template("register.html")
    
@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password"""
    if request.method == "POST":
        cur_password = request.form.get("cur_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirm_new_password")

        if not cur_password or not new_password or not confirmation:
            return apology("input cannot be blank")
        elif new_password != confirmation:
            return apology("passwords does not match")

        with sqlite3.connect("users.db") as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            row = cur.execute("SELECT * FROM users WHERE id = ?;", (session['user_id'],)).fetchone()
            if not check_password_hash(row['hash'], cur_password):
                return apology("wrong password entered")
            cur.execute("UPDATE users SET hash = ? WHERE id = ?;", (generate_password_hash(new_password), session['user_id']))

        return redirect("/")
    else:
        return render_template("changepassword.html")
    
@app.route("/singlechecker")
@login_required
def singlechecker():
    """Implement a single card price checker"""
    with sqlite3.connect("newcards.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        stores = cur.execute("SELECT DISTINCT store FROM cards;").fetchall()
        stores = [store['store'].title() for store in stores]
    return render_template("singlechecker.html", stores=stores)

@app.route("/deckchecker")
@login_required
def deckchecker():
    """Implement a deck price checker"""
    with sqlite3.connect("newcards.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        stores = cur.execute("SELECT DISTINCT store FROM cards;").fetchall()
        stores = [store['store'].title() for store in stores]
    return render_template("deckchecker.html", stores=stores)

@app.route("/singlesearcher", methods=["POST"])
def singlesearcher():
    if request.method == "POST":
        checked_values = [x.lower() for x in request.form.getlist('checkedValues[]')]
        search_box_value = request.form.get('searchBoxValue')

        with sqlite3.connect("newcards.db") as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            query = "SELECT * FROM cards WHERE name LIKE ? and store IN ({}) ORDER BY price LIMIT 20"
            placeholders = ', '.join(['?' for _ in checked_values])
            query = query.format(placeholders)
            cards = cur.execute(query, ("%" + search_box_value + "%", *checked_values)).fetchall()

        cards_data = [dict(card) for card in cards]
    
        return json.dumps(cards_data)
    
@app.route("/decksearcher", methods=["POST"])
def decksearcher():
    if request.method == "POST":
        checked_values = [store.lower() for store in request.form.getlist('checkedValues[]')]
        textarea = request.form.getlist('textArea[]')
        cards = []
        for element in textarea:
            if len(element) != 0:
                word_list = element.split()
                quantity = int(word_list[0])
                name = ' '.join(word_list[1:])
                temp_dict = {}
                temp_dict['name'] = name
                temp_dict['quantity'] = quantity
                cards.append(temp_dict)
        
        updated_cardlist = []
        with sqlite3.connect("newcards.db") as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            query = "SELECT * FROM cards WHERE name LIKE ? and store IN ({}) ORDER BY price LIMIT 1"
            placeholders = ', '.join(['?' for _ in checked_values])
            query = query.format(placeholders)
            
            for card_dict in cards:
                try:
                    card = dict(cur.execute(query, ("%" + card_dict['name'] + "%", *checked_values)).fetchone())
                    card['quantity'] = card_dict['quantity']
                except TypeError:
                    card = card_dict
                    card['price'] = 0
                    card['store'] = 'Not Available'

                updated_cardlist.append(card)

        return json.dumps(updated_cardlist)
