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
# ApiStatus.py
from StartServer import db
from dataclasses import dataclass


@dataclass
class ApiResponse:
    success: bool
    messages: list
    output: any = None

def create_message(type_msg: str, message: str, help_msg: str = 'OK'):
    return {'typeMsg': type_msg, 'message': message, 'helpMsg': help_msg}

class CatStatus(db.Model):
    __tablename__ = 'cat_status'
    id_status = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<CatStatus(id_status={self.id_status}, description={self.description})>"

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

def get_cat_status(page, per_page, search):
    def query_function():
        query = CatStatus.query.filter(CatStatus.description.ilike(f"%{search}%"))
        statuses = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'statuses': [{'id_status': status.id_status, 'description': status.description} for status in statuses.items],
            'total_pages': statuses.pages,
            'total_items': statuses.total
        }

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener estados')

def create_cat_status(data):
    def create_function():
        new_status = CatStatus(description=data['description'])
        db.session.add(new_status)
        return {'message': 'Estado creado exitosamente!'}

    return perform_database_operation(create_function, 'Estado creado exitosamente', 'Error al crear el estado')

def update_cat_status(id_status, data):
    status = CatStatus.query.get(id_status)

    if not status:
        return ApiResponse(success=False, messages=[create_message('ERROR', 'No se encontró el estado')]), 404

    status.description = data['description']

    return perform_database_operation(lambda: None, 'Estado actualizado exitosamente', 'Error al actualizar el estado')

def delete_cat_status(id_status):
    def delete_function():
        status = db.session.query(CatStatus).get(id_status)

        if not status:
            raise ValueError('No se encontró el estado a eliminar')

        db.session.delete(status)

    return perform_database_operation(delete_function, 'Estado eliminado exitosamente de la BD', 'Error al eliminar el estado')




