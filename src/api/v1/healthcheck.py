from fastapi import APIRouter, Depends, Request, status


router = APIRouter()


@router.get("/check")
async def health_check(request: Request):
    return {"status": "ok"}
