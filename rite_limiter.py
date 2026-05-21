import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_messages: int, time_window: float):
        self.max_messages = max_messages
        self.time_window = time_window
        self.users_history = defaultdict(list)

    def can_send(self, user_id: int) -> bool:
        current_time = time.time()
        history = self.users_history[user_id]

        while history and history[0] < current_time - self.time_window:
            history.pop(0)

        if len(history) < self.max_messages:
            history.append(current_time)
            return True
        return False

    def get_wait_time(self, user_id: int) -> float:
        current_time = time.time()
        history = self.users_history[user_id]

        if not history or len(history) < self.max_messages:
            return 0

        oldest = history[0]
        wait_time = oldest + self.time_window - current_time
        return max(0, wait_time)