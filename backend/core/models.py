from uuid import uuid4

from django.db import models


class BaseModel(models.Model):
    """ Overwrite standard model to use UUID as primary key """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampedModel(BaseModel):
    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)
    # A timestamp representing when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        # default ordering
        ordering = ["-created_at", "-updated_at"]


# limit queryset chunk
class LimitedQueryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().iterator(chunk_size=400)


class LimitedQueryChunk(models.Model):
    object = models.Manager()
    chunk_objects = LimitedQueryManager()

    class Meta:
        abstract = True
