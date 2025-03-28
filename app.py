from flask import Flask, request, jsonify, render_template 
import sqlite3
from flask_cors import CORS


app = Flask(__name__) #cria uma instância da aplicação Flask
CORS(app)

def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS livros(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     titulo TEXT NOT NULL,
                     categoria TEXT NOT NULL,
                     autor TEXT NOT NULL,
                     imagem_url TEXT NOT NULL
                     )
                     """)
        print("Banco de dados inicalizado com sucesso!!")

init_db()

@app.route('/')
def homepage():
    return render_template("index.html")


@app.route('/doar', methods=['POST'])
def doar():
    dados = request.get_json()

    titulo = dados.get("titulo")
    categoria = dados.get("categoria")
    autor = dados.get("autor")
    imagem_url = dados.get("imagem_url")

    if not all([titulo, categoria, autor,imagem_url]):
        return jsonify({'erro':'Todos os campos são obrigatórios'}), 400

    with sqlite3.connect('database.db') as conn:
        conn.execute("""
        INSERT INTO livros(titulo,categoria,autor,imagem_url) VALUES(?, ?, ?, ?)

                    """,(titulo,categoria,autor,imagem_url))
        conn.commit()
        
        return jsonify({'mensagem':'Livros Cadastrados Com Sucesso!!'}), 201

@app.route('/livros',methods=['GET'])
def listarLivros():
    # livro_atualizado = request.get_json()
    with sqlite3.connect('database.db') as conn:
        livros = conn.execute("SELECT * FROM livros").fetchall()

    livrosFormatados = []

    for livro in livros:
        dicionarioLivros = {
            "id": livro[0],
            "titulo": livro[1],
            "categoria": livro[2],
            "autor": livro[3],
            "imagem_url": livro[4]
        }
        livrosFormatados.append(dicionarioLivros)
    

    return jsonify(livrosFormatados)

@app.route('/livros/<int:livro_id>', methods=['PUT'])
def atualizarLivros(livro_id):
    livro_atualizado = request.get_json()

    if not livro_atualizado:
        return jsonify({"error": "Dados inválidos ou ausentes"}), 400

    titulo = livro_atualizado.get('titulo')
    categoria = livro_atualizado.get('categoria')
    autor = livro_atualizado.get('autor')
    imagem_url = livro_atualizado.get('imagem_url')

    if not all([titulo, categoria, autor, imagem_url]):
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400

    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livros WHERE id = ?", (livro_id,))
            livro_existente = cursor.fetchone()

            if not livro_existente:
                return jsonify({"erro": "Livro não encontrado"}), 404

            cursor.execute("""
                UPDATE livros 
                SET titulo = ?, categoria = ?, autor = ?, imagem_url = ?
                WHERE id = ?
            """, (titulo, categoria, autor, imagem_url, livro_id))
            conn.commit()

    except sqlite3.Error as e:
        return jsonify({"erro": f"Erro no banco de dados: {str(e)}"}), 500

    return jsonify({
        "message": "Livro atualizado com sucesso!",
        "livro": {
            "id": livro_id,
            "titulo": titulo,
            "categoria": categoria,
            "autor": autor,
            "imagem_url": imagem_url
        }
    }), 200


@app.route('/livros/<int:livro_id>', methods=['DELETE'])
def deletar_livro(livro_id):
    # Conecta ao banco de dados e cria um cursor para executar comandos SQL.
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        # Executa a exclusão do livro com o ID especificado.
        cursor.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
        # Confirma a transação para salvar as mudanças.
        conn.commit()

    # Verifica se algum registro foi afetado (se o livro foi encontrado e excluído).
    if cursor.rowcount == 0:
        # Retorna um erro 400 (Bad Request) se o livro não foi encontrado.
        return jsonify({"erro": "Livro não encontrado"}), 400

    # Retorna uma mensagem de sucesso com o código 200 (OK).
    return jsonify({"menssagem": "Livro excluído com sucesso"}), 200





if __name__ == "__main__":
    app.run(debug=True)



    




