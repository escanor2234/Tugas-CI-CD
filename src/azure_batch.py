import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from azure.core import MatchConditions
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobClient, ContentSettings

from .scraper import ambil_batch

logger = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    account = os.environ["STORAGE_ACCOUNT"]
    container = os.environ["BLOB_CONTAINER"]
    name = "data_saham_2menit.csv"
    with ManagedIdentityCredential(
        identity_config={"resource_id": os.environ["MANAGED_IDENTITY_ID"]},
    ) as credential, BlobClient(
        f"https://{account}.blob.core.windows.net", container, name, credential=credential,
    ) as blob, TemporaryDirectory() as workdir:
        csv = Path(workdir) / name
        try:
            etag = blob.get_blob_properties().etag
        except ResourceNotFoundError:
            etag = None

        if etag is not None:
            with csv.open("wb") as stream:
                blob.download_blob(etag=etag, match_condition=MatchConditions.IfNotModified).readinto(stream)

        if not ambil_batch(csv):
            return 1

        # First write is create-only; an update requires the ETag we downloaded.
        condition = {} if etag is None else {
            "etag": etag, "match_condition": MatchConditions.IfNotModified,
        }
        with csv.open("rb") as stream:
            blob.upload_blob(
                stream, overwrite=etag is not None,
                content_settings=ContentSettings(content_type="text/csv"), **condition,
            )
        logger.info("CSV tersimpan di %s/%s/%s", account, container, name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
