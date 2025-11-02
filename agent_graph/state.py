from typing import Annotated, Literal, Optional

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """
    更新对话状态栈
    :param left:
    :param right:
    :return:
    """
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]

class State:
    """
        定义状态字典的结构
    """
    message: Annotated[list[AnyMessage], add_messages]
    user_info: str
    dialog_state: Annotated[
        list[
            Literal[
                "assistant",
                "update_flight",
                "book_car_rental",
                "book_hotel",
                "book_excursion",
            ]
        ],
        update_dialog_stack,
    ]