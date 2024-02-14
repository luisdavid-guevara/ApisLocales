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
# ApiCustomer.py
from StartServer import db,app
from dataclasses import dataclass

@dataclass
class ApiResponse:
    success: bool
    messages: list
    output: any = None

def create_message(type_msg: str, message: str, help_msg: str = 'OK'):
    return {'typeMsg': type_msg, 'message': message, 'helpMsg': help_msg}

class CatCustomer(db.Model):
    __tablename__ = 'cat_customer'
    id_customer = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(255), nullable=False, unique=True)
    tax_id = db.Column(db.String(255), nullable=False)
    tax_regime = db.Column(db.String(255), nullable=False)
    customer_name = db.Column(db.String(255), nullable=False)
    legal_name = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<CatCustomer(id_customer={self.id_customer}, short_name={self.short_name}, tax_id={self.tax_id}, tax_regime={self.tax_regime}, customer_name={self.customer_name}, legal_name={self.legal_name}, website={self.website}, email={self.email}, phone={self.phone}, is_active={self.is_active})>"




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

def get_cat_customer(page, per_page, search):
    def query_function():
        query = CatCustomer.query.filter(CatCustomer.short_name.ilike(f"%{search}%"))
        customers = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'customers': [{'id_customer': customer.id_customer, 'short_name': customer.short_name, 'tax_id': customer.tax_id, 'tax_regime': customer.tax_regime, 'customer_name': customer.customer_name, 'legal_name': customer.legal_name, 'website': customer.website, 'email': customer.email, 'phone': customer.phone, 'is_active': customer.is_active} for customer in customers.items],
            'total_pages': customers.pages,
            'total_items': customers.total
        }

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener clientes')

def create_cat_customer(data):
    def create_function():
        new_customer = CatCustomer(
            short_name=data['short_name'],
            tax_id=data['tax_id'],
            tax_regime=data['tax_regime'],
            customer_name=data['customer_name'],
            legal_name=data['legal_name'],
            website=data.get('website'),
            email=data.get('email'),
            phone=data.get('phone'),
            is_active=data.get('is_active', True)
        )
        db.session.add(new_customer)
        return {'message': 'Cliente creado exitosamente!'}

    return perform_database_operation(create_function, 'Cliente creado exitosamente', 'Error al crear el cliente')

def update_cat_customer(id_customer, data):
    customer = CatCustomer.query.get(id_customer)

    if not customer:
        return ApiResponse(success=False, messages=[create_message('ERROR', 'No se encontró el cliente')]), 404

    customer.short_name = data['short_name']
    customer.tax_id = data['tax_id']
    customer.tax_regime = data['tax_regime']
    customer.customer_name = data['customer_name']
    customer.legal_name = data['legal_name']
    customer.website = data.get('website')
    customer.email = data.get('email')
    customer.phone = data.get('phone')
    customer.is_active = data.get('is_active', True)

    return perform_database_operation(lambda: None, 'Cliente actualizado exitosamente', 'Error al actualizar el cliente')

def delete_cat_customer(id_customer):
    def delete_function():
        customer = db.session.query(CatCustomer).get(id_customer)

        if not customer:
            raise ValueError('No se encontró el cliente a eliminar')

        db.session.delete(customer)

    return perform_database_operation(delete_function, 'Cliente eliminado exitosamente de la BD', 'Error al eliminar el cliente')

def get_cat_customer_by_short_name(short_name):
    def query_function():
        customers = CatCustomer.query.filter_by(short_name=short_name).all()
        return [{'id_customer': customer.id_customer, 'short_name': customer.short_name, 'tax_id': customer.tax_id, 'tax_regime': customer.tax_regime, 'customer_name': customer.customer_name, 'legal_name': customer.legal_name, 'website': customer.website, 'email': customer.email, 'phone': customer.phone, 'is_active': customer.is_active} for customer in customers]

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener clientes por nombre corto')





