# Pydantic é um framework para validação de dados e gerenciamento de configurações. Facilita a identificação de erros.
# Já possui integração com o FastAPI e é uma das ferramentas mais poderosas disponível.
from pydantic import BaseModel


# Esquema que será retornado no corpo da requisição
class Item(BaseModel):
    sku: str
    description: str
    image_url: str
    reference: str
    quantity: int
