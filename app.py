'''
Para testar a API é necessário ter um servidor rodando, para isso, utilizei o xampp com o Apache ligado e o MySQL ligado também.
Configurações iniciais: 
Apache (config.inc): 
/* Authentication type and info */
$cfg['Servers'][$i]['auth_type'] = 'config';
$cfg['Servers'][$i]['user'] = 'root';
$cfg['Servers'][$i]['password'] = '';
$cfg['Servers'][$i]['extension'] = 'mysqli';
$cfg['Servers'][$i]['AllowNoPassword'] = true;
$cfg['Lang'] = ''; 

MYSQL (my.ini)
Configuração padrão.

Etapa 1:
Crie o modelo da classe com todos os campos que acreditar que sejam necessários para um
produto, também crie métodos de classe e métodos estáticos (se necessário), para criar ações
como: Criação, Leitura, Atualização e Deleção de um objeto, também podem ser criados métodos que
nos trazem informações interessantes como preço, ou um pequeno aglomerado de informações,
como informações básicas, entre outros.

Etapa 2:
Salve os dados que criou na classe anterior em um banco de dados MongoDB no por meio da
biblioteca PyMongo, adicione os métodos criados anteriormente para fazer as modificações no
banco também.

Etapa 3:
Crie uma API com a biblioteca Flask para as ações anteriores dos métodos por meio de
protocolo HTTP.

'''

# Importando as classes e bibliotecas necessárias para o funcionamento do programa
from flask import Flask, Response, request #Importando a classe flask para criar todas as rotas da API, Response será utilizado para criar o retorno da API e request será utilizado para trabalhar com os dados a serem inseridos no banco de dados.
from flask_sqlalchemy import SQLAlchemy #Classe para tratar com o banco de dados.
import mysql
import mysql.connector #Conector importando para gerar conexão com o MySQL.
import json #Subconjunto utilizado para fornecer um intercâmbio de dados.


# Iniciando o Flask
app = Flask(__name__)
# Configurações dos parametros do banco de dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # Criando a conexão com o banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3309/projeto_freshmania' # Criando a conexão com o banco de dados, chamei de projeto_freshmania
# Estrutura -> mysql://username:password@host:port/database_name

# Iniciando o banco de dados
db = SQLAlchemy(app) #A variável app foi chamada para que o SQLAlchemy funcione em conjunto com o Flask.

# Criando a classe Produto
class Produto(db.Model): #db.Model é uma extensão que utilizará algumas coisas pré definidas da própria extensão.
    id = db.Column(db.Integer, primary_key=True) # ID do produto, chave primária
    nome = db.Column(db.String(80), unique=True, nullable=False) # Nome do produto
    volume = db.Column(db.String(80), unique=True, nullable=False) # Volume do produto em Litros
    tipo = db.Column(db.String(80), unique=True, nullable=False) # Tipo do produto (Caixa de leite ou pacote com varias caixas)
    
    # Criando o método construtor da classe, para traduzir para JSON
    def to_json(self):
        return {"id": id, "nome": self.nome, "volume": self.volume, "tipo": self.tipo}
    
    
    #db.create_all() para criar o banco de dados na primeira vez que rodar o programa

# Funções para cadastrar, listar, atualizar e deletar produtos (CRUD)
# Selecionando todos os produtos
@app.route("/produtos", methods=['GET'])
def seleciona_produtos():
    produtos_objeto = Produto.query.all()
    produtos_json = [produto.to_json() for produto in produtos_objeto]
    print(produtos_json)
    return gera_response(200, "produtos", produtos_json, "Produtos selecionados com sucesso")

# Retorna mensagem de erro ou não
def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    response = {}
    response[nome_do_conteudo] = conteudo
    if mensagem:
        response['mensagem'] = mensagem
    return Response(json.dumps(response), status=status, mimetype='application/json')

# Selecionando um produto especifico
@app.route("/produtos/<int:id>", methods=['GET'])
def seleciona_produto(id):
    produto_objeto = Produto.query.filter_by(id=id).first()
    produto_json = produto_objeto.to_json()
    return gera_response(200, "produto", produto_json, "Produto selecionado com sucesso")

# Inserindo um produto
@app.route("/produtos", methods=['POST'])
def cria_produto():
    body = request.get_json()
    produto = Produto(nome=body['nome'], volume=body['volume'], tipo=body['tipo'])
    db.session.add(produto)
    db.session.commit()
    return gera_response(201, "produto", produto.to_json(), "Produto criado com sucesso")


# Atualizando um produto
@app.route("/produtos/<int:id>", methods=['PUT'])
def atualiza_produto(id):
    produto_objeto = Produto.querry.filter_by(id=id).first()
    body = request.get_json()
    
    try:
        if('nome' in body):
            produto_objeto.nome = body['nome']
        if ('volume' in body):
            produto_objeto.volume = body['volume']
        if ('tipo' in body):
            produto_objeto.tipo = body['tipo']
    except Exception as e:
        print("Erro: ", e)
        return gera_response(400, "produto", {}, "Erro na atualização do produto")
    
# Deletando um produto
@app.route("/produtos/<int:id>", methods=['DELETE'])
def deleta_produto(id):
    produto_objeto = Produto.querry.filter_by(id=id).first()
    
    try:
        db.session.delete(produto_objeto)
        db.session.commit()
        return gera_response(200, "produto", produto_objeto.to_json(), "Produto deletado com sucesso")
    except Exception as e:
        print("Erro: ", e)
        return gera_response(400, "produto", {}, "Erro ao deletar o produto")

app.run() #para rodar o programa, chamando a função run
