from deta import Deta
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.models.destination import NewDestination, UpdateDestination


class ManageRoute():

    def __init__(self, deta: Deta) -> None:
        self.router = APIRouter()
        self.database = deta.Base("destinations")
        self._bind()

    def get_router(self) -> APIRouter:
        return self.router

    def _bind(self):

        @self.router.get('/api/search', name='List all Links')
        async def search_destination(param: str = '', searchTarget: str ='p&d', limit: int = 50):
            param = param.strip().lower()
            searchTarget = searchTarget.strip().lower()
            
            if searchTarget not in ['p', 'd', 'p&d']:
                searchTarget = 'p&d'

            if len(param) == 0:
                return []
            
            if searchTarget == 'p':
                query = {'path?contains': param}
            elif searchTarget == 'd':
                query = {'destination?contains': param}
            else:
                query = [
                    {'path?contains': param},
                    {'destination?contains': param}
                ]

            result = self.database.fetch(query=query, limit=limit)

            if result.count == 0:
                return []
            
            newlist = sorted(result.items, key=lambda d: d['clicks'], reverse=True)
            
            return newlist

        @self.router.get('/api/list', name='List all Links')
        async def get_all():
            result = self.database.fetch()

            if result.count == 0:
                return []
            
            newlist = sorted(result.items, key=lambda d: d['clicks'], reverse=True)
            
            return newlist

        @self.router.put('/api/update', name='Update a Link')
        async def update_destination(body: UpdateDestination):
            try:
                result = self.database.fetch(query={'path': body.path})
                if result.count != 0:
                    return JSONResponse(
                        {
                            'message': 'Este nome já esta sendo utilizado.'
                        },
                        status_code=400
                    )

                self.database.update(
                    key=body.id,
                    updates={
                        'path': body.path.strip().lower(),
                        'destination': body.destination,
                        'clicks': 0
                    }
                )
                return JSONResponse(
                    {
                        'message': 'Link editado com sucesso.',
                        'data': {
                            'path': body.path,
                            'destination': body.destination,
                        }
                    }
                )
            except Exception as e:
                return JSONResponse(
                    {
                        'message': 'Ouve um erro ao tentar atualizar o item. Verifique seus dados.',
                        'detail': str(e)
                    },
                    status_code=400
                )

        @self.router.delete('/api/update', name='Delete a Link')
        async def delete_destination(body: UpdateDestination):
            try:
                self.database.delete(body.id)
                return JSONResponse(
                    {
                        'message': 'Link deletado com sucesso.',
                        'data': {
                            'path': body.path,
                            'destination': body.destination,
                        }
                    }
                )
            except Exception as e:
                return JSONResponse(
                    {
                        'message': 'Ouve um erro ao tentar deletar o item. Verifique seus dados.',
                        'detail': str(e)
                    },
                    status_code=400
                )

        @self.router.post('/api/new', name='New Destination')
        async def new_destination(body: NewDestination):
            item = self.database.fetch(query={'path': body.path})
            if item.count == 0:
                self.database.put(
                    data={
                        'path': body.path.strip().lower(),
                        'destination': body.destination,
                        'clicks': 0
                    }
                )
                item = self.database.fetch(query={'path': body.path})
                return JSONResponse(
                    {
                        'message': 'Link criado com sucesso.',
                        'data': {
                            'id': item.items[0]['key'],
                            'path': body.path,
                            'destination': body.destination
                        }
                    }
                )
            
            return JSONResponse(
                {
                    'message': 'Não é possível criar este link com este nome.'
                },
                status_code=400
            )