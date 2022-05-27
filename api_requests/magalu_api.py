from http import HTTPStatus
import os
from uuid import UUID
from api_requests.schema import Item
from api_requests.exception import OrderNotFoundError, CommunicationError

# Httpx é um cliente HTTP completo, com suporte ao protocolo HTTP/2 e provê interface de programação síncrona e
# assíncrona. Utilizado para fazer integração com serviços externos. Funções facilitam a criação de requisições HTTP.
import httpx

# TENANT_ID e APIKEY fixos somente para demonstrações.
APIKEY = os.environ.get("APIKEY", "5734143a-595d-405d-9c97-6c198537108f")
TENANT_ID = os.environ.get("TENANT_ID", "21fea73c-e244-497a-8540-be0d3c583596")
MAGALU_API_URL = "https://alpha.api.magalu.com"
MAESTRO_SERVICE_URL = f"{MAGALU_API_URL}/maestro/v1"

# TODO: Criar testes para funções abaixo.


def _retrieve_items_by_package(order_id, package_id):
    response = httpx.get(
        f"{MAESTRO_SERVICE_URL}/orders/{order_id}/packages/{package_id}/items",
        headers={"X-Api-Key": APIKEY, "X-Tenant-Id": TENANT_ID},
    )
    # Levanta o erro `HTTPStatusError` se algum ocorreu.
    response.raise_for_status()
    return [
        Item(
            sku=item["product"]["code"],
            # Campos que utilizam a função get são opicionais.
            description=item["product"].get("description", ""),
            image_url=item["product"].get("image_url", ""),
            reference=item["product"].get("reference", ""),
            quantity=item["quantity"],
        )
        for item in response.json()
    ]


def mgl_retrieve_items_by_order(order_id: UUID) -> list[Item]:
    try:
        response = httpx.get(
            f"{MAESTRO_SERVICE_URL}/orders/{order_id}",
            headers={"X-Api-Key": APIKEY, "X-Tenant-Id": TENANT_ID},
        )
        response.raise_for_status()
        packages = response.json()["packages"]
        items = []
        for package in packages:
            items.extend(
                _retrieve_items_by_package(order_id, package["uuid"])
            )
        return items
    except httpx.HTTPStatusError as exc:
        # Aqui poderiam ser tratados outros erros como autenticação.
        if exc.response.status_code == HTTPStatus.NOT_FOUND:
            raise OrderNotFoundError() from exc
        raise exc
    except httpx.HTTPError as exc:
        raise CommunicationError() from exc
