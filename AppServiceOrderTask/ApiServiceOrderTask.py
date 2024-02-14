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
# ApiServiceOrderTask.py
from dataclasses import dataclass
from StartServer import app, db  
from AppEquipment.ApiEquipment import CatEquipment

@dataclass
class ApiResponse:
    success: bool
    messages: list
    output: any = None

def create_message(type_msg: str, message: str, help_msg: str = 'OK'):
    return {'typeMsg': type_msg, 'message': message, 'helpMsg': help_msg}

def init_db():
    from StartServer import db
    return db

class CatStatus(init_db().Model):
    __tablename__ = 'cat_status'
    __table_args__ = {'extend_existing': True}
    id_status = init_db().Column(init_db().Integer, primary_key=True)
    description = init_db().Column(init_db().String)

    def __repr__(self):
        return f"<CatStatus(id_status={self.id_status}, description={self.description})>"

class CatWorker(init_db().Model):
    __tablename__ = 'cat_worker'
    __table_args__ = {'extend_existing': True}
    id_worker = init_db().Column(init_db().Integer, primary_key=True)
    name = init_db().Column(init_db().String)
    user = init_db().Column(init_db().String)
    password = init_db().Column(init_db().String)

    def __repr__(self):
        return f"<CatWorker(id_worker={self.id_worker}, name={self.name}, user={self.user}, password={self.password})>"

class MovServiceOrder(init_db().Model):
    __tablename__ = 'mov_service_order'
    __table_args__ = {'extend_existing': True}
    id_service_order = init_db().Column(init_db().Integer, primary_key=True)
    cod_project = init_db().Column(init_db().String)
    short_name = init_db().Column(init_db().String)
    date_assigned = init_db().Column(init_db().DateTime)
    time_assigned = init_db().Column(init_db().DateTime)
    id_worker = init_db().Column(init_db().Integer, init_db().ForeignKey('cat_worker.id_worker'))
    map_latitude = init_db().Column(init_db().String)
    map_longitude = init_db().Column(init_db().String)
    url_signature = init_db().Column(init_db().String)

    def __repr__(self):
        return f"<MovServiceOrder(id_service_order={self.id_service_order}, cod_project={self.cod_project}, short_name={self.short_name}, date_assigned={self.date_assigned}, time_assigned={self.time_assigned}, id_worker={self.id_worker}, map_latitude={self.map_latitude}, map_longitude={self.map_longitude}, url_signature={self.url_signature})>"

class Task(db.Model):
    __tablename__ = 'task'
    id_task = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(255), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('cat_equipment.id_equipment'), nullable=False)

    equipment = db.relationship('CatEquipment', backref='tasks')

    def __repr__(self):
        return f"<Task(id_task={self.id_task}, task_name={self.task_name}, equipment_id={self.equipment_id})>"

class MovServiceOrderTask(init_db().Model):
    __tablename__ = 'mov_service_order_task'
    __table_args__ = {'extend_existing': True}
    id_service_order_task = init_db().Column(init_db().Integer, primary_key=True)
    id_service_order = init_db().Column(init_db().Integer, init_db().ForeignKey('mov_service_order.id_service_order'))
    id_worker = init_db().Column(init_db().Integer, init_db().ForeignKey('cat_worker.id_worker'))
    id_equipment = init_db().Column(init_db().Integer, init_db().ForeignKey('cat_equipment.id_equipment'))
    description = init_db().Column(init_db().String(255))
    notes = init_db().Column(init_db().String(255))
    date_service = init_db().Column(init_db().DateTime)
    time_spent = init_db().Column(init_db().Time)
    id_status = init_db().Column(init_db().Integer, init_db().ForeignKey('cat_status.id_status'))
    picture = init_db().Column(init_db().LargeBinary)

    def __repr__(self):
        return f"<MovServiceOrderTask(id_service_order_task={self.id_service_order_task}, id_service_order={self.id_service_order}, id_worker={self.id_worker}, id_equipment={self.id_equipment}, description={self.description}, notes={self.notes}, date_service={self.date_service}, time_spent={self.time_spent}, id_status={self.id_status}, picture={self.picture})>"

def get_error_message(exception):
    if isinstance(exception, ValueError):
        return str(exception)
    else:
        return f'Error: {str(exception)}'

def perform_database_operation(func, success_message, error_message):
    db = init_db()
    try:
        result = func(db)
        db.session.commit()
        return ApiResponse(success=True, messages=[create_message('INFO-API', success_message)], output=result)
    except Exception as e:
        return ApiResponse(success=False, messages=[create_message('ERROR', get_error_message(e)), create_message('INFO-API', error_message)])

def get_service_order_tasks(page, per_page, search):
    def query_function(db):
        query = MovServiceOrderTask.query.filter(MovServiceOrderTask.description.ilike(f"%{search}%"))
        tasks = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'tasks': [
                {
                    'id_service_order_task': task.id_service_order_task,
                    'id_service_order': task.id_service_order,
                    'id_worker': task.id_worker,
                    'id_equipment': task.id_equipment,
                    'description': task.description,
                    'notes': task.notes,
                    'date_service': task.date_service.isoformat() if task.date_service else None,
                    'time_spent': task.time_spent.isoformat() if task.time_spent else None,
                    'id_status': task.id_status,
                    'picture': task.picture
                } for task in tasks.items
            ],
            'total_pages': tasks.pages,
            'total_items': tasks.total
        }

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener tareas de orden de servicio')

def create_service_order_task(data):
    print(f"Data received: {data}")

    def create_function(db):
        new_task = MovServiceOrderTask(
            id_service_order=data['id_service_order'],
            id_worker=data['id_worker'],
            id_equipment=data['id_equipment'],
            description=data['description'],
            notes=data['notes'],
            date_service=data['date_service'],
            time_spent=data['time_spent'],
            id_status=data['id_status'],
            picture=data['picture']
        )
        db.session.add(new_task)
        return {'message': 'Tarea creada exitosamente!'}

    return perform_database_operation(create_function, 'Tarea creada exitosamente', 'Error al crear la tarea')

def update_service_order_task(id_service_order_task, data):
    task = MovServiceOrderTask.query.get(id_service_order_task)

    if not task:
        return ApiResponse(success=False, messages=[create_message('ERROR', 'No se encontró la tarea')]), 404

    task.id_service_order = data['id_service_order']
    task.id_worker = data['id_worker']
    task.id_equipment = data['id_equipment']
    task.description = data['description']
    task.notes = data['notes']
    task.date_service = data['date_service']
    task.time_spent = data['time_spent']
    task.id_status = data['id_status']

    return perform_database_operation(lambda: None, 'Tarea actualizada exitosamente', 'Error al actualizar la tarea')

def delete_service_order_task(id_service_order_task):
    def delete_function(db):
        task = db.session.query(MovServiceOrderTask).get(id_service_order_task)

        if not task:
            raise ValueError('No se encontró la tarea a eliminar')

        db.session.delete(task)

    return perform_database_operation(delete_function, 'Tarea eliminada exitosamente de la BD', 'Error al eliminar la tarea')





