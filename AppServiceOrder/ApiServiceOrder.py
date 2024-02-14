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
from dataclasses import dataclass
from datetime import datetime
from StartServer import app, db


@dataclass
class ApiResponse:
    success: bool
    messages: list
    output: any = None


def create_message(type_msg: str, message: str, help_msg: str = 'OK'):
    return {'typeMsg': type_msg, 'message': message, 'helpMsg': help_msg}


class CatWorker(db.Model):
    __tablename__ = 'cat_worker'
    __table_args__ = {'extend_existing': True}
    id_worker = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<CatWorker(id_worker={self.id_worker}, name={self.name}, username={self.username}, password={self.password})>"


class MovServiceOrder(db.Model):
    __tablename__ = 'mov_service_order'
    __table_args__ = {'extend_existing': True}
    id_service_order = db.Column(db.Integer, primary_key=True)
    cod_project = db.Column(db.String(255))
    short_name = db.Column(db.String(255))
    date_assigned = db.Column(db.DateTime)
    time_assigned = db.Column(db.DateTime)
    id_worker = db.Column(db.Integer, db.ForeignKey('cat_worker.id_worker'))
    map_latitude = db.Column(db.String(255))
    map_longitude = db.Column(db.String(255))
    url_signature = db.Column(db.String(255))

    def __repr__(self):
        return f"<MovServiceOrder(id_service_order={self.id_service_order}, cod_project={self.cod_project}, short_name={self.short_name}, date_assigned={self.date_assigned}, time_assigned={self.time_assigned}, id_worker={self.id_worker}, map_latitude={self.map_latitude}, map_longitude={self.map_longitude}, url_signature={self.url_signature})>"


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


def get_mov_service_orders(page, per_page, search):
    def query_function():
        query = MovServiceOrder.query.filter(MovServiceOrder.short_name.ilike(f"%{search}%"))
        service_orders = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'service_orders': [{'id_service_order': order.id_service_order, 'cod_project': order.cod_project, 'short_name': order.short_name, 'date_assigned': order.date_assigned, 'time_assigned': order.time_assigned, 'id_worker': order.id_worker, 'map_latitude': order.map_latitude, 'map_longitude': order.map_longitude, 'url_signature': order.url_signature} for order in service_orders.items],
            'total_pages': service_orders.pages,
            'total_items': service_orders.total
        }

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener órdenes de servicio')


def create_mov_service_order(data):
    def create_function():
        if 'date_assigned' not in data or 'time_assigned' not in data:
            raise ValueError('Both date_assigned and time_assigned are required.')

        date_assigned = datetime.strptime(data['date_assigned'], "%Y-%m-%d") if data['date_assigned'] else None
        time_assigned = datetime.strptime(data['time_assigned'], "%Y-%m-%d %H:%M:%S") if data['time_assigned'] else None

        new_order = MovServiceOrder(
            cod_project=data['cod_project'],
            short_name=data['short_name'],
            date_assigned=date_assigned,
            time_assigned=time_assigned,
            id_worker=data['id_worker'],
            map_latitude=data['map_latitude'],
            map_longitude=data['map_longitude'],
            url_signature=data['url_signature']
        )
        db.session.add(new_order)
        return {'message': 'Registro creado exitosamente!'}

    return perform_database_operation(create_function, 'Registro creado exitosamente', 'Error al crear el registro')


def update_mov_service_order(id_service_order, data):
    order = MovServiceOrder.query.get(id_service_order)

    if not order:
        return ApiResponse(success=False, messages=[create_message('ERROR', 'No se encontró el registro')]), 404

    order.cod_project = data['cod_project']
    order.short_name = data['short_name']

    order.date_assigned = datetime.strptime(data['date_assigned'], "%Y-%m-%d") if data['date_assigned'] else None
    order.time_assigned = datetime.strptime(data['time_assigned'], "%Y-%m-%d %H:%M:%S") if data['time_assigned'] else None

    order.id_worker = data['id_worker']
    order.map_latitude = data['map_latitude']
    order.map_longitude = data['map_longitude']
    order.url_signature = data['url_signature']

    return perform_database_operation(lambda: None, 'Registro actualizado exitosamente', 'Error al actualizar el registro')


def delete_mov_service_order(id_service_order):
    def delete_function():
        order = db.session.query(MovServiceOrder).get(id_service_order)

        if not order:
            raise ValueError('No se encontró el registro a eliminar')

        db.session.delete(order)

    return perform_database_operation(delete_function, 'Registro eliminado exitosamente de la BD', 'Error al eliminar el registro')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)



