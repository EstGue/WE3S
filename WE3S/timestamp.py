import math
from colorama import Fore
from colorama import Style

class Timestamp:
    # Precision is 1 microsecond
    
    def __init__(self, timestamp = None):
        if timestamp is None:
            self.s = 0
            self.ms = 0
            self.us = 0
        elif isinstance(timestamp, int):
            self.s = timestamp
            self.ms = 0
            self.us = 0
        elif isinstance(timestamp, float):
            timestamp = round(timestamp * 10**6)
            self.s = timestamp // 10**6
            timestamp = timestamp - self.s * 10**6
            self.ms = timestamp // 10**3
            timestamp = timestamp - self.ms * 10**3
            self.us = timestamp
        else:
            self.s = timestamp.s
            self.ms = timestamp.ms
            self.us = timestamp.us
        self.verify_inner_state()

    def __add__(self, other):
        other_t = Timestamp(other)
        res = Timestamp()
        res.us = self.us + other_t.us
        res.ms = res.us // 1000
        res.us = res.us % 1000
        res.ms += self.ms + other_t.ms
        res.s = res.ms // 1000
        res.ms = res.ms % 1000
        res.s += self.s + other_t.s
        res.verify_inner_state()
        return res

    # __radd__ = __add__

    def __sub__(self, other):
        assert(self >= other)
        other_t = Timestamp(other)
        res = Timestamp()
        res.s = self.s - other_t.s
        res.ms = self.ms - other_t.ms
        res.us = self.us - other_t.us
        if res.us < 0:
            res.ms -= 1
            res.us = 1000 + res.us
        if res.ms < 0:
            res.s -= 1
            res.ms = 1000 + res.ms
        res.verify_inner_state()
        return res

    def __mul__(self, other):
        if isinstance(other, int):
            res = Timestamp()
            res.us = self.us * other
            carry = res.us // 1000
            res.us = res.us % 1000
            res.ms = self.ms * other
            res.ms += carry
            carry = res.ms // 1000
            res.ms = res.ms % 1000
            res.s = self.s * other
            res.s += carry
            res.verify_inner_state()
            return res
        else:
            print("Unsupported operation: cannot multiply a timestamp with something other than an int")
            assert(0)

    __rmul__ = __mul__

    def __eq__(self, other):
        other_t = Timestamp(other)
        return self.s == other_t.s and self.ms == other_t.ms and self.us == other_t.us

    # Greater than
    def __gt__(self, other):
        other_t = Timestamp(other)
        if self.s > other_t.s:
            return True
        elif self.s == other_t.s:
            if self.ms > other_t.ms:
                return True
            elif self.ms == other_t.ms:
                if self.us > other_t.us:
                    return True
        return False

    # Greater or equal
    def __ge__(self, other):
        other_t = Timestamp(other)
        if self.s > other_t.s:
            return True
        elif self.s == other_t.s:
            if self.ms > other_t.ms:
                return True
            elif self.ms == other_t.ms:
                if self.us >= other_t.us:
                    return True
        return False

    # less than
    def __lt__(self, other):
        other_t = Timestamp(other)
        if self.s < other_t.s:
            return True
        elif self.s == other_t.s:
            if self.ms < other_t.ms:
                return True
            elif self.ms == other_t.ms:
                if self.us < other_t.us:
                    return True
        return False

    # Less or equal
    def __le__(self, other):
        other_t = Timestamp(other)
        if self.s < other_t.s:
            return True
        elif self.s == other_t.s:
            if self.ms < other_t.ms:
                return True
            elif self.ms == other_t.ms:
                if self.us <= other_t.us:
                    return True
        return False

    def __float__(self):
        res = self.s
        res += self.ms * 10**-3
        res += self.us * 10**-6
        return res
    
    def __str__(self):
        return str("{:.6f}".format(float(self)))

    def verify_inner_state(self):
        assert(isinstance(self.s, int))
        assert(isinstance(self.ms, int))
        assert(isinstance(self.us, int))
        result = True
        # if not self.s >= 0:
        #     print(f"{Fore.RED}ERROR: the timestamp must be positive")
        #     print(self)
        #     result = False
        #     print(f"{Style.RESET_ALL}")
        if not self.ms >= 0 or not self.ms < 1000:
            print(f"{Fore.RED}ERROR: timestamp ms must be comprised between 0 and 1000")
            print("ms=", self.ms)
            result = False
            print(f"{Style.RESET_ALL}")
        if not self.us >= 0 or not self.us < 1000:
            print(f"{Fore.RED}ERROR: timestamp us must be comprised between 0 and 1000")
            print("us=", self.us)
            result = False
            print(f"{Style.RESET_ALL}")

        assert(result)
