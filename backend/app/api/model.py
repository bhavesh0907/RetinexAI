from fastapi import APIRouter

router = APIRouter(tags=["Model"])


@router.get("/info")
def info():
    return {"model": "resnet50"}


@router.get("/version")
def version():
    return {"version": "1.0"}