import os
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, flash

BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(BASE_DIR, 'giochi.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    """Create tables if they don't exist and seed some example data (if empty)."""
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS giochi (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          nome TEXT NOT NULL,
          numero_giocatori_massimo INTEGER NOT NULL,
          durata_media INTEGER NOT NULL,
          categoria TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS partite (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          gioco_id INTEGER NOT NULL,
          data DATE NOT NULL,
          vincitore TEXT NOT NULL,
          punteggio_vincitore INTEGER NOT NULL,
          FOREIGN KEY (gioco_id) REFERENCES giochi (id)
        );
        """
    )

    cur.execute('SELECT COUNT(*) FROM giochi')
    count = cur.fetchone()[0]
    if count == 0:
        cur.executemany(
            'INSERT INTO giochi (nome, numero_giocatori_massimo, durata_media, categoria) VALUES (?,?,?,?)',
            [
                ('Catan', 4, 90, 'Strategia'),
                ('Dixit', 6, 30, 'Party'),
                ('Ticket to Ride', 5, 60, 'Strategia'),
            ],
        )

        cur.executemany(
            'INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (?,?,?,?)',
            [
                (1, '2023-10-15', 'Alice', 10),
                (1, '2023-10-22', 'Bob', 12),
                (2, '2023-11-05', 'Charlie', 25),
                (3, '2023-11-10', 'Alice', 8),
            ],
        )

    db.commit()
    cur.close()
    db.close()


app = Flask(__name__)
app.config['DATABASE'] = DATABASE
app.secret_key = 'dev-secret-for-local'

@app.route('/')
def home():
    return redirect(url_for('list_giochi'))


@app.route('/giochi')
def list_giochi():
    db = get_db()
    cur = db.execute('SELECT * FROM giochi ORDER BY id')
    giochi = cur.fetchall()
    return render_template('index.html', giochi=giochi)


@app.route('/giochi/new', methods=['GET', 'POST'])
def new_gioco():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        numero = request.form.get('numero_giocatori_massimo')
        durata = request.form.get('durata_media')
        categoria = request.form.get('categoria', '').strip()

        if not nome or not numero or not durata or not categoria:
            flash('Tutti i campi sono obbligatori', 'error')
            return render_template('new_gioco.html')

        db = get_db()
        db.execute(
            'INSERT INTO giochi (nome, numero_giocatori_massimo, durata_media, categoria) VALUES (?,?,?,?)',
            (nome, int(numero), int(durata), categoria),
        )
        db.commit()
        flash('Gioco creato con successo', 'success')
        return redirect(url_for('list_giochi'))

    return render_template('new_gioco.html')


@app.route('/giochi/<int:gioco_id>/partite', methods=['GET', 'POST'])
def gioco_partite(gioco_id):
    db = get_db()
    gioco = db.execute('SELECT * FROM giochi WHERE id = ?', (gioco_id,)).fetchone()
    if gioco is None:
        flash('Gioco non trovato', 'error')
        return redirect(url_for('list_giochi'))

    if request.method == 'POST':
        data = request.form.get('data')
        vincitore = request.form.get('vincitore', '').strip()
        punteggio = request.form.get('punteggio_vincitore')

        if not data or not vincitore or not punteggio:
            flash('Tutti i campi della partita sono obbligatori', 'error')
            return redirect(url_for('gioco_partite', gioco_id=gioco_id))

        db.execute(
            'INSERT INTO partite (gioco_id, data, vincitore, punteggio_vincitore) VALUES (?,?,?,?)',
            (gioco_id, data, vincitore, int(punteggio)),
        )
        db.commit()
        flash('Partita registrata', 'success')
        return redirect(url_for('gioco_partite', gioco_id=gioco_id))

    cur = db.execute('SELECT * FROM partite WHERE gioco_id = ? ORDER BY data DESC', (gioco_id,))
    partite = cur.fetchall()
    return render_template('partite.html', gioco=gioco, partite=partite)


if __name__ == '__main__':
    app.run(debug=True)
