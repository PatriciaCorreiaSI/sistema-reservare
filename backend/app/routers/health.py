from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health verifica se a API está em execução.
    """
    return {"status": "healthy"}
