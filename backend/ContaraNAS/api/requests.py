from pydantic import BaseModel


class PairRequest(BaseModel):
    """Request to pair with the NAS"""

    pairing_code: str
