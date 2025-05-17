import flet as ft
import sqlite3
from typing import Optional
import hashlib

DATABASE_NAME = "db.db"

def create_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            telefono TEXT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def agregar_usuario(usuario, telefono, email, password, rol):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, telefono, email, password, rol) VALUES (?, ?, ?, ?, ?)",
                       (usuario, telefono, email, hashed_password, rol))
        conn.commit()
        conn.close()
        return True, "Usuario registrado exitosamente."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "El usuario o el correo electrónico ya existen."

def verificar_usuario(usuario, password):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, password, telefono, email, rol FROM usuarios WHERE usuario = ?", (usuario,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        stored_password = user_data[2]
        hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
        if hashed_input_password == stored_password:
            return True, user_data  # Retorna True y todos los datos del usuario
    return False, "Credenciales incorrectas."

def obtener_usuario_por_nombre(usuario):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, telefono, email, rol FROM usuarios WHERE usuario = ?", (usuario,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def actualizar_usuario(usuario_original, nuevo_usuario, telefono, email, password):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("""
            UPDATE usuarios
            SET usuario = ?, telefono = ?, email = ?, password = ?
            WHERE usuario = ?
        """, (nuevo_usuario, telefono, email, hashed_password, usuario_original))
        conn.commit()
        conn.close()
        return True, "Perfil actualizado exitosamente."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "El nuevo usuario o correo electrónico ya existen."

def main(page: ft.Page):
    page.title = "Mi Aplicación"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 350
    page.window_height = 600 # Aumentar la altura para la vista de perfil

    create_tables()
    current_user_data: Optional[tuple] = None

    # Establecer la ruta inicial al cargar la aplicación
    page.route = "/login"

    # Controles para el formulario de Login
    login_usuario = ft.TextField(label="Usuario")
    login_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
    login_recordar = ft.Checkbox(label="Recordar contraseña")
    login_mensaje = ft.Text("", color=ft.Colors.RED_ACCENT_700)
    login_boton = ft.ElevatedButton("Iniciar Sesión")
    login_registro_link = ft.TextButton("¿No tienes cuenta? Regístrate aquí")

    # Controles para el formulario de Registro
    registro_usuario = ft.TextField(label="Usuario")
    registro_telefono = ft.TextField(label="Teléfono")
    registro_email = ft.TextField(label="Email")
    registro_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
    registro_confirmar_password = ft.TextField(label="Confirmar Contraseña", password=True, can_reveal_password=True)
    registro_rol = ft.Dropdown(
        label="Rol",
        options=[
            ft.dropdown.Option("Root"),
            ft.dropdown.Option("Administrador1"),
            ft.dropdown.Option("Administrador"),
        ],
        value="Administrador",  # Valor por defecto
    )
    registro_mensaje = ft.Text("", color=ft.Colors.RED_ACCENT_700)
    registro_boton = ft.ElevatedButton("Registrarse")
    registro_login_link = ft.TextButton("¿Ya tienes cuenta? Inicia sesión aquí")

    # Controles para la vista Home
    home_nombre_usuario = ft.TextButton(
        content=ft.Text(weight=ft.FontWeight.BOLD, size=18),
        on_click=lambda _: page.go("/profile") # Mantener el perfil en este icono por ahora
    )
    home_cerrar_sesion_icono = ft.IconButton(ft.Icons.LOGOUT, on_click=lambda _: page.go("/login"))
    home_contactos_icono = ft.IconButton(ft.Icons.PERSON, on_click=lambda _: page.go("/contacts"))
    home_view = ft.Column(
        [
            ft.Row(
                [
                    ft.Container(expand=True), # Empuja los elementos al extremo derecho
                    home_nombre_usuario,
                    home_contactos_icono,
                    ft.VerticalDivider(), # Separador vertical
                    home_cerrar_sesion_icono,
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            ft.Text("¡Bienvenido a la página de inicio!", size=20),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    # Controles para la vista de Perfil
    profile_usuario = ft.TextField(label="Usuario")
    profile_telefono = ft.TextField(label="Teléfono")
    profile_email = ft.TextField(label="Email")
    profile_password = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True)
    profile_confirmar_password = ft.TextField(label="Confirmar Nueva Contraseña", password=True, can_reveal_password=True)
    profile_mensaje = ft.Text("", color=ft.Colors.RED_ACCENT_700)
    profile_guardar_boton = ft.ElevatedButton("Guardar Cambios")
    profile_volver_boton = ft.TextButton("Volver al Inicio", on_click=lambda _: page.go("/home"))
    profile_view = ft.Column(
        [
            ft.Container(
                padding=ft.padding.all(30),
                content=ft.Column(
                    [
                        ft.Text("Editar Perfil", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                        profile_usuario,
                        profile_telefono,
                        profile_email,
                        profile_password,
                        profile_confirmar_password,
                        profile_mensaje,
                        profile_guardar_boton,
                        profile_volver_boton,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Controles para la vista de Contactos
    contactos_titulo = ft.Text("Mis Contactos", style=ft.TextThemeStyle.HEADLINE_SMALL)
    contactos_volver_boton = ft.ElevatedButton("Volver", on_click=lambda _: page.go("/home"))
    contactos_view = ft.Column(
        [
            contactos_titulo,
            ft.Text("¡Aquí estarán tus contactos!", size=16),
            contactos_volver_boton,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    def actualizar_vista(route):
        page.views.clear()
        if page.route == "/login":
            page.views.append(
                ft.View(
                    "/login",
                    [
                        ft.Text("Iniciar Sesión", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                        login_usuario,
                        login_password,
                        login_recordar,
                        login_mensaje,
                        login_boton,
                        login_registro_link,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    padding=ft.padding.all(30),
                )
            )
        elif page.route == "/register":
            page.views.append(
                ft.View(
                    "/register",
                    [
                        ft.Text("Registro de Usuario", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                        registro_usuario,
                        registro_telefono,
                        registro_email,
                        registro_password,
                        registro_confirmar_password,
                        registro_rol,
                        registro_mensaje,
                        registro_boton,
                        registro_login_link,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    padding=ft.padding.all(30),
                )
            )
        elif page.route == "/home":
            if current_user_data:
                home_nombre_usuario.content.value = current_user_data[1]
            page.views.append(
                ft.View(
                    "/home",
                    [home_view],
                    padding=ft.padding.only(top=10, right=10, left=30, bottom=30), # Reducir padding superior y derecho
                )
            )
        elif page.route == "/profile":
            if current_user_data:
                # Corregir la asignación de valores aquí
                profile_usuario.value = current_user_data[1]
                profile_telefono.value = current_user_data[3]
                profile_email.value = current_user_data[4]
                profile_password.value = "" # Limpiar campos de contraseña
                profile_confirmar_password.value = ""
                profile_mensaje.value = ""
            page.views.append(
                ft.View(
                    "/profile",
                    [profile_view],
                )
            )
        elif page.route == "/contacts":
            page.views.append(
                ft.View(
                    "/contacts",
                    [contactos_view],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    vertical_alignment=ft.MainAxisAlignment.CENTER,  # Añadido para centrar la vista
                    padding=ft.padding.all(30),
                )
            )
        page.update() # Añadido para actualizar la página después de cambiar la ruta

    def ir_a_registro(e):
        page.go("/register")

    def ir_a_login(e):
        page.go("/login")

    def manejar_login(e):
        nonlocal current_user_data
        success, user_data = verificar_usuario(login_usuario.value, login_password.value)
        if success:
            current_user_data = user_data
            login_mensaje.value = ""
            page.go("/home")
        else:
            login_mensaje.value = user_data # 'user_data' contiene el mensaje de error en caso de fallo
        page.update()

    def manejar_registro(e):
        if registro_password.value != registro_confirmar_password.value:
            registro_mensaje.value = "Las contraseñas no coinciden."
            page.update()
            return

        success, message = agregar_usuario(
            registro_usuario.value,
            registro_telefono.value,
            registro_email.value,
            registro_password.value,
            registro_rol.value,
        )
        if success:
            registro_mensaje.value = message
            page.go("/login")  # Redirigir al login después del registro exitoso
        else:
            registro_mensaje.value = message
        page.update()

    def guardar_perfil(e):
        nonlocal current_user_data
        if current_user_data is None:
            profile_mensaje.value = "No hay usuario autenticado."
            page.update()
            return

        if profile_password.value and profile_password.value != profile_confirmar_password.value:
            profile_mensaje.value = "Las nuevas contraseñas no coinciden."
            page.update()
            return

        nuevo_password = profile_password.value if profile_password.value else current_user_data[2] # Si no se ingresa nueva contraseña, se mantiene la anterior

        success, message = actualizar_usuario(
            current_user_data[1], # Usuario original
            profile_usuario.value,
            profile_telefono.value,
            profile_email.value,
            nuevo_password
        )
        if success:
            profile_mensaje.value = message
            # Recargar los datos del usuario actualizados
            current_user_data = obtener_usuario_por_nombre(profile_usuario.value)
            page.go("/home")
        else:
            profile_mensaje.value = message
        page.update()

    login_registro_link.on_click = ir_a_registro
    registro_login_link.on_click = ir_a_login
    login_boton.on_click = manejar_login
    registro_boton.on_click = manejar_registro
    profile_guardar_boton.on_click = guardar_perfil

    page.on_route_change = actualizar_vista
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)
