import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from docetl.operations.base import BaseOperation
from docetl.operations.utils import RichLoopBar

from .conversation import Conversation
from .walker import DepthFirstGraphWithTreeBackupWalker


class ConversationOperation(BaseOperation):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    def syntax_check(self) -> None:
        pass

    def execute(
        self, input_data: List[Dict], is_build: bool = False
    ) -> Tuple[List[Dict], float]:
        """
        Executes the cluster operation on the input data. Modifies the
        input data and returns it in place.

        Args:
            input_data (List[Dict]): A list of dictionaries to process.
            is_build (bool): Whether the operation is being executed
              in the build phase. Defaults to False.

        Returns:
            Tuple[List[Dict], float]: A tuple containing the
              list of conversation outputs and the total cost of the operation.
        """
        if not input_data:
            return input_data, 0

        kw = dict(self.config)
        kw.pop("name")
        kw.pop("type")
        documents_source = kw.pop("documents", None)
        if documents_source is None:
            documents = input_data
        else:
            documents = self.runner.datasets[documents_source].load()
        walker = DepthFirstGraphWithTreeBackupWalker(input_data, **kw)
        output = []

        conv = Conversation(
            self.console,
            documents,
            walker,
            **kw)
        
        for utterance in conv:
            output.append(utterance)
        
        return output, 0
