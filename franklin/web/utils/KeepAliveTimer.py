"""This class creates a timer that must be kept alive by calling "run".
When "run" is not called before the end of the specified delay,
the function passed when creating the instance is called and the timer ends.

I.E. A perodic event refreshes the timer every 5 seconds, when it fails to do so,
the function is called so we immediately handle the fact that
the event didn't occur in the expected timeframe.

Usage:
    - Create an instance of KeepAliveTimer, passing it a delay (in seconds)
    and a function that will be called when the timer stops.
    - Call the "run" method to start the timer, reset it (even if it stopped previously).
    - You can set a new function with the "fn" property, it will restart the timer
    and the new function will be called when the delay is reached.
"""

import threading

class KeepAliveTimer():
    def __init__(self, delay, fn):
        self.delay = delay
        self.__fn = fn
        self.timer = None

    def run(self):
        """Starts the timer. When the timer is already running, resets it."""
        # Handle a potential running Timer
        if self.timer is not None:
            self.timer.cancel()
        self.__init_timer()
        self.timer.start()
    
    def stop(self):
        """Stops the timer. It can be re-launched by calling "run" again."""
        self.timer.cancel()

    def __init_timer(self):
        self.timer = threading.Timer(self.delay, self.fn)

    @property
    def fn(self):
        return self.__fn
    
    @fn.setter
    def fn(self, new_fn):
        """Sets the function to be called when the timer is over
        and starts/resets the timer if needed.
        :param new_fn: The new function."""
        self.__fn = new_fn
        if self.timer is not None:
            self.timer.cancel()
            self.run()
        self.__init_timer()