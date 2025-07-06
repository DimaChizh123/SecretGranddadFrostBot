from typing import NamedTuple

class CallbackData(NamedTuple):
    action: str | None
    id: int | None
    id2: int | None

def parse_callback_data(data: str) -> CallbackData:
    try:
        action, obj_id, obj2_id = data.split(':')
        return CallbackData(action, int(obj_id), int(obj2_id))
    except ValueError:
        return CallbackData(None, None, None)

def make_callback_data(action: str | CallbackData, obj_id: int = 0, obj2_id: int = 0) -> str:
    if isinstance(action, CallbackData):
        return f"{action.action}:{action.id}:{action.id2}"
    return f"{action}:{obj_id}:{obj2_id}"