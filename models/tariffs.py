from pydantic import BaseModel
from decimal import Decimal
from models.base import SuccessResponse
from tortoise.models import Model
from tortoise import fields


class Tariff(Model):
    id = fields.IntField(pk=True)
    date = fields.DateField()


class CargoType(Model):
    cargo_type = fields.CharField(255)
    rate = fields.DecimalField(5, 3)
    tariff = fields.ForeignKeyField('models.Tariff', 'cargos', on_delete=fields.CASCADE)


class Cost(BaseModel):
    total: Decimal


class CostSuccessResponse(SuccessResponse):
    data: Cost


class TariffSuccessResponse(SuccessResponse):
    data: list[dict]
