from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.conta_a_pagar_receber_model import ContaPagarReceber
from contas_a_pagar_e_receber.models.fornecedor_cliente_model import FornecedorCliente
from contas_a_pagar_e_receber.routers.fornecedor_cliente_router import FornecedorClienteResponse
from shared.dependencies import get_db
from shared.exceptions import NotFound

router = APIRouter(prefix="/contas-a-pagar-e-receber")


class ContasPagarReceberResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    tipo: str
    fornecedor: FornecedorClienteResponse | None = None
    data_baixa : datetime | None = None
    valor_baixa : Decimal | None = None
    esta_baixada : bool | None = None

    class Config:
        orm_mode = True


class ContaPagarReceberTipoEnum(str, Enum):
    PAGAR = 'PAGAR'
    RECEBER = 'RECEBER'


class ContasPagarReceberRequest(BaseModel):
    descricao: str = Field(min_length=3, max_length=30)
    valor: Decimal = Field(gt=0)
    tipo: ContaPagarReceberTipoEnum
    fornecedor_cliente_id: int | None = None


@router.get('/', response_model=List[ContasPagarReceberResponse])
def listar_contas(db: Session = Depends(get_db)) -> List[ContasPagarReceberResponse]:
    return db.query(ContaPagarReceber).all()


@router.get('/{id_conta}', response_model=ContasPagarReceberResponse)
def listar_conta(id_conta: int,
                 db: Session = Depends(get_db)) -> List[ContasPagarReceberResponse]:
    conta_a_pagar_receber: ContaPagarReceber = busca_conta_por_id(id_conta, db)
    return conta_a_pagar_receber


@router.post('/', response_model=ContasPagarReceberResponse, status_code=201)
def criar_conta(conta: ContasPagarReceberRequest, db: Session = Depends(get_db)) -> ContasPagarReceberResponse:
    valida_fornecedor(conta.fornecedor_cliente_id, db)

    contas_a_pagar_e_receber = ContaPagarReceber(descricao=conta.descricao,
                                                 valor=conta.valor,
                                                 tipo=conta.tipo,
                                                 fornecedor_cliente_id=conta.fornecedor_cliente_id)

    db.add(contas_a_pagar_e_receber)
    db.commit()
    db.refresh(contas_a_pagar_e_receber)

    return contas_a_pagar_e_receber


@router.put('/{id}', response_model=ContasPagarReceberResponse, status_code=200)
def atualizar_conta(id: int,
                    conta: ContasPagarReceberRequest, db: Session = Depends(get_db)):
    valida_fornecedor(conta.fornecedor_cliente_id, db)

    conta_atualizada = busca_conta_por_id(id, db)
    conta_atualizada.descricao = conta.descricao
    conta_atualizada.valor = conta.valor
    conta_atualizada.tipo = conta.tipo

    db.add(conta_atualizada)
    db.commit()
    db.refresh(conta_atualizada)

    return conta_atualizada


@router.post('/{id}/baixar', response_model=ContasPagarReceberResponse, status_code=200)
def baixar_conta(id: int,
                 db: Session = Depends(get_db)):

    conta_atualizada = busca_conta_por_id(id, db)

    if (conta_atualizada.esta_baixada and conta_atualizada.valor != conta_atualizada.valor_baixa):
        return conta_atualizada

    conta_atualizada.data_baixa = datetime.now()
    conta_atualizada.esta_baixada = True
    conta_atualizada.valor_baixa = conta_atualizada.valor

    db.add(conta_atualizada)
    db.commit()
    db.refresh(conta_atualizada)

    return conta_atualizada


@router.delete('/{id}', status_code=204)
def delete_conta(id: int, db: Session = Depends(get_db)):
    contas_a_pagar_e_receber = busca_conta_por_id(id, db)
    db.delete(contas_a_pagar_e_receber)
    db.commit()


def busca_conta_por_id(id_da_conta_a_pagar_e_receber: int, db: Session) -> ContaPagarReceber:
    conta_a_pagar_e_receber = db.query(ContaPagarReceber).get(id_da_conta_a_pagar_e_receber)

    if not conta_a_pagar_e_receber:
        raise NotFound("Conta")

    return conta_a_pagar_e_receber


def valida_fornecedor(fornecedor_cliente_id, db):
    if fornecedor_cliente_id is not None:
        contas_a_pagar_e_receber = db.query(FornecedorCliente).get(fornecedor_cliente_id)
        if contas_a_pagar_e_receber is None:
            raise HTTPException(status_code=422, detail="Fornecedor Cliente não encontrado")
