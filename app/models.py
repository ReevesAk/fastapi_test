from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Tasks(models.Model):
    """
    The Task model
    """

    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=100, unique=True)
    description = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_completed = fields.BooleanField(auto_now=True)

    def full_name(self) -> str:
        """
        Returns the task title
        """
        
        return self.title

    class PydanticMeta:
        ordering = ["title"]
        

Task_Pydantic = pydantic_model_creator(Tasks, name="Task")
TaskIn_Pydantic = pydantic_model_creator(Tasks, name="TaskIn", exclude_readonly=True)