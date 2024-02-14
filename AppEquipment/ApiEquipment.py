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
# ApiEquipment.py
from StartServer import db,app
from dataclasses import dataclass


@dataclass
class ApiResponse:
    success: bool
    messages: list
    output: any = None

def create_message(type_msg: str, message: str, help_msg: str = 'OK'):
    return {'typeMsg': type_msg, 'message': message, 'helpMsg': help_msg}

class CatEquipment(db.Model):
    __tablename__ = 'cat_equipment'
    id_equipment = db.Column(db.Integer, primary_key=True)
    equipment_type = db.Column(db.String(255), nullable=False)
    serial_number = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<CatEquipment(id_equipment={self.id_equipment}, equipment_type={self.equipment_type}, serial_number={self.serial_number}, condition={self.condition})>"

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

def get_cat_equipment(page, per_page, search):
    def query_function():
        query = CatEquipment.query.filter(CatEquipment.equipment_type.ilike(f"%{search}%"))
        equipment = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'equipment': [{'id_equipment': item.id_equipment, 'equipment_type': item.equipment_type, 'serial_number': item.serial_number, 'condition': item.condition} for item in equipment.items],
            'total_pages': equipment.pages,
            'total_items': equipment.total
        }

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener equipos')

def create_cat_equipment(data):
    def create_function():
        new_equipment = CatEquipment(
            equipment_type=data['equipment_type'],
            serial_number=data['serial_number'],
            condition=data.get('condition')
        )
        db.session.add(new_equipment)
        return {'message': 'Equipo creado exitosamente!'}

    return perform_database_operation(create_function, 'Equipo creado exitosamente', 'Error al crear el equipo')

def update_cat_equipment(id_equipment, data):
    equipment = CatEquipment.query.get(id_equipment)

    if not equipment:
        return ApiResponse(success=False, messages=[create_message('ERROR', 'No se encontró el equipo')]), 404

    equipment.equipment_type = data['equipment_type']
    equipment.serial_number = data['serial_number']
    equipment.condition = data.get('condition')

    return perform_database_operation(lambda: None, 'Equipo actualizado exitosamente', 'Error al actualizar el equipo')

def delete_cat_equipment(id_equipment):
    def delete_function():
        equipment = db.session.query(CatEquipment).get(id_equipment)

        if not equipment:
            raise ValueError('No se encontró el equipo a eliminar')

        db.session.delete(equipment)

    return perform_database_operation(delete_function, 'Equipo eliminado exitosamente de la BD', 'Error al eliminar el equipo')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()




