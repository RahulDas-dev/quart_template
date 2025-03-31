from application import InvoiceInferApp


def register_app(app: InvoiceInferApp) -> None:
    if app.config.get("DEBUG", False) is False:
        import warnings

        warnings.simplefilter("ignore", ResourceWarning)
