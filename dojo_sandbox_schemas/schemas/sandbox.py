"""Module containing Sandbox related schemas.
There is a clear distinction between Sandbox schemas and Worker schemas.
Sandbox schemas are aware of what a challenge is, they know about inputs,
outputs, callbacks..."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from dojo_sandbox_schemas.schemas.workers import WorkerEnvironment, WorkerFile


class SandboxCallback(BaseModel):
    """Model representing a callback object that will allow
    the Sandbox worker to keep an external component updated
    about the Worker status
    """

    url: str
    """URL of the external component to call on status update"""

    token: Optional[str] = None
    """Optional token to pass on the HTTP call"""


class SandboxJobInput(BaseModel):
    """Model representing input sent to a Worker
    It bundles input sent to stdin, input sent as parameters
    and files uploaded to the worker
    """

    stdin: Optional[str] = None
    """Optional stdin"""

    parameters: Optional[list[str]] = None
    """Optional parameters to append to the command"""

    files: Optional[list[WorkerFile]] = None
    """Optional files to upload to the worker"""

    command: Optional[str] = None
    """Overrides the command used to execute the code
    Usually, this should stay equal to `None`
    """

    def combine(self, override: SandboxJobInput) -> SandboxJobInput:
        """Combines two `SandboxJobInput` into one, the object passed in
        parameter will take priority on "self".
        You can consider this method to be :
        `default_input.combine(override_input)`
        """
        return SandboxJobInput(
            stdin=override.stdin or self.stdin,
            parameters=override.parameters or self.parameters,
            files=override.files or self.files,
            command=override.command or self.command,
        )


class SandboxJobCreate(BaseModel):
    """Model representing the request required to create a Worker"""

    environment: WorkerEnvironment
    """Environment of the Worker, contains everything required for the Worker to
    properly execute (image, files, default command...)
    """

    base_input: SandboxJobInput = Field(default_factory=SandboxJobInput)
    """`SandboxJobInput` that will serve as default when not defined in an input.
    Each of the `SandboxJobInput` fields are equal to `None` by default,
    override it in the check to ignore the `base_input`.
    """

    inputs: dict[str, SandboxJobInput]
    """Dictionnary mapping check ids to `SandboxJobInput`.
    Each input executes the command with the given `SandboxJobInput`
    """

    user_files: list[WorkerFile] = []
    """Files uploaded by the user to solve the challenge.
    Usually contains a single file with the user solution
    (such as code.py, code.js...)
    """

    callback: Optional[SandboxCallback] = None
    """Callback that will be called each time the Worker status
    is updated"""

    timeout: int = 30
    """Timeout for the Sandbox Job execution in seconds, defaults to 30 seconds
    """

    class Config:
        orm_mode = True


class SandboxJobStatus(Enum):
    """Enum containing all possible status of the Sandbox Worker"""

    Pending = "Pending"
    Started = "Started"
    Failure = "Failure"
    Timeout = "Timeout"
    Success = "Success"


class SandboxJobOutput(BaseModel):
    stdout: str = ""
    """Content of stdout"""

    stderr: str = ""
    """Content of stderr"""

    files: list[WorkerFile] = []
    """Will contain every file that was required to be uploaded
    with the `WorkerInputFileType.Uploader` file type
    """

    duration: float
    """Time it took for the Worker to output this result"""


class SandboxJobState(BaseModel):
    id: str
    """Unique identifier of the `WorkerExecution`
    It can be used to poll the progress of the execution"""

    status: SandboxJobStatus
    """Status of the `WorkerExecution`"""

    environment: str
    """Unique identifier of the `WorkerEnvironment`"""

    details: Optional[str] = None
    """Detailed status of the Worker, will contain exceptions reasons if any"""

    outputs: Optional[dict[str, SandboxJobOutput]] = None
    """Dictionnary mapping inputs ids to their corresponding outputs"""
