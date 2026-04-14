from datetime import date
from typing import Annotated

from pydantic.functional_serializers import PlainSerializer

# A custom datetime.date annotation that allows custom serialization.
SerializedDate = Annotated[
    date, PlainSerializer(lambda x: x.isoformat(), return_type=str)
]
