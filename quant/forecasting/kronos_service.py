from datetime import date
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from quant.forecasting.kronos_service import predict
print("LOADED FORECASTS ROUTE FILE", flush=True)

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


class ForecastRequest(BaseModel):
    symbol: str
    forecast_date: date
    target: Literal["open", "low", "high", "close"]
    horizon: int = Field(ge=1, le=48)


@router.post("/predict")
def predict_forecast(request: ForecastRequest):
    print("TEST: FORECAST ROUTE WAS CALLED", flush=True)
    print("FORECAST ROUTE FUNCTION CALLED", flush=True)

    result = predict(
        symbol=request.symbol,
        forecast_date=request.forecast_date,
        target=request.target,
        horizon=request.horizon,
    )

    print("FORECAST RESULT:", repr(result), flush=True)
    return result