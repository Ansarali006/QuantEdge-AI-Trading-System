from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


class ForecastRequest(BaseModel):
    symbol: str
    forecast_date: date
    target: Literal["open", "low", "high", "close"]
    horizon: int = Field(ge=1, le=48)


@router.post("/predict")
def predict_forecast(request: ForecastRequest):
    # We will call kronos_service.py here in the next step.
    return {
        "symbol": request.symbol,
        "forecast_date": str(request.forecast_date),
        "target": request.target,
        "horizon": request.horizon,
        "predictions": [],
        "message": "Filters received. Kronos model is not connected yet.",
    }