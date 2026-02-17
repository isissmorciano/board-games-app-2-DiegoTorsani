import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, flash
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['DATABASE'] = os.path.join(BASE_DIR, 'board_games.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_path = app.config.get('DATABASE')
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return redirect(url_for('lista_giochi'))


@app.route('/giochi', methods=['GET', 'POST'])
def lista_giochi():
    db = get_db()
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        try:
            numero = int(request.form.get('numero_giocatori_massimo') or 0)
        except ValueError:
            numero = 0
        try:
            durata = int(request.form.get('durata_media') or 0)
        except ValueError:
            durata = 0
        categoria = request.form.get('categoria', '').strip()
        if not nome or not categoria:
            flash('Nome e categoria sono obbligatori', 'warning')
        else:
            db.execute(
                'INSERT INTO giochi (nome, numero_giocatori_massimo, durata_media, categoria) VALUES (?,?,?,?)',
                (nome, numero, durata, categoria),
            )
            db.commit()
            return redirect(url_for('lista_giochi'))

    cur = db.execute('SELECT * FROM giochi ORDER BY id')
    giochi = cur.fetchall()
    return render_template('games.html', giochi=giochi)


@app.route('/giochi/<int:gioco_id>/partite', methods=['GET', 'POST'])
def partite_gioco(gioco_id):
    db = get_db()
    gioco = db.execute('SELECT * FROM giochi WHERE id = ?', (gioco_id,)).fetchone()
    if gioco is None:
        flash('Gioco non trovato', 'danger')
        return redirect(url_for('lista_giochi'))

    if request.method == 'POST':
        data = request.form.get('data', '').strip()
        vincitore = request.form.get('vincitore', '').strip()
        try:
            punteggio = int(request.form.get('punteggio_vincitore') or 0)
        except ValueError:
            punteggio = 0

        if not data or not vincitore:
            flash('Data e vincitore sono obbligatori', 'warning')
        else:
            db.execute(
                'INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (?,?,?,?)',
                (gioco_id, data, vincitore, punteggio),
            )
            db.commit()
            return redirect(url_for('partite_gioco', gioco_id=gioco_id))

    cur = db.execute('SELECT * FROM partite WHERE gioco_id = ? ORDER BY data DESC', (gioco_id,))
    partite = cur.fetchall()
    return render_template('game_partite.html', gioco=gioco, partite=partite)


if __name__ == '__main__':
    app.run(debug=True)
