import os

from deta import Deta
from fastapi import APIRouter

from src.routes.destination_route import DestinationRoute
from src.routes.manage_route import ManageRoute

router = APIRouter()
deta = Deta(os.environ['DETA_PROJECT_KEY'])

router.include_router(
    ManageRoute(deta).get_router(),
    tags=['Manage']
)

router.include_router(
    DestinationRoute(deta).get_router(),
    tags=['Destination']
)
