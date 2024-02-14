# StartServer.py

import sys
from flask import Flask
from config import Config, db

# Añade el directorio al PYTHONPATH
sys.path.append(r'C:\Users\blind\Downloads\Python bd')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Mueve la inicialización de SQLAlchemy aquí
    db.init_app(app)

    with app.app_context():
        # Mueve la creación de tablas aquí para evitar problemas de importación circular
        db.create_all()

    return app

def register_dynamic_routes(app):
    configurations = BaseConfiguration.query.filter_by(cod_configuration='API_ROUTE').all()

    for config in configurations:
        parameters = BaseConfParameter.query.filter_by(cod_configuration=config.cod_configuration).all()

        for param in parameters:
            # Dividir los métodos y las rutas
            methods, route = param.value.split(','), param.description
            endpoint = param.cod_parameter

            # Asegúrate de que la ruta comience con una barra y elimina espacios
            if not route.startswith('/'):
                route = '/' + route

            route = route.replace(" ", "")  # Elimina espacios en blanco
            methods = [method.strip() for method in methods]  # Elimina espacios en blanco en los métodos

            # Registra la ruta en la aplicación Flask
            app.add_url_rule(route, endpoint, methods=methods)

            # Imprime las rutas registradas
            print(f"Ruta registrada: {route} para {endpoint} con métodos {methods}")


if __name__ == '__main__':
    app = create_app()

    # Añade la siguiente línea para configurar la aplicación Flask con SQLAlchemy
    app.app_context().push()

    # Registrar las rutas dinámicas después de crear la aplicación y configurarla
    from AppWorker.ApiWorker import get_cat_workers, create_cat_worker, update_cat_worker, delete_cat_worker
    from AppWorker.models import BaseConfiguration, BaseConfParameter

    # Registra las rutas dinámicas desde la base de datos
    register_dynamic_routes(app)

    # Resto del código sin cambios
    app.run(debug=True)








