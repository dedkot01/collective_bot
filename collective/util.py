from pathlib import Path
import uuid

from amzqr import amzqr


def gen_qr_file(words: str) -> Path:
    path = Path(f'/tmp/{uuid.uuid1()}.png')
    amzqr.run(
        words,
        # picture='collective/img/logo.jpg',
        save_name=path.as_posix(),
    )
    return path
