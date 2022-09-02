#!/usr/bin/env python
"""
 Este projeto é apenas um modelo simples de CRUD com FASTAPI com ODM em Mongo
"""
__author__ = "Vítor Silvério Rodrigues"
__email__ = "vitor.silverio.rodrigues@gmail.com"

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from odmantic import AIOEngine, Model, EmbeddedModel, ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
from datetime import datetime
from typing import List, Optional


def copy_attributes(src: Model, dest: Model):
    for key, value in src.dict().items():
        if key == "id":
            continue
        setattr(dest, key, value)


class Cliente(EmbeddedModel):
    nome: str
    documento: Optional[str]


class Servico(EmbeddedModel):
    descricao: str
    valor_unitario: float
    quantidade: float


class Orcamento(Model):
    numero: str
    cliente: Cliente
    servicos: List[Servico]
    validade: datetime
    observacao: Optional[str]

    class Config:
        json_encoders = {datetime: lambda v: v.timestamp()}


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_client = AsyncIOMotorClient(config("MONGO_URL"))
engine = AIOEngine(client=mongo_client, database="sistemaorcamentos")


@app.get("/")
def root():
    return {"message": "It works"}


@app.post("/orcamento")
async def criar_rocamento(orcamento: Orcamento) -> Orcamento:
    await engine.save(orcamento)
    return orcamento


@app.get("/orcamento")
async def get_orcamentos() -> List[Orcamento]:
    return await engine.find(Orcamento)


@app.put("/orcamento/{id}")
async def update_orcamentos(id: ObjectId, orcamento: Orcamento) -> Orcamento:
    old_orcamento = await engine.find_one(Orcamento, Orcamento.id == id)
    if not old_orcamento:
        raise HTTPException(status_code=404)
    copy_attributes(orcamento, old_orcamento)
    await engine.save(old_orcamento)
    return old_orcamento


@app.delete("/orcamento/{id}")
async def delete_orcamento(id: ObjectId) -> Response:
    orcamento = await engine.find_one(Orcamento, Orcamento.id == id)
    if not orcamento:
        raise HTTPException(status_code=404)
    await engine.delete(orcamento)
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app")
