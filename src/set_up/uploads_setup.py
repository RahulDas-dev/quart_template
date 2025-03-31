from quart_uploads import configure_uploads

from application import InvoiceInferApp
from library.extensions import pdf_loader


def register_app(app: InvoiceInferApp) -> None:
    configure_uploads(app, pdf_loader)
