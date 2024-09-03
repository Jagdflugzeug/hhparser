from pydantic import BaseModel, field_validator
from datetime import timedelta, datetime
import pytz


class HabrArticle(BaseModel):
    title: str
    hub: int
    post_link: str
    author_name: str
    author_link: str
    datetime_published: str

    @field_validator('datetime_published')
    def parse_datetime(cls, value):
        if isinstance(value, str):
            try:
                dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
                dt = dt.replace(tzinfo=pytz.UTC)
                return dt
            except ValueError as e:
                raise ValueError(f"Invalid datetime format: {e}")
        raise TypeError("Datetime must be a string")


class Hub(BaseModel):
    id: int
    name: str
    active: bool
    check_period: timedelta
    url: str

