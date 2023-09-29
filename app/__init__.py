from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from app.database import DatabaseConnection
from config import Config
import os

def init_app():
    #app = Flask(__name__, static_folder=Config.STATIC_FOLDER, template_folder=Config.TEMPLATE_FOLDER) eliminar si funciona
    app = Flask(__name__, static_folder=Config.STATIC_FOLDER, template_folder=Config.TEMPLATE_FOLDER, instance_relative_config=True)
    #app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER  eliminar si funciona
    app.config.from_object(Config)
    app.secret_key = 'tu_clave_secreta'  # Cambia esto a una clave segura

    @app.route('/Enter.html')
    def Enter():
        return render_template('Enter.html')

    # Restringir el acceso a loginP.html solo a usuarios registrados
    @app.route('/loginP.html')
    def login_p():
        if 'user_id' in session:
            correo_usuario = session['user_id']
            
            # Consulta SQL para obtener el ID del usuario por su correo electrónico
            query = "SELECT id FROM usuarios WHERE correo_electronico = %s"
            result = DatabaseConnection.fetch_one(query, (correo_usuario,))
            
            if result:
                user_id = result[0]
                
                # Obtener la lista de servidores desde la base de datos utilizando user_id como ID del usuario
                servidores = obtener_servidores_del_usuario(user_id)
                return render_template('loginP.html', servidores=servidores)
        
        flash("Debes iniciar sesión o registrarte para acceder a esta página.", "info")
        return redirect(url_for('bienvenido'))

    def obtener_servidores_del_usuario(user_id):
        try:
            # Define la consulta SQL para obtener los servidores asociados al usuario
            query = "SELECT id, nombre_servidor FROM servidores WHERE propietario_id = %s"
            
            # Ejecuta la consulta y obtén los resultados
            servidores = DatabaseConnection.fetch_all(query, (user_id,))
            
            return servidores
        except Exception as e:
            # Manejo de errores
            print("Error al obtener servidores del usuario:", str(e))
            return []

    # Restringir el acceso a miperfil.html solo a usuarios registrados
    @app.route('/miperfil.html')
    def mi_perfil():
        if 'user_id' in session:
            user_id = session['user_id']
            user = obtener_usuario_por_correo(user_id)

            if user:
               
                if request.method == 'POST':
                    # Verificar si se ha enviado una nueva imagen de perfil
                    if 'profileImage' in request.files:
                        image = request.files['profileImage']
                        if image.filename != '':
                            # Procesar y guardar la imagen de perfil
                            image_path = os.path.join(Config.UPLOAD_FOLDER, image.filename)    #image_path = Config.UPLOAD_FOLDER + '/' + image.filename
                            image.save(image_path)

                            # Actualizar el atributo 'imagen_perfil' en la base de datos con la ruta de la imagen
                            #actualizar_imagen_perfil(user_id, image_path)
                            # Define la consulta SQL para actualizar la imagen de perfil en la base de datos
                            query = "UPDATE usuarios SET imagen_perfil = %s WHERE correo_electronico = %s"
                            # Ejecuta la consulta
                            DatabaseConnection.execute(query, (image_path, user_id))

                    # Procesar otros cambios en los datos del usuario (nombre, apellido, etc.)
                    nuevoUsuario = request.form.get('userName')
                    nuevoNombre = request.form.get('userFirstName')
                    nuevoApellido = request.form.get('userLastName')
                    nuevoEmail = request.form.get('userEmail')
                    nuevoimage = request.form.get('userimage')

                    # Actualizar los datos en la base de datos
                    #actualizar_datos_usuario(user_id, nuevoUsuario, nuevoNombre, nuevoApellido, nuevoEmail, nuevoimage)
                    # Define la consulta SQL para actualizar los datos del usuario en la base de datos
                    query = "UPDATE usuarios SET nombre_usuario = %s, nombre = %s, apellido = %s, correo_electronico = %s, imagen_perfil = %s WHERE correo_electronico = %s"
                    # Ejecuta la consulta
                    DatabaseConnection.execute(query, (nuevoUsuario, nuevoNombre, nuevoApellido, nuevoEmail, nuevoimage, user_id))
                
                #renderizar la plantilla con la información del usuario y la imagen de perfil
                return render_template('miperfil.html', user=user)
            else:
                flash("El usuario no se encuentra en la base de datos.", "error")
                return redirect(url_for('bienvenido'))
        else:
            flash("Debes iniciar sesión o registrarte para acceder a esta página.", "info")
            return redirect(url_for('bienvenido'))
        
    def obtener_usuario_por_correo(correo):
        # Define la consulta SQL para obtener al usuario por su dirección de correo electrónico
        query = "SELECT id, nombre_usuario, correo_electronico, nombre, apellido, imagen_perfil, contrasena FROM usuarios WHERE correo_electronico = %s"
        
        # Ejecuta la consulta y obtén el resultado
        result = DatabaseConnection.fetch_one(query, (correo,))
        
        if result:
            # Construye un diccionario con los datos del usuario
            user = {
                'id': result[0],
                'nombre_usuario': result[1],
                'correo_electronico': result[2],
                'nombre': result[3],
                'apellido': result[4],
                'imagen_perfil': result[5],
                'contrasena': result[6]
                
            }
            return user
        else:
            return None

    # Restringir el acceso a la página de inicio (bienvenido) solo a usuarios no registrados
    @app.route('/', methods=['GET', 'POST'])
    def bienvenido():
        if request.method == 'POST':
            if 'registerEmail' in request.form:  # Verifica si se está procesando un registro
                return register()    
            else:
                return login()
        else:
            #if 'user_id' in session:
                #return redirect(url_for('mi_perfil'))
            return mostrar_formulario()

    def obtener_usuarios(email):
        # Agrega la lógica para obtener usuarios de la base de datos.
        query = "SELECT correo_electronico, contrasena FROM usuarios WHERE correo_electronico = %s"
        user = DatabaseConnection.fetch_one(query, (email,))
        return user

    @app.route('/login', methods=['POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('registerEmail')
            password = request.form.get('registerPassword')

            # Obtener el usuario de la base de datos
            user = obtener_usuarios(email)

            if user and user[1] == password:
                flash("Inicio de sesión exitoso", "success")
                # Establecer el usuario en la sesión
                session['user_id'] = email
                return redirect(url_for('login_p'))
            else:
                flash("Correo electrónico o contraseña incorrectos", "error")

        # Renderizar el formulario de inicio de sesión
        return render_template('login.html')

    def mostrar_formulario():
        return render_template('login.html')
    
    @app.route('/register', methods=['POST'])
    def register():
        if request.method == 'POST':
            # Obtener los datos del formulario
            registerEmail = request.form.get('registerEmail')
            registerUsername = request.form.get('registerUsername')
            registerFirstName = request.form.get('registerFirstName')
            registerLastName = request.form.get('registerLastName')
            registerPassword = request.form.get('registerPassword')
            dob = request.form.get('dob')

            # Insertar nuevo usuario en la base de datos
            query = "INSERT INTO usuarios (nombre_usuario, contrasena, correo_electronico, nombre, apellido, fecha_nacimiento) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (registerUsername, registerPassword, registerEmail, registerFirstName, registerLastName, dob)

            try:
                DatabaseConnection.execute(query, values)
                flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
                return redirect(url_for('bienvenido'))
            except Exception as e:
                flash("Registro fallido. Por favor, inténtalo nuevamente.", "error")
                print("Error de base de datos:", str(e))

        # Renderizar el formulario de registro
        return render_template('login.html')
    
    @app.route('/guardar_cambios', methods=['POST'])
    def guardar_cambios():
        if 'user_id' in session:
            user_id = session['user_id']
            user = obtener_usuario_por_correo(user_id)
            print(f"usuario: {user_id}")
            if user:
                # Verificar si se ha enviado una nueva imagen de perfil
                if 'profileImage' in request.files:
                    image = request.files['profileImage']
                    print(f"image: {image}")
                    if image.filename != '':
                        # Crear el directorio si no existe
                        image_dir = os.path.join(Config.UPLOAD_FOLDER, user_id)
                        os.makedirs(image_dir, exist_ok=True)

                        # Procesar y guardar la imagen de perfil
                        #image_path = Config.UPLOAD_FOLDER + '/' + image.filename
                        #print(f"image_path: {image_path}")
                        image_path = os.path.join(image_dir, image.filename)
                        print(f"image_path: {image_path}")
                        image.save(image_path)
                        
                        # Actualizar la imagen de perfil en la base de datos
                        query = "UPDATE usuarios SET imagen_perfil = %s WHERE correo_electronico = %s"
                        DatabaseConnection.execute(query, (image_path, user_id))

                # Procesar otros cambios en los datos del usuario (nombre, apellido, etc.)
                nuevoUsuario = request.form.get('userName')
                nuevoNombre = request.form.get('userFirstName')
                nuevoApellido = request.form.get('userLastName')
                nuevoEmail = request.form.get('userEmail')

                # Actualizar los datos en la base de datos
                query = "UPDATE usuarios SET nombre_usuario = %s, nombre = %s, apellido = %s, correo_electronico = %s WHERE correo_electronico = %s"
                DatabaseConnection.execute(query, (nuevoUsuario, nuevoNombre, nuevoApellido, nuevoEmail, user_id))

                # Devolver una respuesta JSON para indicar el éxito de la operación
                response_data = {'success': True}
                return jsonify(response_data)

        # Si algo sale mal, devolver una respuesta JSON con un mensaje de error
        response_data = {'success': False, 'message': 'Error al guardar los cambios.'}
        return jsonify(response_data), 400


    # Agregar una nueva ruta para cambiar la contraseña
    @app.route('/cambiar_contraseña', methods=['POST'])
    def cambiar_contraseña():
        if 'user_id' in session:
            user_id = session['user_id']
            print(f"usuario: {user_id}")

            # Obtener la contraseña actual, nueva contraseña y confirmación de la solicitud POST
            contraseña_actual = request.form.get('contraseñaActual')
            nueva_contraseña = request.form.get('nuevaContraseña')
            confirmar_contraseña = request.form.get('confirmarContraseña')

            # Define la consulta SQL para obtener la contraseña actual del usuario
            query = "SELECT contrasena FROM usuarios WHERE correo_electronico = %s"
            # Ejecuta la consulta
            result = DatabaseConnection.fetch_one(query, (user_id,))
            print(f"result: {result}")

            if result:
                contraseña_almacenada = result[0]
                print(f"contraseña_almacenada: {contraseña_almacenada}")

                # Verificar que la contraseña actual coincida con la almacenada en la base de datos
                if contraseña_almacenada == contraseña_actual:
                    print(f"contraseña_actual: {contraseña_actual}")
                    # Verificar si la nueva contraseña y la confirmación coinciden
                    if nueva_contraseña == confirmar_contraseña:
                        print(f"nueva_contraseña: {nueva_contraseña}")
                        print(f"confirmar_contraseña: {confirmar_contraseña}")
                        # Actualizar la contraseña en la base de datos
                        # Define la consulta SQL para actualizar la contraseña
                        query = "UPDATE usuarios SET contrasena = %s WHERE correo_electronico = %s"
                        # Ejecuta la consulta
                        DatabaseConnection.execute(query, (nueva_contraseña, user_id))
                        return jsonify({"success": True, "message": "Contraseña cambiada con éxito."})
                    else:
                        return jsonify({"success": False, "message": "La nueva contraseña y la confirmación no coinciden."})
                else:
                    return jsonify({"success": False, "message": "Contraseña actual incorrecta."})

        return jsonify({"success": False, "message": "Error al cambiar la contraseña."})  

    # Realiza la alteración de la tabla para agregar la columna propietario_id
    query_check = "SHOW COLUMNS FROM servidores LIKE 'propietario_id'"
    result = DatabaseConnection.fetch_one(query_check)

    from flask import request, jsonify

    # Guarda los servidores creados por el ususario
    @app.route('/guardar_servidor', methods=['POST'])
    def guardar_servidor():
        try:
            if 'user_id' in session:
                # Obtener el correo electrónico del usuario desde la sesión
                correo_usuario = session.get('user_id')
                print(f"correo_usuario: {correo_usuario}")
                # Define la consulta SQL para obtener el ID actual del usuario
                query = "SELECT id FROM usuarios WHERE correo_electronico = %s"
                
                # Ejecutar la consulta
                result = DatabaseConnection.fetch_one(query, (correo_usuario,))
                print(f"result: {result}")
                if result:
                    user_id = result[0]  # El ID del usuario que inició sesión
                    print(f"user_id: {user_id}")
                    # Obtener los datos JSON de la solicitud
                    data = request.get_json()
                    print(f"data: {data}")
                    if 'nombreServidor' in data:
                        nombre_servidor = data['nombreServidor']
                        print(f"nombre_servidor: {nombre_servidor}")
                        # Verificar si el servidor ya existe para evitar duplicados
                        query = "SELECT id FROM servidores WHERE nombre_servidor = %s"
                        result = DatabaseConnection.fetch_one(query, (nombre_servidor,))

                        if result:
                            response_data = {'success': False, 'message': 'El servidor ya existe.'}
                        else:
                            # Insertar el servidor en la base de datos con el propietario_id
                            query = "INSERT INTO servidores (nombre_servidor, propietario_id) VALUES (%s, %s)"
                            values = (nombre_servidor, user_id)
                            DatabaseConnection.execute(query, values)
                            DatabaseConnection.get_connection().commit()
                            response_data = {'success': True, 'message': 'Servidor creado con éxito.'}
                    else:
                        response_data = {'success': False, 'message': 'Nombre de servidor no proporcionado.'}
                else:
                    response_data = {'success': False, 'message': 'Usuario no encontrado.'}
            else:
                user_id = None
                response_data = {'success': False, 'message': 'Usuario no autenticado.'}

        except Exception as e:
            response_data = {'success': False, 'message': 'Error al guardar el servidor.'}
            print("Error de base de datos:", str(e))
            DatabaseConnection.get_connection().rollback()

        return jsonify(response_data)
    
    def obtener_servidor_id_por_nombre(nombre_servidor):
        query = "SELECT id FROM servidores WHERE nombre_servidor = %s"
        result = DatabaseConnection.fetch_one(query, (nombre_servidor,))
        if result:
            return result[0]
        return None

    @app.route('/crear_canal', methods=['POST'])
    def crear_canal():
        if 'user_id' in session:
            user_id = session['user_id']
            print(f"user_id: {user_id}")
            data = request.get_json()
            nombre_canal = data.get('nombreCanal')
            print(f"nombre_canal: {nombre_canal}")
            servidor_nombre = data.get('servidorNombre')  # Cambiar a 'servidorNombre'
            print(f"servidor_nombre: {servidor_nombre}")
            if nombre_canal and servidor_nombre:
                servidor_id = obtener_servidor_id_por_nombre(servidor_nombre)
                print(f"servidor_id: {servidor_id}")
                if servidor_id is not None:
                    # Insertar el nuevo canal en la base de datos
                    query = "INSERT INTO canales (nombre_canal, servidor_id) VALUES (%s, %s)"
                    values = (nombre_canal, servidor_id)
                    print(f"values: {values}")
                    DatabaseConnection.execute(query, values)
                    DatabaseConnection.get_connection().commit()
                    
                    # Puedes devolver un mensaje de éxito si lo deseas
                    response_data = {'success': True, 'message': 'Canal creado con éxito.'}
                else:
                    response_data = {'success': False, 'message': 'El servidor no fue encontrado.'}
            else:
                response_data = {'success': False, 'message': 'Nombre de canal o servidor no proporcionado.'}
        else:
            response_data = {'success': False, 'message': 'Usuario no autenticado.'}

        return jsonify(response_data)   

    return app


""" # Consultar la ruta de la imagen de perfil desde la base de datos
                query = "SELECT imagen_perfil FROM usuarios WHERE correo_electronico = %s"
                result = DatabaseConnection.execute(query, (user_id,))
                print(f"result: {result}")
                profile_image_path = result.fetchone()[0] if result else None   
                , profile_image_path=profile_image_path """
                

"""    def actualizar_imagen_perfil(user_id, image_path):
        # Define la consulta SQL para actualizar la imagen de perfil en la base de datos
        query = "UPDATE usuarios SET imagen_perfil = %s WHERE correo_electronico = %s"
        # Ejecuta la consulta
        DatabaseConnection.execute(query, (image_path, user_id))

    def actualizar_datos_usuario(user_id, nuevoUsuario, nuevoNombre, nuevoApellido, nuevoEmail):
        # Define la consulta SQL para actualizar los datos del usuario en la base de datos
        query = "UPDATE usuarios SET nombre_usuario = %s, nombre = %s, apellido = %s, correo_electronico = %s WHERE correo_electronico = %s"
        # Ejecuta la consulta
        DatabaseConnection.execute(query, (nuevoUsuario, nuevoNombre, nuevoApellido, nuevoEmail, user_id))"""

"""   @app.route('/guardar_cambios', methods=['POST'])
    def guardar_cambios():
        if 'user_id' in session:
            user_id = session['user_id']
            user = obtener_usuario_por_correo(user_id)
            print(f"usuario: {user_id}")
            if user:
                # Verificar si se ha enviado una nueva imagen de perfil
                if 'profileImage' in request.files:
                    image = request.files['profileImage']
                    print(f"image: {image}")
                    if image.filename != '':
                        # Procesar y guardar la imagen de perfil
                        image_path = Config.UPLOAD_FOLDER +  '/' + image.filename
                        print(f"image_path: {image_path}")
                        image.save(image_path)
                        print(f"image: {image}")
                        # Actualizar el atributo 'imagen_perfil' en la base de datos con la ruta de la imagen
                        actualizar_imagen_perfil(user_id, image_path)

                # Procesar otros cambios en los datos del usuario (nombre, apellido, etc.)
                nuevoUsuario = request.form.get('userName')
                nuevoNombre = request.form.get('userFirstName')
                nuevoApellido = request.form.get('userLastName')
                nuevoEmail = request.form.get('userEmail')

                # Actualizar los datos en la base de datos
                actualizar_datos_usuario(user_id, nuevoUsuario, nuevoNombre, nuevoApellido, nuevoEmail)

                # Devolver una respuesta JSON para indicar el éxito de la operación
                response_data = {'success': True}
                return jsonify(response_data)

        # Si algo sale mal, devolver una respuesta JSON con un mensaje de error
        response_data = {'success': False, 'message': 'Error al guardar los cambios.'}
        return jsonify(response_data), 400"""

"""    # Agregar una nueva ruta para cambiar la contraseña
    @app.route('/cambiar_contraseña', methods=['POST'])
    def cambiar_contraseña():
        if 'user_id' in session:
            user_id = session['user_id']
            print(f"usuario: {user_id}")

            # Obtener la contraseña actual y nueva contraseña de la solicitud POST
            nueva_contraseña = request.form.get('nuevaContraseña')
            confirmar_contraseña = request.form.get('confirmarContraseña')

            # Verificar si la nueva contraseña y la confirmación coinciden
            if nueva_contraseña == confirmar_contraseña:
                print(f"nueva_contraseña: {nueva_contraseña}")
                print(f"confirmar_contraseña: {confirmar_contraseña}")
                # Actualizar la contraseña en la base de datos
                # Define la consulta SQL para actualizar la contraseña
                #query = "UPDATE usuarios SET contrasena = %s WHERE id = %s"
                query = "UPDATE usuarios SET contrasena = %s WHERE correo_electronico = %s"

                # Ejecuta la consulta
                DatabaseConnection.execute(query, (nueva_contraseña, user_id))
                return jsonify({"success": True, "message": "Contraseña cambiada con éxito."})
            else:
                return jsonify({"success": False, "message": "La nueva contraseña y la confirmación no coinciden."})

        return jsonify({"success": False, "message": "Error al cambiar la contraseña."})"""

"""@app.route('/guardar_servidor', methods=['POST'])
    def guardar_servidor():
        if 'user_id' in session:
            user_id = session['user_id']
            nombre_servidor = request.form.get('nombreServidor')

            # Verifica si el servidor ya existe para evitar duplicados
            query = "SELECT id FROM servidores WHERE nombre_servidor = %s"
            result = DatabaseConnection.fetch_one(query, (nombre_servidor,))

            if result:
                flash("El servidor ya existe.", "error")
            else:
                # Insertar el servidor en la base de datos
                query = "INSERT INTO servidores (nombre_servidor, propietario_id) VALUES (%s, %s)"
                values = (nombre_servidor, user_id)
                try:
                    query = "INSERT INTO servidores (nombre_servidor, propietario_id) VALUES (%s, %s)"
                    values = (nombre_servidor, user_id)
                    DatabaseConnection.execute(query, values)
                    flash("Servidor creado con éxito.", "success")

                    # Realizar un commit para confirmar los cambios en la base de datos
                    DatabaseConnection.get_connection().commit()

                    flash("Servidor creado con éxito.", "success")

                    # Devolver una respuesta JSON para indicar el éxito de la operación
                    response_data = {'success': True, 'message': 'Servidor creado con éxito.'}
                    return jsonify(response_data)
                except Exception as e:
                    flash("Error al crear el servidor. Por favor, inténtalo nuevamente.", "error")
                    print("Error de base de datos:", str(e))
                    # Realiza un rollback en caso de error
                    DatabaseConnection.get_connection().rollback()

        # Si algo sale mal, devolver una respuesta JSON con un mensaje de error
        response_data = {'success': False, 'message': 'Error al guardar el servidor.'}
        return jsonify(response_data), 400
        #return redirect(url_for('login_p'))
"""
"""@app.route('/guardar_servidor', methods=['POST'])
    def guardar_servidor():
        try:
            if 'user_id' in session:
                correo_electronico = session.get('user_id')

                # Define la consulta SQL para obtener el ID del usuario
                query = "SELECT id FROM usuarios WHERE correo_electronico = %s"
                
                # Ejecuta la consulta
                result = DatabaseConnection.fetch_one(query, (correo_electronico,))
                
                # Verifica si se encontró un usuario con el correo electrónico
                if result is not None:
                    user_id = result[0]  # Obtiene el ID del usuario desde el resultado de la consulta

                    data = request.get_json()

                    # Verifica si el servidor ya existe para evitar duplicados
                    query = "SELECT id FROM servidores WHERE nombre_servidor = %s"
                    result = DatabaseConnection.fetch_one(query, (data.get('nombreServidor'),))

                    if result:
                        response_data = {'success': False, 'message': 'El servidor ya existe.'}
                    else:
                        # Insertar el servidor en la base de datos, incluyendo el propietario_id
                        query = "INSERT INTO servidores (nombre_servidor, descripcion, propietario_id) VALUES (%s, %s, %s)"
                        values = (data.get('nombreServidor'), data.get('descripcion'), user_id)
                        DatabaseConnection.execute(query, values)
                        DatabaseConnection.get_connection().commit()
                        response_data = {'success': True, 'message': 'Servidor creado con éxito.'}
                else:
                    response_data = {'success': False, 'message': 'Usuario no encontrado.'}
            else:
                response_data = {'success': False, 'message': 'Usuario no autenticado.'}

        except Exception as e:
            response_data = {'success': False, 'message': 'Error al guardar el servidor.'}
            print("Error de base de datos:", str(e))
            DatabaseConnection.get_connection().rollback()

        return jsonify(response_data)
"""
"""@app.route('/guardar_servidor', methods=['POST'])
    def guardar_servidor():
        try:
            if 'user_id' in session:
                # Obtener el ID del usuario desde la sesión
                user_id = session.get('user_id')

                if user_id.isdigit():
                    user_id = int(user_id)
                    print(f"user_id: {user_id}")
                else:
                    user_id = None

                # Obtener los datos JSON de la solicitud
                data = request.get_json()
                print(f"data: {data}")

                if 'nombreServidor' in data:
                    nombre_servidor = data['nombreServidor']
                    print(f"nombre_servidor: {nombre_servidor}")

                    # Verificar si el servidor ya existe para evitar duplicados
                    query = "SELECT id FROM servidores WHERE nombre_servidor = %s"
                    result = DatabaseConnection.fetch_one(query, (nombre_servidor,))

                    if result:
                        response_data = {'success': False, 'message': 'El servidor ya existe.'}
                    else:
                        # Insertar el servidor en la base de datos con el propietario_id
                        query = "INSERT INTO servidores (nombre_servidor, propietario_id) VALUES (%s, %s)"
                        values = (nombre_servidor, user_id)
                        DatabaseConnection.execute(query, values)
                        DatabaseConnection.get_connection().commit()
                        response_data = {'success': True, 'message': 'Servidor creado con éxito.'}
                else:
                    response_data = {'success': False, 'message': 'Nombre de servidor no proporcionado.'}

            else:
                user_id = None
                response_data = {'success': False, 'message': 'Usuario no autenticado.'}

        except Exception as e:
            response_data = {'success': False, 'message': 'Error al guardar el servidor.'}
            print("Error de base de datos:", str(e))
            DatabaseConnection.get_connection().rollback()

        return jsonify(response_data)"""

"""@app.route('/crear_canal', methods=['POST'])
    def crear_canal():
        if 'user_id' in session:
            user_id = session['user_id']
            nombre_canal = request.form.get('nombreCanal')
            nombre_servidor = request.form.get('nombreServidor')

            if nombre_canal and nombre_servidor:
                # Obtén el ID del servidor basado en el nombre
                servidor_id = obtener_servidor_id_por_nombre(nombre_servidor)

                if servidor_id is not None:
                    # Inserta el nuevo canal en la base de datos con el servidor_id
                    query = "INSERT INTO canales (nombre_canal, servidor_id) VALUES (%s, %s)"
                    values = (nombre_canal, servidor_id)
                    DatabaseConnection.execute(query, values)
                    DatabaseConnection.get_connection().commit()
                    response_data = {'success': True, 'message': 'Canal creado con éxito.'}
                else:
                    response_data = {'success': False, 'message': 'El servidor no fue encontrado.'}
            else:
                response_data = {'success': False, 'message': 'Nombre de canal o servidor no proporcionado.'}
        else:
            response_data = {'success': False, 'message': 'Usuario no autenticado.'}

        return jsonify(response_data)"""