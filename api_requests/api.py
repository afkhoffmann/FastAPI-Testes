# Uvicorn é um servidor de aplicação com suporte a frameworks assíncronos, utilizado para rodar a aplicação tanto
# na máquina quanto em um servidor de internet.
import uvicorn
# FastAPI é uma ferramenta para desenvolvimento web, possui funções que auxiliam operações de roteamento, tratamento de
# requisições, renderização de conteúdo, gerenciamento de sessão e cookies, entre outros.
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
# Httpie (http) é um cliente HTTP por linha de comando, usado para fazer testes de maneira simples.
from http import HTTPStatus
from uuid import UUID
from api_requests.exception import OrderNotFoundError, CommunicationError
from api_requests.schema import Item


app = FastAPI()


def retrieve_items_by_order(order_id: UUID) -> list[Item]:
    pass


# Registro do endpoint /healthcheck
@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

# Cria uma injeção de dependência na rota abaixo. Permite mudar o recuperador de itens para um dublê nos testes e mudar
# a maneira utilizada para recuperar os itens de um pedido sem precisar modificar todos os lugares que dependem da
# função de recuperação de itens.
@app.get("/orders/{order_id}/items")
def list_items(items: list[Item] = Depends(retrieve_items_by_order)):
    return items


@app.exception_handler(OrderNotFoundError)
def handle_order_not_found_error(request: Request, exc: OrderNotFoundError):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"message": "Order not found"},
    )


@app.exception_handler(CommunicationError)
def handle_communication_error(request: Request, exc: CommunicationError):
    return JSONResponse(
        status_code=HTTPStatus.BAD_GATEWAY,
        content={"message": "Error communicating with the external service"},
    )


# Inicia uvicorn direto da aplicação. "reload=True" atualiza a aplicação durante a execução sempre que houver alteração
# no código.
def start():
    uvicorn.run("api_requests.api:app", host="0.0.0.0", port=8001, reload=True)


if __name__ == "__main__":
    start()
