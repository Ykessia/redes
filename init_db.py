import sqlite3

conn = sqlite3.connect('database.db')

# Criar tabelas
conn.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL
);
''')

conn.execute('''
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    data_criacao TEXT NOT NULL,
    data_limite TEXT,
    status TEXT NOT NULL,
    prioridade TEXT,
    categoria TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
''')

conn.close()
print("Banco de dados inicializado com sucesso!")
