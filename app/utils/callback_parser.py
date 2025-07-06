from typing import NamedTuple

class CallbackData(NamedTuple):
    action: str | None
    entity: str | None
    id: int | None

def parse_callback_data(data: str) -> CallbackData:
    try:
        action, entity, obj_id = data.split(':')
        return CallbackData(action, entity, int(obj_id))
    except ValueError:
        return CallbackData(None, None, None)

def make_callback_data(action: str | CallbackData, entity: str = "", obj_id: int = 0) -> str:
    if isinstance(action, CallbackData):
        return f"{action.action}:{action.entity}:{action.id}"
    return f"{action}:{entity}:{obj_id}"