"""Rotas do programa de fidelidade."""
from fastapi import APIRouter, Depends

from app.api.presenters import fidelidade_out
from app.application.services.fidelidade_service import FidelidadeService
from app.core.deps import CurrentUser, get_fidelidade_service
from app.schemas.fidelidade import FidelidadeResponse, ResgateRequest

router = APIRouter(prefix="/fidelidade", tags=["Fidelidade"])


@router.get("/saldo", response_model=FidelidadeResponse, summary="Saldo de pontos")
def saldo(
    user: CurrentUser, service: FidelidadeService = Depends(get_fidelidade_service)
):
    return fidelidade_out(service.saldo(user.get("uid")))


@router.post(
    "/resgatar", response_model=FidelidadeResponse,
    summary="Resgatar pontos (exige consentimento LGPD)",
)
def resgatar(
    payload: ResgateRequest, user: CurrentUser,
    service: FidelidadeService = Depends(get_fidelidade_service),
):
    return fidelidade_out(service.resgatar(user.get("uid"), payload.pontos))
