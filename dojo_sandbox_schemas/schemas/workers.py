"""Module containing Sandbox related schemas.
There is a clear distinction between Sandbox schemas and Worker schemas.
Worker schemas are aware of what an environment and files are but do not
care about inputs, parameters..."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class WorkerFileType(Enum):
    """Enum representing the type of a Worker file"""

    File = "File"
    """Simple file type"""

    Directory = "Directory"
    """Simple directory type"""

    Downloader = "Downloader"  # TODO: to implement
    """Downloads a file from outside"""

    Uploader = "Uploader"
    """Does not create the file, uploads it after
    the execution is over
    """


class WorkerFile(BaseModel):
    """Model representing a file uploaded to a Worker"""

    path: str
    """File path"""

    type: WorkerFileType
    """File type"""

    permissions: int = 644  # TODO: to implement
    """File / Directory permissions"""

    data: str | None = None
    """Data of the file
    Will be treated differently depending of the file type :

    - File: base64 encoded file content
    - Directory: ignored
    - Downloader: file URL
    - Uploader: once the file is retrieved, equal to
                base64 encoded file content
    """


class WorkerEnvironment(BaseModel):
    id: str
    """Unique identifier of the environment"""

    image: str
    """Link to a Docker image uploaded to a repository"""

    image_pull_secret: str | None  # TODO: to implement
    """Optional secret used to pull the Docker image if private"""

    files: list[WorkerFile] = []
    """Files that are required by the environment.
    Usually not required if the user code is standalone.
    """

    command: str
    """Command that will be used to start the code"""

    requires_user_files: list[WorkerFile] | None = None  # TODO: to implement
    """Requirements for the user sent files
    Each entry in the `requires_user_files `list will act like a filter.
    It will try to match using the `path` attribute and then check if :
    - the file type is the same
    - the permissions are equal
    - the data is equal
    """
