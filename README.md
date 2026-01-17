# G-Thread Finder 📧

**G-Thread Finder** es una aplicación de escritorio moderna y segura diseñada para filtrar y visualizar historiales de conversación de Gmail. Permite buscar hilos completos con un destinatario específico, visualizar el contenido rico (HTML + Imágenes) y exportar el historial limpio para reportes.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Características Principales

*   **🔍 Filtrado Inteligente**: Busca conversaciones específicas por correo de destinatario y palabras clave.
*   **🎨 Diseño Material Design 3**: Interfaz limpia, moderna y responsiva.
*   **📑 Lectura Completa**: Visualiza correos con formato HTML original e imágenes integradas.
*   **📋 Portapapeles Avanzado**:
    *   **Copia Individual**: Copia el contenido de un correo manteniendo el formato para pegar en Word/Docs.
    *   **Copia Historial Completo**: Descarga y une *todos* los correos del hilo en un solo bloque formateado.
*   **🧹 Limpieza de Firmas**: Elimina automáticamente las firmas de Gmail para un reporte más limpio.
*   **🔐 Seguridad OAuth 2.0**: Autenticación directa con Google sin almacenar contraseñas.
*   **🚀 Standalone**: Ejecutable `.exe` portable (no requiere instalación de Python).

## 🛠️ Instalación y Requisitos

### Opción 1: Ejecutable (Windows)
1.  Descarga la última versión desde la sección de [Releases](https://github.com/strix07/gestor-de-correos/releases) (si disponible).
2.  **Requisito Crítico**: Necesitas un archivo `credentials.json` de Google Cloud Platform.
    *   Crea un proyecto en GCP.
    *   Habilita la **Gmail API**.
    *   Crea credenciales OAuth 2.0 (Desktop App).
    *   Descarga el JSON y colócalo en la **misma carpeta** que el `.exe`.

### Opción 2: Correr desde Código
Requisitos: Python 3.x, pip.

1.  Clonar repositorio:
    ```bash
    git clone https://github.com/strix07/gestor-de-correos.git
    cd gestor-de-correos
    ```
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Colocar `credentials.json` en la raíz del proyecto.
4.  Ejecutar:
    ```bash
    python main.py
    ```

## 🏗️ Construir el .exe
Si deseas compilar tu propia versión:
```bash
pyinstaller --noconfirm --onefile --windowed --add-data "templates;templates" --add-data "static;static" --name "GThreadFinder" main.py
```

## 📄 Licencia
Este proyecto está bajo la Licencia MIT.
