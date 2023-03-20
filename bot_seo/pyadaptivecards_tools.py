""" Extensions and hacks for pyadaptivecards. """
from typing import Literal, List, Optional

from pyadaptivecards.abstract_components import Serializable
import pyadaptivecards.container
import pyadaptivecards.components


class Column(pyadaptivecards.components.Column):
    def __init__(
        self,
        items=None,
        separator=None,
        spacing=None,
        selectAction=None,
        style=None,
        verticalContentAlignment=None,
        horizontalAlignment=None,
        width=None,
        id=None,
    ):
        super().__init__(
            items=items,
            separator=separator,
            spacing=spacing,
            selectAction=selectAction,
            style=style,
            verticalContentAlignment=verticalContentAlignment,
            width=width,
            id=id,
        )
        self.horizontalAlignment = horizontalAlignment

        self.simple_properties.append("horizontalAlignment")


class Container(pyadaptivecards.container.Container):
    def __init__(
        self,
        items,
        selectAction=None,
        style=None,
        verticalContentAlignment=None,
        height=None,
        separator=None,
        spacing=None,
        isVisible=None,
        id=None,
    ):
        super().__init__(
            items,
            selectAction=selectAction,
            style=style,
            verticalContentAlignment=verticalContentAlignment,
            height=height,
            separator=separator,
            spacing=spacing,
            id=id,
        )
        self.isVisible = isVisible

        self.simple_properties.append("isVisible")


class ToggleVisibility(Serializable):
    def __init__(
        self,
        *,
        title: Optional[str] = None,
        iconURL: Optional[str] = None,
        style: Optional[Literal["positive", "negative"]] = None,
        isPrimary: Optional[bool] = None,
        targetElements: Optional[List[Serializable]] = None,
        id: Optional[str] = None,
    ):
        self.type = "Action.ToggleVisibility"
        self.title = title
        self.iconURL = iconURL
        self.style = style
        self.isPrimary = isPrimary
        self._targetElements = targetElements
        self.id = id
        super().__init__(
            serializable_properties=[],
            simple_properties=[
                "id",
                "type",
                "title",
                "iconURL",
                "style",
                "isPrimary",
                "targetElements",
            ],
        )

    @property
    def targetElements(self):
        return [target.id for target in self._targetElements]


class ActionSet(Serializable):
    def __init__(
        self,
        actions: List[Serializable],
        isVisible: Optional[bool] = None,
        spacing: Optional[str] = None,
        separator: Optional[bool] = None,
        horizontalAlignment: Optional[str] = None,
        id: Optional[str] = None,
    ):
        self.type = "ActionSet"
        self.actions = actions
        self.isVisible = isVisible
        self.spacing = spacing
        self.separator = separator
        self.horizontalAlignment = horizontalAlignment
        self.id = id

        super().__init__(
            serializable_properties=["actions"],
            simple_properties=[
                "isVisible",
                "spacing",
                "separator",
                "horizontalAlignment",
                "id",
                "type",
            ],
        )
