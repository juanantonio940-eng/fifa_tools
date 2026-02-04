import base64
import requests
import json
from typing import Optional, Union
from pathlib import Path
from PIL import Image
from io import BytesIO
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnyticketsFulfillmentAPI:
    """
    Cliente para la API de Fulfillment de Anytickets.
    Gestiona la carga de pruebas y confirmación de pedidos.
    """

    BASE_URL = "https://any-catchall.com/api/v1"

    def __init__(self, bearer_token: str, dev_token: str):
        """
        Inicializar cliente de Anytickets.

        Args:
            bearer_token: Token de autenticación Bearer
            dev_token: Token de desarrollo para funciones avanzadas
        """
        self.bearer_token = bearer_token
        self.dev_token = dev_token
        self.session = requests.Session()
        self._setup_headers()

    def _setup_headers(self):
        """Configurar headers comunes para todas las peticiones."""
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'DevToken': self.dev_token,
            'Content-Type': 'application/json'
        }

    # ========================
    # UTILIDADES - Conversión a Base64
    # ========================

    @staticmethod
    def image_file_to_base64(file_path: str) -> str:
        """
        Convertir archivo de imagen local a Base64.

        Args:
            file_path: Ruta del archivo de imagen

        Returns:
            String en formato data URL con Base64

        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el archivo no es una imagen válida
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        # Validar que sea una imagen
        valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        if file_path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Formato no soportado. Usa: {', '.join(valid_extensions)}")

        # Leer y convertir a Base64
        with open(file_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_string = base64.b64encode(image_data).decode('utf-8')

        # Determinar MIME type
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(file_path.suffix.lower(), 'image/png')

        return f"data:{mime_type};base64,{base64_string}"

    @staticmethod
    def image_url_to_base64(image_url: str) -> str:
        """
        Descargar imagen desde URL y convertir a Base64.

        Args:
            image_url: URL de la imagen

        Returns:
            String en formato data URL con Base64

        Raises:
            requests.RequestException: Si hay error descargando la imagen
        """
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Validar que sea una imagen
            content_type = response.headers.get('content-type', 'image/png')
            if 'image' not in content_type:
                raise ValueError(f"URL no contiene una imagen válida: {content_type}")

            # Convertir a Base64
            base64_string = base64.b64encode(response.content).decode('utf-8')
            return f"data:{content_type};base64,{base64_string}"

        except requests.RequestException as e:
            logger.error(f"Error descargando imagen desde {image_url}: {e}")
            raise

    @staticmethod
    def bytes_to_base64(image_bytes: bytes, mime_type: str = 'image/png') -> str:
        """
        Convertir bytes de imagen a Base64.

        Args:
            image_bytes: Bytes de la imagen
            mime_type: Tipo MIME de la imagen

        Returns:
            String en formato data URL con Base64
        """
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        return f"data:{mime_type};base64,{base64_string}"

    # ========================
    # PASO 1: UPLOAD PROOF
    # ========================

    def upload_static_proof(self, invoice_id: int, proof_file: str) -> dict:
        """
        Subir prueba estática (captura de pantalla en Base64).

        Args:
            invoice_id: ID de la factura/pedido
            proof_file: Imagen en formato data URL Base64

        Returns:
            Respuesta de la API con URL de la prueba

        Raises:
            requests.RequestException: Error en la petición
            ValueError: Datos inválidos
        """
        if not isinstance(invoice_id, int) or invoice_id <= 0:
            raise ValueError("invoice_id debe ser un número positivo")

        if not proof_file.startswith('data:'):
            raise ValueError("proof_file debe estar en formato data URL Base64")

        url = f"{self.BASE_URL}/fulfillment/upload/static"
        payload = {
            "InvoiceId": invoice_id,
            "ProofFile": proof_file
        }

        try:
            logger.info(f"Subiendo prueba estática para factura {invoice_id}")
            response = self.session.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Prueba subida exitosamente. URL: {data.get('url')}")
            return data

        except requests.RequestException as e:
            logger.error(f"Error subiendo prueba estática: {e}")
            raise

    def upload_transfer_link(self, invoice_id: int, transfer_link: str) -> dict:
        """
        Subir URL de transferencia móvil.

        Args:
            invoice_id: ID de la factura/pedido
            transfer_link: URL de la transferencia (ej: Ticketmaster, StubHub)

        Returns:
            Respuesta de la API con URL de la prueba

        Raises:
            requests.RequestException: Error en la petición
            ValueError: Datos inválidos
        """
        if not isinstance(invoice_id, int) or invoice_id <= 0:
            raise ValueError("invoice_id debe ser un número positivo")

        if not isinstance(transfer_link, str) or not transfer_link.startswith('http'):
            raise ValueError("transfer_link debe ser una URL válida")

        url = f"{self.BASE_URL}/fulfillment/upload/link"
        payload = {
            "InvoiceId": invoice_id,
            "Link": transfer_link
        }

        try:
            logger.info(f"Subiendo link de transferencia para factura {invoice_id}")
            response = self.session.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Link subido exitosamente. URL: {data.get('url')}")
            return data

        except requests.RequestException as e:
            logger.error(f"Error subiendo link de transferencia: {e}")
            raise

    # ========================
    # PASO 2: CONFIRM FULFILLMENT
    # ========================

    def confirm_fulfillment(
            self,
            invoice_id: int,
            proof_url: Optional[str] = None,
            transfer_link: Optional[str] = None,
            marketplace: str = 'general',
            transfer_source: Optional[str] = None
    ) -> dict:
        """
        Confirmar fulfillment del pedido en el marketplace.

        Args:
            invoice_id: ID de la factura/pedido
            proof_url: URL de la prueba (del upload/static)
            transfer_link: URL de transferencia (del upload/link)
            marketplace: Marketplace destino ('general', 'gotickets')
            transfer_source: REQUERIDO para GoTickets si usas proof_url

        Returns:
            Respuesta de la API

        Raises:
            requests.RequestException: Error en la petición
            ValueError: Datos inválidos
        """
        # Validaciones
        if not isinstance(invoice_id, int) or invoice_id <= 0:
            raise ValueError("invoice_id debe ser un número positivo")

        if not proof_url and not transfer_link:
            raise ValueError("Debes proporcionar proof_url o transfer_link")

        if proof_url and transfer_link:
            raise ValueError("No puedes proporcionar ambos: proof_url y transfer_link")

        if marketplace == 'gotickets' and proof_url and not transfer_source:
            raise ValueError("transfer_source es requerido para GoTickets con proof_url")

        url = f"{self.BASE_URL}/fulfillment/confirm"
        payload = {"InvoiceId": invoice_id}

        if proof_url:
            payload["ProofUrl"] = proof_url

        if transfer_link:
            payload["Link"] = transfer_link

        if transfer_source and marketplace == 'gotickets':
            payload["TransferSource"] = transfer_source

        try:
            logger.info(f"Confirmando fulfillment para factura {invoice_id}")
            response = self.session.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Fulfillment confirmado exitosamente")
            return data

        except requests.RequestException as e:
            logger.error(f"Error confirmando fulfillment: {e}")
            raise

    # ========================
    # FLUJO COMPLETO
    # ========================

    def complete_fulfillment(
            self,
            invoice_id: int,
            image_source: Union[str, bytes],
            source_type: str = 'file',
            marketplace: str = 'general',
            transfer_source: Optional[str] = None,
            skip_confirm: bool = False
    ) -> dict:
        """
        Flujo completo de fulfillment (upload + confirm).

        Args:
            invoice_id: ID de la factura
            image_source:
                - Si source_type='file': ruta del archivo
                - Si source_type='url': URL de la imagen
                - Si source_type='bytes': bytes de la imagen
            source_type: Tipo de fuente ('file', 'url', 'bytes')
            marketplace: Marketplace destino
            transfer_source: REQUERIDO para GoTickets
            skip_confirm: Si True, solo sube la imagen sin confirmar

        Returns:
            Respuesta final de confirmación

        Raises:
            ValueError: Datos inválidos
            requests.RequestException: Error en la petición
        """
        logger.info(f"Iniciando fulfillment completo para factura {invoice_id}")

        try:
            # Paso 1: Convertir imagen a Base64
            if source_type == 'file':
                proof_file = self.image_file_to_base64(image_source)
            elif source_type == 'url':
                proof_file = self.image_url_to_base64(image_source)
            elif source_type == 'bytes':
                proof_file = self.bytes_to_base64(image_source)
            else:
                raise ValueError(f"source_type no válido: {source_type}")

            # Paso 2: Subir prueba
            upload_response = self.upload_static_proof(invoice_id, proof_file)
            proof_url = upload_response.get('url')

            if not proof_url:
                raise ValueError("No se recibió URL de prueba en la respuesta")

            # Paso 3: Confirmar fulfillment (opcional)
            if skip_confirm:
                logger.info(f"Imagen subida exitosamente (sin confirmar) para factura {invoice_id}")
                return {
                    'success': True,
                    'invoice_id': invoice_id,
                    'proof_url': proof_url,
                    'confirmation': {'code': 'upload_only'}
                }

            confirm_response = self.confirm_fulfillment(
                invoice_id=invoice_id,
                proof_url=proof_url,
                marketplace=marketplace,
                transfer_source=transfer_source
            )

            logger.info(f"Fulfillment completado exitosamente para factura {invoice_id}")
            return {
                'success': True,
                'invoice_id': invoice_id,
                'proof_url': proof_url,
                'confirmation': confirm_response
            }

        except Exception as e:
            logger.error(f"Error en fulfillment completo: {e}")
            return {
                'success': False,
                'invoice_id': invoice_id,
                'error': str(e)
            }

    def close(self):
        """Cerrar sesión."""
        self.session.close()


# Contexto manager para uso seguro
class AnyTicketsClient:
    """Context manager para Anytickets API."""

    def __init__(self, bearer_token: str, dev_token: str):
        self.client = AnyticketsFulfillmentAPI(bearer_token, dev_token)

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()

    BEARER_TOKEN = os.getenv('ANYTICKETS_BEARER_TOKEN')
    DEV_TOKEN = os.getenv('ANYTICKETS_DEV_TOKEN')

    if not BEARER_TOKEN or not DEV_TOKEN:
        print("Error: Configura ANYTICKETS_BEARER_TOKEN y ANYTICKETS_DEV_TOKEN")
        exit(1)

    # Ejemplo de uso
    with AnyTicketsClient(BEARER_TOKEN, DEV_TOKEN) as client:
        # client.complete_fulfillment(invoice_id=123, image_source='ruta/imagen.png')
        print("Cliente inicializado correctamente")