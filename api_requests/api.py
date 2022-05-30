# isort é uma ferramenta que ordena de forma alfabética as importações,
# separando as bilbiotecas que são padrões da linguagem, as externas ao
# sistema e as nativas do próprio sistema. O isort irá modificar o seu
# código ordenando as importações alfabéticamente. Dessa forma, o bloco
# de importações fica organizado e padronizado no projeto.

# O black é um formatador automático de código, ele irá modificar o seu
# código seguindo o guia de estilo do Python.

# Httpie (http) é um cliente HTTP por linha de comando, usado para fazer
# testes de maneira simples.
from http import HTTPStatus
from uuid import UUID

# Uvicorn é um servidor de aplicação com suporte a frameworks assíncronos,
# utilizado para rodar a aplicação tanto na máquina quanto em um servidor
# de internet.
import uvicorn

# FastAPI é uma ferramenta para desenvolvimento web, possui funções que
# auxiliam operações de roteamento, tratamento de requisições, renderização
# de conteúdo, gerenciamento de sessão e cookies, entre outros.
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from api_requests.exception import CommunicationError, OrderNotFoundError
from api_requests.magalu_api import mgl_retrieve_items_by_order
from api_requests.schema import ErrorResponse, HealthCheckResponse, Item

app = FastAPI()


def retrieve_items_by_order(order_id: UUID) -> list[Item]:
    return mgl_retrieve_items_by_order(order_id)


# Registro do endpoint /healthcheck na tag "healthcheck"
@app.get(
    "/healthcheck",
    tags=["healthcheck"],
    summary="Integridade do sistema",
    response_model=HealthCheckResponse,
    description="Verifica a integridade do sistema",
)
async def healthcheck():
    return {"status": "ok"}


# Cria uma injeção de dependência na rota abaixo. Permite mudar o
# recuperador de itens para um dublê nos testes e mudar a maneira utilizada
# para recuperar os itens de um pedido sem precisar modificar todos os
# lugares que dependem da função de recuperação de itens.
@app.get(
    "/orders/{order_id}/items",
    tags=["orders"],
    summary="Itens de um pedido",
    response_model=list[Item],
    description="Retorna todos os itens de um determinado pedido",
    responses={
        HTTPStatus.NOT_FOUND.value: {
            "description": "Pedido não encontrado",
            "model": ErrorResponse,
        },
        HTTPStatus.BAD_GATEWAY.value: {
            "description": "Falha de comunicação com o servidor remoto",
            "model": ErrorResponse,
        },
    },
)
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


# Inicia uvicorn direto da aplicação. "reload=True" atualiza a aplicação
# durante a execução sempre que houver alteração no código.
def start():
    uvicorn.run("api_requests.api:app", host="0.0.0.0", port=8001, reload=True)


if __name__ == "__main__":
    start()
