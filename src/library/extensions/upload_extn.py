from quart_uploads import UploadSet

pdf_loader = UploadSet(name="pdf", extensions=("pdf", "PDF"))
