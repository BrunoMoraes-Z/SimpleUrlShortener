import json
import os

from deta import Deta
from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse, Response


class DestinationRoute():

    def __init__(self, deta: Deta) -> None:
        self.router = APIRouter()
        self.database = deta.Base("destinations")
        self._save_default()
        self._bind()

    def get_router(self) -> APIRouter:
        return self.router

    def _save_default(self):
        item = self.database.fetch(query={'path': "DEFAULT"})
        if item.count == 0:
            self.database.put(
                data={
                    'path': 'DEFAULT',
                    'destination': os.environ['DEFAULT_DESTINATION_WHEN_NOT_FOUND'],
                    'clicks': 0
                }
            )
            item = self.database.fetch(query={'path': "DEFAULT"})
        self.default = item.items[0]['destination']

    def _bind(self):
        @self.router.get('/{path:path}', name='Get Destination')
        async def get_destination(path: str):
            item = self.database.fetch(query={'path': path})
            if item.count != 0:
                self.database.update(
                    key=item.items[0]['key'],
                    updates={
                        'clicks': int(item.items[0]['clicks']) + 1
                    }
                )

                destination: str = item.items[0]['destination']

                # Caso seja URL
                if destination.startswith('http'):
                    return RedirectResponse(destination)
                
                # Caso seja JSON
                if destination.startswith('{') or destination.startswith('['):
                    return JSONResponse(
                        json.loads(destination)
                    )
                
                # Caso seja XML
                if destination.startswith('<') and destination.endswith('>'):
                    return Response(
                        content=destination,
                        headers={
                            'content-type': 'application/xml'
                        }
                    )
                
                # Retorna Texto
                return destination
            return RedirectResponse(self.default)