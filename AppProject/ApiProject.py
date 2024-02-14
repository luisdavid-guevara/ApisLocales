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


@dataclass
class ApiResponse:
    success: bool
    messages: list
    output: any = None


def create_message(type_msg: str, message: str, help_msg: str = 'OK'):
    return {'typeMsg': type_msg, 'message': message, 'helpMsg': help_msg}


class MovProject(db.Model):
    __tablename__ = 'mov_project'
    id_project = db.Column(db.Integer, primary_key=True)
    id_company = db.Column(db.Integer)
    cod_project = db.Column(db.String(255))
    name = db.Column(db.String(255))
    short_name = db.Column(db.String(255), db.ForeignKey('cat_customer.short_name'))
    created_at = db.Column(db.TIMESTAMP)
    created_by = db.Column(db.String(255))
    updated_at = db.Column(db.TIMESTAMP)
    updated_by = db.Column(db.String(255))

    # Agrega el backref en la relación
    customer = db.relationship('CatCustomer', backref='projects')

    def __repr__(self):
        return f"<MovProject(id_project={self.id_project}, id_company={self.id_company}, cod_project={self.cod_project}, name={self.name}, short_name={self.short_name}, created_at={self.created_at}, created_by={self.created_by}, updated_at={self.updated_at}, updated_by={self.updated_by})>"



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
        return ApiResponse(success=False, messages=[create_message('ERROR', get_error_message(e)),
                                                    create_message('INFO-API', error_message)])


def get_projects(page, per_page, search):
    def query_function():
        query = MovProject.query.filter(MovProject.cod_project.ilike(f"%{search}%"))
        project_items = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'project_items': [{'id_project': item.id_project, 'id_company': item.id_company, 'cod_project': item.cod_project, 'name': item.name, 'short_name': item.short_name, 'created_at': item.created_at, 'created_by': item.created_by, 'updated_at': item.updated_at, 'updated_by': item.updated_by} for item in project_items.items],
            'total_pages': project_items.pages,
            'total_items': project_items.total
        }

    return perform_database_operation(query_function, 'Consulta exitosa', 'Error al obtener ítems de proyectos')


def create_mov_project(data):
    def create_function():
        new_item = MovProject(
            id_company=data['id_company'],
            cod_project=data['cod_project'],
            name=data['name'],
            short_name=data['short_name'],
            created_at=data['created_at'],
            created_by=data['created_by'],
            updated_at=data['updated_at'],
            updated_by=data['updated_by']
        )
        db.session.add(new_item)
        return {'message': 'Proyecto creado exitosamente!'}

    return perform_database_operation(create_function, 'Proyecto creado exitosamente', 'Error al crear el proyecto')


def update_mov_project(id_project, data):
    item = MovProject.query.get(id_project)

    if not item:
        return ApiResponse(success=False, messages=[create_message('ERROR', 'No se encontró el proyecto')]), 404

    item.id_company = data['id_company']
    item.cod_project = data['cod_project']
    item.name = data['name']
    item.short_name = data['short_name']
    item.created_at = data['created_at']
    item.created_by = data['created_by']
    item.updated_at = data['updated_at']
    item.updated_by = data['updated_by']

    return perform_database_operation(lambda: None, 'Proyecto actualizado exitosamente', 'Error al actualizar el proyecto')


def delete_mov_project(id_project):
    try:
        def delete_function():
            item = db.session.query(MovProject).get(id_project)
            if not item:
                raise ValueError('No se encontró el proyecto a eliminar')
            db.session.delete(item)

        return perform_database_operation(delete_function, 'Proyecto eliminado exitosamente de la BD',
                                         'Error al eliminar el proyecto')
    except Exception as e:
        print(f"Error en delete_mov_project_item: {e}")
        raise e


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
