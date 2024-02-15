from fastapi import FastAPI,Request
import uvicorn
from contas_a_pagar_e_receber.routers import contas_a_pagar_e_receber_router, fornecedor_cliente_router
from shared.database import engine,Base
from shared.exceptions import NotFound
from shared.exceptions_handler import not_found_exception_handler

# from contas_a_pagar_e_receber.models.conta_a_pagar_receber_model import ContaPagarReceber
#
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine) # Criação da database/tabelas ao iniciar o programa
app = FastAPI()


@app.get("/")
def hello_world():
    return "Hello, world"


app.include_router(contas_a_pagar_e_receber_router.router)
app.include_router(fornecedor_cliente_router.router)
app.add_exception_handler(NotFound,not_found_exception_handler)
if __name__ == "__main__":
    uvicorn.run(app, port=8000)
