#/*-------------------------------------------------------------------------------------------------------------------------------\
#| TERIAN INTEGRADORES DE TECNOLOGIA             |                 DIRECCION DE TECNOLOGIAS DE LA INFORMACION                     |
#|--------------------------------------------------------------------------------------------------------------------------------|
#| Programa: folder\ApiWorker                                                                                                 |
#| Objetivo: Api que permite el crud y la paginacion de la tabala cat_worker                                                                                       |
#|    Autor: Luis David Guevara Sandoval (LDGS)                                               |    
#|    Fecha: Enero del 2024                                                                                                      |   
#|  Sistema: Terian Field Service                                                                                                 |
#|--------------------------------------------------------------------------------------------------------------------------------|
#|                                     H I S T O R I A L   D E   M O D I F I C A C I O N E S                                      |
#|--------------------------------------------------------------------------------------------------------------------------------|
#| RESPONSABLE              |  TAREA   | FECHA        | DESCRIPCION                                                               |
#|--------------------------------------------------------------------------------------------------------------------------------|
#| [Nombre Apellido] (INIC) |  000000  |  TT/TT/TTTT  | [Descripción del Cambio]                                                  |
#\-------------------------------------------------------------------------------------------------------------------------------*/

from StartServer import db  
from dataclasses import dataclass
from flask import request


@dataclass
class ApiResponse:
    success: bool
    messages: list
    output: any = None

def create_message(type_msg: str, message: str, help_msg: str = 'OK'):
    return {'typeMsg': type_msg, 'message': message, 'helpMsg': help_msg}

class CatWorker(db.Model):
    __tablename__ = 'cat_worker'
    id_worker = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<CatWorker(id_worker={self.id_worker}, name={self.name}, username={self.username}, password={self.password})>"

def get_error_message(exception):
    if isinstance(exception, ValueError):
        return str(exception)
    else:
        return f'Error: {str(exception)}'

def perform_database_operation(func, success_message, error_message):
    try:
        result = func()
        db.session.commit()
        return ApiResponse(success=True, messages=[create_message('INFO-API', success_message)], output=result)
    except Exception as e:
        return ApiResponse(success=False, messages=[create_message('ERROR', get_error_message(e)), create_message('INFO-API', error_message)])

def get_cat_workers():
    page = request.args.get('page', default=1, type=int)
    per_page = 10
    search = request.args.get('search', default='', type=str)

    def query_function():
        query = CatWorker.query.filter(CatWorker.name.ilike(f"%{search}%"))
        workers = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'workers': [{'id_worker': worker.id_worker, 'name': worker.name, 'username': worker.username, 'password': worker.password} for worker in workers.items],
            'total_pages': workers.pages,
            'total_items': workers.total
        }

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener trabajadores')


def create_cat_worker(data):
    def create_function():
        new_worker = CatWorker(name=data['name'], username=data['username'], password=data['password'])
        db.session.add(new_worker)
        return {'message': 'Registro creado exitosamente!'}

    return perform_database_operation(create_function, 'Registro creado exitosamente', 'Error al crear el registro')

def update_cat_worker(id_worker, data):
    worker = CatWorker.query.get(id_worker)

    if not worker:
        return ApiResponse(success=False, messages=[create_message('ERROR', 'No se encontró el registro')]), 404

    worker.name = data['name']
    worker.username = data['username']
    worker.password = data['password']

    return perform_database_operation(lambda: None, 'Registro actualizado exitosamente', 'Error al actualizar el registro')

def delete_cat_worker(id_worker):
    def delete_function():
        worker = db.session.query(CatWorker).get(id_worker)

        if not worker:
            raise ValueError('No se encontró el registro a eliminar')

        db.session.delete(worker)

    return perform_database_operation(delete_function, 'Registro eliminado exitosamente de la BD', 'Error al eliminar el registro')

def get_cat_workers_by_user(username):
    def query_function():
        workers = CatWorker.query.filter_by(username=username).all()
        return [{'id_worker': worker.id_worker, 'name': worker.name, 'username': worker.username, 'password': worker.password} for worker in workers]

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener trabajadores por usuario')