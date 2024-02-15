from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from shared.database import Base
from shared.dependencies import get_db

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False})

TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_listar_contas_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    client.post('/contas-a-pagar-e-receber/',json={'descricao': 'Conta a Pagar','valor': 101.1,'tipo': 'PAGAR', })
    client.post('/contas-a-pagar-e-receber/', json={'descricao': 'Conta a Receber', 'valor': 101.1,'tipo': 'PAGAR'})

    response = client.get('/contas-a-pagar-e-receber/')
    assert response.status_code == 200
    print(response.json())
    assert response.json() == [
        {'descricao': 'Conta a Pagar', 'id': 1, 'tipo': 'PAGAR', 'valor': 101.1,'fornecedor': None},
        {'descricao': 'Conta a Receber', 'id': 2, 'tipo': 'PAGAR', 'valor': 101.1,'fornecedor': None}
    ]


def test_criar_conta_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    nova_conta = {
        'descricao': 'Conta a Pagar',
        'valor': 100.0000000000,
        'tipo': 'PAGAR',
        'fornecedor': None
    }

    nova_conta_copy = nova_conta.copy()
    nova_conta_copy['id'] = 1

    response = client.post('/contas-a-pagar-e-receber/', json=nova_conta)
    print(response.json())
    assert response.status_code == 201
    assert response.json() == nova_conta_copy


def test_deve_retornar_erro_quando_exceder_a_descricao():
    response = client.post('contas-a-pagar-e-receber',json={
        'descricao': 'Teste erro que não funciona no SQLite',
        'valor': 100,
        'tipo': 'PAGAR'
    })

    assert response.status_code == 422

def test_deve_retornar_erro_quando_o_valor_for_zero_ou_menor():
    response = client.post('contas-a-pagar-e-receber', json={
        'descricao': 'Teste erro que não funciona no SQLite',
        'valor': 0,
        'tipo': 'PAGAR'
    })

    assert response.status_code == 422

    response = client.post('contas-a-pagar-e-receber', json={
        'descricao': 'Teste erro que não funciona no SQLite',
        'valor': -1,
        'tipo': 'PAGAR'
    })

    assert response.status_code == 422

def test_deve_retornar_erro_quando_o_tipo_for_invalido():
    response = client.post('contas-a-pagar-e-receber', json={
        'descricao': 'Teste erro que não funciona no SQLite',
        'valor': 100,
        'tipo': 'INVALIDO'
    })

    assert response.status_code == 422

def test_atualizar_conta_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    nova_conta = {
        'descricao': 'Conta a Pagar',
        'valor': 100,
        'tipo': 'PAGAR'
    }

    response = client.post('/contas-a-pagar-e-receber/', json=nova_conta)

    id_conta_a_pagar = response.json()['id']

    conta_atualizada = {
        'descricao': 'Conta a Pagar',
        'valor': 222,
        'tipo': 'PAGAR'
    }
    response_put = client.put(f'/contas-a-pagar-e-receber/{id_conta_a_pagar}', json=conta_atualizada)

    assert response_put.status_code == 200


def test_delete_conta_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    nova_conta = {
        'descricao': 'Conta a Pagar',
        'valor': 100,
        'tipo': 'PAGAR'
    }

    response = client.post('/contas-a-pagar-e-receber/', json=nova_conta)

    id_conta_a_pagar = response.json()['id']

    response_delete = client.delete(f'/contas-a-pagar-e-receber/{id_conta_a_pagar}')
    assert response_delete.status_code == 204

def test_deve_retornar_nao_encontrado_para_id_nao_existente():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response = client.get('/contas-a-pagar-e-receber/100')
    assert response.status_code == 404


def test_deve_retornar_nao_encontrado_para_id_nao_existente_na_atualizacao():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    conta_atualizada = {
        'descricao': 'Conta a Pagar',
        'valor': 222,
        'tipo': 'PAGAR'
    }
    response_put = client.put(f'/contas-a-pagar-e-receber/1100', json=conta_atualizada)
    assert response_put.status_code == 404


def test_deve_retornar_nao_encontrado_para_id_nao_existente_na_delecao():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response = client.delete('/contas-a-pagar-e-receber/100')
    assert response.status_code == 404


def test_criar_conta_a_pagar_e_receber_com_fornecedor():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    novo_fornecedor_cliente = {
        'nome' : "Casa do Musico"
    }

    client.post('/fornecedor-cliente', json=novo_fornecedor_cliente)


    nova_conta = {
        'descricao': 'Conta a Pagar',
        'valor': 100.0000000000,
        'tipo': 'PAGAR',
        'fornecedor_cliente_id': 1
    }

    nova_conta_copy = nova_conta.copy()
    nova_conta_copy['id'] = 1
    nova_conta_copy['fornecedor'] = {
        'id' : 1,
        'nome' : 'Casa do Musico'
    }

    del nova_conta_copy['fornecedor_cliente_id']

    response = client.post('/contas-a-pagar-e-receber/', json=nova_conta)
    print(response.json())
    assert response.status_code == 201
    assert response.json() == nova_conta_copy

def test_deve_retornar_erro_ao_inserir_uma_nova_conta_com_fornecedor_invalido():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    nova_conta = {
        'descricao': 'Conta a Pagar',
        'valor': 100.0000000000,
        'tipo': 'PAGAR',
        'fornecedor_cliente_id': 1111
    }

    response = client.post('/contas-a-pagar-e-receber/', json=nova_conta)
    assert response.status_code == 422

