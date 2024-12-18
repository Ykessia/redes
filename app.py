from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey'

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Página inicial - redireciona para login ou dashboard
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

# Página de cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha_hash))
        conn.commit()
        conn.close()
        flash('Cadastro realizado com sucesso!')
        return redirect('/login')
    return render_template('register.html')

# Página de login com mensagem de erro para usuário não cadastrado
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            if check_password_hash(user['senha'], senha):
                session['user_id'] = user['id']
                session['nome'] = user['nome']
                return redirect('/dashboard')
            else:
                flash('Senha incorreta')
        else:
            flash('Usuário não cadastrado')  # Mensagem de erro para usuário não cadastrado
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Página de tarefas (dashboard) com opções de filtragem
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = session['user_id']
    
    # Filtros para status, data de criação, prazo, prioridade, descrição e categoria
    filtro_status = request.args.get('status')
    filtro_data_criacao = request.args.get('data_criacao')
    filtro_prazo = request.args.get('data_limite')
    filtro_prioridade = request.args.get('prioridade')
    filtro_descricao = request.args.get('descricao')
    filtro_categoria = request.args.get('categoria')

    query = 'SELECT * FROM tasks WHERE user_id = ?'
    params = [user_id]

    if filtro_status:
        query += ' AND status = ?'
        params.append(filtro_status)

    if filtro_data_criacao:
        query += ' AND data_criacao >= ?'
        params.append(filtro_data_criacao)

    if filtro_prazo:
        query += ' AND data_limite <= ?'
        params.append(filtro_prazo)

    if filtro_prioridade:
        query += ' AND prioridade = ?'
        params.append(filtro_prioridade)

    if filtro_descricao:
        query += ' AND descricao LIKE ?'
        params.append(f'%{filtro_descricao}%')

    if filtro_categoria:
        query += ' AND categoria = ?'
        params.append(filtro_categoria)

    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', tasks=tasks)

# Página de adicionar tarefa
@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        descricao = request.form['descricao']
        data_limite = request.form['data_limite']
        prioridade = request.form['prioridade']
        categoria = request.form['categoria']
        user_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (descricao, data_criacao, data_limite, status, prioridade, categoria, user_id) VALUES (?, ?, ?, "Pendente", ?, ?, ?)',
                       (descricao, datetime.now(), data_limite, prioridade, categoria, user_id))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    return render_template('add_task.html')

# Página de editar tarefa
@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (id, session['user_id']))
    task = cursor.fetchone()

    if request.method == 'POST':
        descricao = request.form['descricao']
        status = request.form['status']
        data_limite = request.form['data_limite']
        prioridade = request.form['prioridade']
        categoria = request.form['categoria']

        cursor.execute('UPDATE tasks SET descricao = ?, status = ?, data_limite = ?, prioridade = ?, categoria = ? WHERE id = ?',
                       (descricao, status, data_limite, prioridade, categoria, id))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    conn.close()
    return render_template('edit_task.html', task=task)

# Excluir tarefa
@app.route('/delete_task/<int:id>')
def delete_task(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
