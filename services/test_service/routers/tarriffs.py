import decimal
import json

from fastapi import (
    APIRouter,
    Depends
)
import logging
from fastapi.responses import JSONResponse
from misc.handlers import (
    error_404,
    error_400
)

from models.tariffs import (
    Tariff,
    CargoType,
    Cost,
    CostSuccessResponse,
    TariffSuccessResponse
)
from datetime import date
from misc.enums import DeclaredTypesEnum
from misc.encoders import DecimalEncoder

router = APIRouter(
    prefix='/products',
    tags=['products']
)

logger = logging.getLogger(__name__)


@router.post(
    '/',
    name='set_tariff'
)
async def set_tariff(
        tariff: dict
) -> TariffSuccessResponse | JSONResponse:
    await Tariff.all().delete()  # Чтобы упростить задачу, просто очистим БД от предыдущих тарифов
    await CargoType.all().delete()

    # Создаем из входящего JSON тарифы
    for tariff_date, cargo_types in tariff.items():
        cur_tariff = await Tariff.create(date=tariff_date)

        for cargo_type in cargo_types:
            await CargoType.create(**cargo_type, tariff=cur_tariff)

    tariffs = await Tariff.all().prefetch_related('cargos')
    tariffs_json = [{str(i.date): [dict(j) for j in await i.cargos.all()]} for i in tariffs]
    tariffs_json = json.loads(json.dumps(tariffs_json, cls=DecimalEncoder))

    return TariffSuccessResponse(data=tariffs_json)


@router.get(
    '/',
    name='get_cost',
    response_model=CostSuccessResponse
)
async def get_cost(
        declared_value: int,
        declared_type: DeclaredTypesEnum,
        declared_date: date
) -> CostSuccessResponse | JSONResponse:
    tariff = await Tariff.filter(date__lt=declared_date).order_by('-date').first().prefetch_related('cargos')
    if not tariff:
        return await error_404('Tariff not found')

    cargo_type = await tariff.cargos.filter(cargo_type=declared_type.value).first()
    if not cargo_type:
        return await error_404('Cargo type in tariff not found')

    result = Cost(total=decimal.Decimal(cargo_type.rate) * declared_value)
    return CostSuccessResponse(data=result)
