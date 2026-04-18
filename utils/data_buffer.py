"""
Data Buffer Manager for handling dynamic data buffers
"""

import time
import pandas as pd
from typing import Optional, Dict
from config.constants import BUFFER_PREFIX


class DataBufferManager:
    """
    Manages dynamic data buffers for historical market data.
    Creates variables with consistent naming pattern and handles automatic
    buffer switching and data loading.
    """

    def __init__(self, buffer_prefix: str = BUFFER_PREFIX):
        """
        Initialize the buffer manager.

        Args:
            buffer_prefix: Common prefix for all buffer variable names
        """
        self.buffers: Dict[str, pd.DataFrame] = {}
        self.buffer_prefix = buffer_prefix
        self.current_buffer_index = -1  # -1 means no buffer yet
        self.current_position = 0  # Current reading position in active buffer
        self.pending_load = False  # Indicates if a load is in progress
        self.last_load_attempt_time = 0.0  # Timestamp of last load attempt

    def create_new_buffer(self, data: pd.DataFrame) -> str:
        """
        Create a new buffer with unique name and store the data.

        Args:
            data: DataFrame to store in the new buffer

        Returns:
            Name of the created buffer
        """
        # Generate unique buffer name
        new_index = len(self.buffers)
        buffer_name = f"{self.buffer_prefix}_{new_index}"

        # Store the data
        self.buffers[buffer_name] = data.copy()

        # If this is the first buffer, set it as current
        if self.current_buffer_index == -1:
            self.current_buffer_index = new_index
            self.current_position = 0

        return buffer_name

    def get_current_buffer(self) -> Optional[pd.DataFrame]:
        """
        Get the currently active buffer.

        Returns:
            DataFrame of current buffer or None if no buffer exists
        """
        if self.current_buffer_index == -1:
            return None

        buffer_name = f"{self.buffer_prefix}_{self.current_buffer_index}"
        return self.buffers.get(buffer_name)

    def get_remaining_data(self) -> int:
        """
        Count remaining data points in the current buffer.

        Returns:
            Number of remaining data points
        """
        current_buffer = self.get_current_buffer()
        if current_buffer is None:
            return 0

        return len(current_buffer) - self.current_position

    def advance_to_next_buffer(self) -> bool:
        """
        Switch to the next buffer if available.

        Returns:
            True if successfully switched, False if no next buffer
        """
        next_index = self.current_buffer_index + 1
        next_buffer_name = f"{self.buffer_prefix}_{next_index}"

        if next_buffer_name in self.buffers:
            self.current_buffer_index = next_index
            self.current_position = 0
            return True

        return False

    def get_current_data_point(self) -> Optional[Dict]:
        """
        Get the current data point and advance the position.

        Returns:
            Dictionary containing the current data point or None if exhausted
        """
        current_buffer = self.get_current_buffer()
        if current_buffer is None:
            return None

        if self.current_position >= len(current_buffer):
            return None

        data_point = current_buffer.iloc[self.current_position].to_dict()
        self.current_position += 1

        return data_point

    def should_load_new_data(self, threshold: int) -> bool:
        """
        Check if new data should be loaded based on threshold.

        Args:
            threshold: Minimum remaining data points before loading

        Returns:
            True if new data should be loaded
        """
        if self.pending_load:
            return False  # Already loading

        remaining = self.get_remaining_data()
        return remaining <= threshold and remaining > 0

    def mark_load_pending(self):
        """Mark that a data load operation is in progress."""
        self.pending_load = True
        self.last_load_attempt_time = time.time()

    def confirm_load_success(self, data: pd.DataFrame) -> str:
        """
        Confirm successful data load and create new buffer.

        Args:
            data: Successfully loaded data

        Returns:
            Name of the created buffer
        """
        self.pending_load = False
        return self.create_new_buffer(data)

    def mark_load_failed(self):
        """Mark that the load operation failed (allows retry)."""
        self.pending_load = False

    def get_buffer_stats(self) -> Dict:
        """
        Get statistics about the buffer manager state.

        Returns:
            Dictionary with buffer statistics
        """
        return {
            'total_buffers': len(self.buffers),
            'current_buffer_index': self.current_buffer_index,
            'current_position': self.current_position,
            'remaining_in_current': self.get_remaining_data(),
            'pending_load': self.pending_load,
            'current_buffer_name': f"{self.buffer_prefix}_{self.current_buffer_index}" if self.current_buffer_index >= 0 else None
        }

    def has_data(self) -> bool:
        """Check if there is any data available to process."""
        return len(self.buffers) > 0 and self.current_buffer_index >= 0
