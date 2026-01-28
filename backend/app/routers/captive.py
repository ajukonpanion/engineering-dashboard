from fastapi import APIRouter
from fastapi.responses import RedirectResponse, PlainTextResponse

router = APIRouter(tags=["captive"])

# Android captive check
@router.get("/generate_204")
def android_204():
    return RedirectResponse(url="/", status_code=302)

# Some Android variants
@router.get("/gen_204")
def android_gen_204():
    return RedirectResponse(url="/", status_code=302)

# Apple captive check
@router.get("/hotspot-detect.html")
def apple_hotspot():
    return RedirectResponse(url="/", status_code=302)

# Windows NCSI
@router.get("/ncsi.txt")
def windows_ncsi():
    return PlainTextResponse("Microsoft NCSI")

@router.get("/connecttest.txt")
def windows_connecttest():
    return RedirectResponse(url="/", status_code=302)
