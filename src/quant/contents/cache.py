from abc import ABCMeta
from typing import Any

import streamlit as st


class CacheMemory(metaclass=ABCMeta):
    """Cache data to share it between pages of this run.

    A new page has to be inherited from this class to share memory.
    """

    name: str
    icon: str

    memory: dict[str, Any] = st.session_state

    @staticmethod
    def add_state(var: str, value: Any = None) -> None:
        """Add a variable to shared memory."""
        if var not in CacheMemory.memory:
            CacheMemory.memory[var] = value

    @staticmethod
    def change_state(var: str, value: Any) -> None:
        """Change the value in shared memory of the given variable."""
        assert var in CacheMemory.memory, f"Please make [{var}] first !"
        CacheMemory.memory[var] = value

    @staticmethod
    def get_state(var: str) -> Any:
        """Get the value of the given variable from shared memory."""
        assert var in CacheMemory.memory, f"There is no [{var}]."
        return CacheMemory.memory[var]
