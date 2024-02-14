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
from StartServer import app, db
from AppProduct.ApiProduct import CatProduct

@dataclass
class ApiResponse:
    success: bool
    messages: list
    output: any = None


def create_message(type_msg: str, message: str, help_msg: str = 'OK'):
    return {'typeMsg': type_msg, 'message': message, 'helpMsg': help_msg}


class MovServiceOrderItem(db.Model):
    __tablename__ = 'mov_service_order_item'
    id_service_order_item = db.Column(db.Integer, primary_key=True)
    id_service_order = db.Column(db.Integer, db.ForeignKey('mov_service_order.id_service_order'))
    id_service_order_sequence = db.Column(db.Integer)
    product_code = db.Column(db.String(255), db.ForeignKey('cat_product.product_code'))
    quantity = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    value = db.Column(db.Float)

    product = db.relationship('CatProduct', back_populates='service_order_items')

    def __repr__(self):
        return f"<MovServiceOrderItem(id_service_order_item={self.id_service_order_item}, id_service_order={self.id_service_order}, id_service_order_sequence={self.id_service_order_sequence}, product_code={self.product_code}, quantity={self.quantity}, unit_price={self.unit_price}, value={self.value})>"


class MovServiceOrder(db.Model):
    __tablename__ = 'mov_service_order'
    id_service_order = db.Column(db.Integer, primary_key=True)
    cod_project = db.Column(db.String(255))
    short_name = db.Column(db.String(255))
    date_assigned = db.Column(db.TIMESTAMP)
    time_assigned = db.Column(db.TIMESTAMP)
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


def get_mov_service_order_items(page, per_page, search):
    def query_function():
        query = MovServiceOrderItem.query.filter(MovServiceOrderItem.product_code.ilike(f"%{search}%"))
        service_order_items = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'service_order_items': [{'id_service_order_item': item.id_service_order_item, 'id_service_order': item.id_service_order, 'id_service_order_sequence': item.id_service_order_sequence, 'product_code': item.product_code, 'quantity': item.quantity, 'unit_price': item.unit_price, 'value': item.value} for item in service_order_items.items],
            'total_pages': service_order_items.pages,
            'total_items': service_order_items.total
        }

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener ítems de órdenes de servicio')


def create_mov_service_order_item(data):
    def create_function():
        new_item = MovServiceOrderItem(
            id_service_order=data['id_service_order'],
            id_service_order_sequence=data['id_service_order_sequence'],
            product_code=data['product_code'],
            quantity=data['quantity'],
            unit_price=data['unit_price'],
            value=data['value']
        )
        db.session.add(new_item)
        return {'message': 'Ítem de orden de servicio creado exitosamente!'}

    return perform_database_operation(create_function, 'Ítem de orden de servicio creado exitosamente', 'Error al crear el ítem de orden de servicio')


def update_mov_service_order_item(id_service_order_item, data):
    item = MovServiceOrderItem.query.get(id_service_order_item)

    if not item:
        return ApiResponse(success=False, messages=[create_message('ERROR', 'No se encontró el ítem')]), 404

    item.id_service_order = data['id_service_order']
    item.id_service_order_sequence = data['id_service_order_sequence']
    item.product_code = data['product_code']
    item.quantity = data['quantity']
    item.unit_price = data['unit_price']
    item.value = data['value']

    return perform_database_operation(lambda: None, 'Ítem de orden de servicio actualizado exitosamente', 'Error al actualizar el ítem de orden de servicio')


def delete_mov_service_order_item(id_service_order_item):
    try:
        def delete_function():
            item = db.session.query(MovServiceOrderItem).get(id_service_order_item)
            if not item:
                raise ValueError('No se encontró el ítem a eliminar')
            db.session.delete(item)

        return perform_database_operation(delete_function, 'Ítem de orden de servicio eliminado exitosamente de la BD',
                                         'Error al eliminar el ítem de orden de servicio')
    except Exception as e:
        print(f"Error en delete_mov_service_order_item: {e}")
        raise e


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)



