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
    cursor.execute("SELECT id, usuario, password FROM usuarios WHERE usuario = ?", (usuario,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        stored_password = user_data[2]
        hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
        if hashed_input_password == stored_password:
            return True, user_data[1]  # Retorna True y el nombre de usuario
    return False, "Credenciales incorrectas."

def main(page: ft.Page):
    page.title = "Mi Aplicación"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 350
    page.window_height = 500

    create_tables()
    current_user: Optional[str] = None

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
    home_nombre_usuario = ft.Text("")
    home_cerrar_sesion_icono = ft.IconButton(ft.Icons.LOGOUT, on_click=lambda _: page.go("/login"))
    home_view = ft.Column(
        [
            ft.Row([home_nombre_usuario, ft.Container(expand=True), home_cerrar_sesion_icono], alignment=ft.MainAxisAlignment.END),
            ft.Text("¡Bienvenido a la página de inicio!", size=20),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
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
            home_nombre_usuario.value = f"Hola, {current_user}"
            page.views.append(
                ft.View(
                    "/home",
                    [home_view],
                    padding=ft.padding.all(30),
                )
            )
        page.update()

    def ir_a_registro(e):
        page.go("/register")

    def ir_a_login(e):
        page.go("/login")

    def manejar_login(e):
        nonlocal current_user
        success, message = verificar_usuario(login_usuario.value, login_password.value)
        if success:
            current_user = message
            login_mensaje.value = ""
            page.go("/home")
        else:
            login_mensaje.value = message
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

    login_registro_link.on_click = ir_a_registro
    registro_login_link.on_click = ir_a_login
    login_boton.on_click = manejar_login
    registro_boton.on_click = manejar_registro

    page.on_route_change = actualizar_vista
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)