# O Desenvolvimento Guiado por Testes (Test Driven Development - TDD) é uma
# técnica de desenvolvimento de software que baseia em um ciclo curto de
# repetições: escrever um caso de teste automatizado que define uma melhoria
# desejada ou nova funcionalidade; produzir um código que possa ser validade
# pelo teste para posteriormente o código ser refatorado para um código sob
# padrões aceitáveis.

# Escrever testes antes do código ajuda no planejamento da arquitetura da
# aplicação, e os testes podem ser um guia de como a aplicação deve se
# comportar.

# python -m pytest tests

from http import HTTPStatus
from uuid import UUID

# Pytest é um framework para escrever testes simples ou funcionais complexos.
import pytest
from fastapi.testclient import TestClient

from api_requests.api import app, retrieve_items_by_order
from api_requests.exception import CommunicationError, OrderNotFoundError
from api_requests.schema import Item


# Cria a fixture client, usada para testar consistentemente algum item
@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def override_retrieve_items_by_order():
    def _override_retrieve_items_by_order(items_or_error):
        def stuntman(order_id: UUID) -> list[Item]:
            if isinstance(items_or_error, Exception):
                raise items_or_error
            return items_or_error

        app.dependency_overrides[retrieve_items_by_order] = stuntman

    yield _override_retrieve_items_by_order
    app.dependency_overrides.clear()


# Classe para testar a integridade do sistema
class TestHealthCheck:
    def test_return_code_must_be_status_200(self, client):
        response = client.get("/healthcheck")
        assert response.status_code == HTTPStatus.OK

    def test_return_format_must_be_json(self, client):
        response = client.get("/healthcheck")
        assert response.headers["Content-Type"] == "application/json"

    def test_must_have_information(self, client):
        response = client.get("/healthcheck")
        assert response.json() == {"status": "ok"}


# Agrupamento de testes para facilitar a leitura
class TestListOrders:
    def test_invalid_order_id_must_return_error_message(self, client):
        response = client.get("/orders/invalid-value/items")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_order_id_not_found_return_error_message(
            self, client, override_retrieve_items_by_order
    ):
        override_retrieve_items_by_order(OrderNotFoundError())
        response = client.get(
            "/orders/ea78b59b-885d-4e7b-9cd0-d54acadb4933/items"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_order_id_found_must_return_status_ok(
            self, client, override_retrieve_items_by_order
    ):
        override_retrieve_items_by_order([])
        response = client.get(
            "/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items"
        )
        assert response.status_code == HTTPStatus.OK

    def test_order_id_found_must_return_items(
            self, client, override_retrieve_items_by_order
    ):
        order_items = [
            Item(
                sku="1",
                description="Item 1",
                image_url="http://url.com/img1",
                reference="ref1",
                quantity=1,
            ),
            Item(
                sku="2",
                description="Item 2",
                image_url="http://url.com/img2",
                reference="ref2",
                quantity=2,
            ),
        ]
        override_retrieve_items_by_order(order_items)
        response = client.get(
            "/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items")
        assert response.json() == order_items

    def test_order_source_fail_must_return_error_message(
            self, client, override_retrieve_items_by_order
    ):
        override_retrieve_items_by_order(CommunicationError())
        response = client.get(
            "/orders/ea78b59b-885d-4e7b-9cd0-d54acadb4933/items")
        assert response.status_code == HTTPStatus.BAD_GATEWAY
