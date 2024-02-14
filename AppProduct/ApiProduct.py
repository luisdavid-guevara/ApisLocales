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
from StartServer import db,app
from dataclasses import dataclass

@dataclass
class ApiResponse:
    success: bool
    messages: list
    output: any = None

def create_message(type_msg: str, message: str, help_msg: str = 'OK'):
    return {'typeMsg': type_msg, 'message': message, 'helpMsg': help_msg}

class CatProduct(db.Model):
    __tablename__ = 'cat_product'
    __table_args__ = {'extend_existing': True}
    id_product = db.Column(db.Integer, primary_key=True)
    product_group_code = db.Column(db.String(255))
    product_code = db.Column(db.String(255))
    sku = db.Column(db.String(255))
    uom = db.Column(db.String(255))
    minimum_stock = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    service_order_items = db.relationship('MovServiceOrderItem', back_populates='product')

    def __repr__(self):
        return f"<CatProduct(id_product={self.id_product}, product_group_code={self.product_group_code}, product_code={self.product_code}, sku={self.sku}, uom={self.uom}, minimum_stock={self.minimum_stock}, is_active={self.is_active})>"


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

def get_cat_products(page, per_page, search):
    def query_function():
        query = CatProduct.query.filter(CatProduct.product_code.ilike(f"%{search}%"))
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'products': [{'id_product': product.id_product, 'product_group_code': product.product_group_code, 'product_code': product.product_code, 'sku': product.sku, 'uom': product.uom, 'minimum_stock': product.minimum_stock, 'is_active': product.is_active} for product in products.items],
            'total_pages': products.pages,
            'total_items': products.total
        }

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener productos')

def create_cat_product(data):
    def create_function():
        new_product = CatProduct(
            product_group_code=data['product_group_code'],
            product_code=data['product_code'],
            sku=data['sku'],
            uom=data['uom'],
            minimum_stock=data['minimum_stock'],
            is_active=data.get('is_active', True)
        )
        db.session.add(new_product)
        return {'message': 'Producto creado exitosamente!'}

    return perform_database_operation(create_function, 'Producto creado exitosamente', 'Error al crear el producto')

def update_cat_product(id_product, data):
    product = CatProduct.query.get(id_product)

    if not product:
        return ApiResponse(success=False, messages=[create_message('ERROR', 'No se encontró el producto')]), 404

    product.product_group_code = data['product_group_code']
    product.product_code = data['product_code']
    product.sku = data['sku']
    product.uom = data['uom']
    product.minimum_stock = data['minimum_stock']
    product.is_active = data.get('is_active', True)

    return perform_database_operation(lambda: None, 'Producto actualizado exitosamente', 'Error al actualizar el producto')

def delete_cat_product(id_product):
    def delete_function():
        product = db.session.query(CatProduct).get(id_product)

        if not product:
            raise ValueError('No se encontró el producto a eliminar')

        db.session.delete(product)

    return perform_database_operation(delete_function, 'Producto eliminado exitosamente de la BD', 'Error al eliminar el producto')

def get_cat_product_by_code(product_code):
    def query_function():
        products = CatProduct.query.filter_by(product_code=product_code).all()
        return [{'id_product': product.id_product, 'product_group_code': product.product_group_code, 'product_code': product.product_code, 'sku': product.sku, 'uom': product.uom, 'minimum_stock': product.minimum_stock, 'is_active': product.is_active} for product in products]

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener productos por código')
