from itertools import count
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from typing import Optional


server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='API de registro')
spec.register(server)
datebase = TinyDB('datebase.json')
c = count()



class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda:next(c))
    nome: str
    idade: int


class Pessoas(BaseModel):
    pessoas: list[Pessoa]
    count: int


@server.get('/pessoas')
@spec.validate(resp=Response(HTTP_200=Pessoas))
def buscar_pessoas():
    """"Retorna todas as Pessoas da sua base de dados"""
    return jsonify(
        Pessoas(
            pessoas=datebase.all(),
            count=len(datebase.all())
        ).dict()
    )


@server.get('/pessoas/<int:id>')
@spec.validate(resp=Response(HTTP_200=Pessoa))
def buscar_pessoa(id):
    try:
        pessoa = datebase.search(Query().id==id)[0]
    except IndexError:
        return {'message': 'Pessoa not found!'}, 404
    return jsonify(pessoa)


@server.post('/pessoas')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_201=Pessoa))
def inserir_pessoa():
    """Insere uma Pessoa no banco de dados"""
    body = request.context.body.dict()
    datebase.insert(body)
    return body


@server.put('/pessoas/<int:id>')
@spec.validate(
    body=Request(Pessoa), resp=Response(HTTP_200=Pessoas)
)
def altera_pessoa(id):
    """"Altera uma pessoa do banco de dados"""
    Pessoa = Query()
    body=request.context.body.dict()
    datebase.update(body, Pessoa.id == id)
    return jsonify(body)


@server.delete('/pessoas/<int:id>')
@spec.validate(resp=Response('HTTP_204'))
def deleta_pessoa(id):
    """"Deleta uma Pessoa do banco de dados"""
    datebase.remove(Query().id == id)
    return jsonify({})


server.run()