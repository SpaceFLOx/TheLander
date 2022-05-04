import time
from threading import Thread


class Timer(Thread):
  """
  Timer that runs in new thread and calls a callback fn infinitely, with a minimum
  temporal delta of MIN_PERIOD_MS
  """
  MIN_PERIOD_MS = 100
  SLEEP_FACTOR = 0.3

  def __init__(self, callback_fn) -> None:
    Thread.__init__(self)
    self.callback_fn = callback_fn
    self.daemon = True
    self.active = True
    self.start()

  def current_time_millies(self) -> int:
    return time.time_ns() // 1_000_000

  def stop_timer(self):
    self.active = False

  def run(self):
    t_prev = self.current_time_millies()
    t_delta = 0
    while self.active:
      t_current = self.current_time_millies()
      t_delta += t_current - t_prev
      t_prev = t_current
      if t_delta >= Timer.MIN_PERIOD_MS:
        self.callback_fn()
        t_delta = 0
        time.sleep(Timer.SLEEP_FACTOR * (Timer.MIN_PERIOD_MS / 1000.0))
