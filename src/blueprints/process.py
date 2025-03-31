import logging
from dataclasses import dataclass

from pydantic import BaseModel
from quart import Blueprint, abort, current_app
from quart_schema import DataSource, validate_request, validate_response
from quart_schema.pydantic import File

from library.extensions import pdf_loader
from service import InvoiceData, InvoiceService, Pdf2ImgService

from .background_task import cleanup_temp_files

bp = Blueprint("process", __name__, url_prefix="/process")

logger = logging.getLogger(__name__)


@dataclass
class Rqst(BaseModel):
    document: File


@bp.route("/", methods=["POST"])
@validate_request(Rqst, source=DataSource.FORM_MULTIPART)
@validate_response(InvoiceData, 201)
async def post(rqest: Rqst) -> tuple:
    # document = (await request.files).get("file", None)
    logger.info(f"rqest.document.filename {rqest.document.filename}")
    if rqest.document is None or rqest.document.filename is None:
        logger.error("Uploaded files is not valid...")
        return abort(403, "Invalid File Object")

    uploaded_file = await pdf_loader.save(rqest.document)
    logger.info(f"Uploaded files {uploaded_file} ...")
    image_directory = await Pdf2ImgService.convert(uploaded_file)  # Use await here
    logger.info(f"Converted to Images {image_directory.name!s} ...")
    data, dadta_str = await InvoiceService.run(image_directory)  # Await if it's async
    logger.info("Agents Completed Extraction ...")
    if current_app.config.get("CLEANUP_TEMP_FILES", False):
        current_app.add_background_task(cleanup_temp_files, [uploaded_file, image_directory])
    return data, 201
