from typing import Optional, Dict, Any

from qrogue.util import MyRandom


class WaveFunction:
    def __init__(self, weights: Dict[Optional[Any], float], default_value: Any = None):
        self.__weights = weights
        self.__default_value = default_value
        self.__state: Optional[Any] = None

    @property
    def is_collapsed(self) -> bool:
        return self.__state is not None

    @property
    def state(self) -> Any:
        assert self.is_collapsed, "WaveFunction not yet collapsed!"
        return self.__state

    def adapt_weights(self, type_weights: Dict[Optional[Any], int]):
        """
        type_weights is only read, never written
        """
        if self.is_collapsed:
            return  # no need to adapt anything

        weight_sum = sum(type_weights.values())

        for key in self.__weights:
            if key in type_weights:
                norm_weight = type_weights[key] / weight_sum
                # for now the normalization will not be perfectly accurate
                # todo fix/come up with solution (floats?)
                # e.g. increase weight by 20% = multiply by 1.2
                self.__weights[key] = int(self.__weights[key] * (1 + norm_weight))
            else:
                self.__weights[key] = 0  # non-existing key is like a 0 weight

    def collapse(self, rand: MyRandom) -> Any:
        if len(self.__weights) == 0:
            self.__state = self.__default_value  # collapse to default_value if nothing else is possible
        if self.is_collapsed:
            return self.__state

        weight_sum = sum(self.__weights.values())
        rand_val = rand.get_int(0, weight_sum, "WaveFunction.collapse()")
        val = 0
        for key in self.__weights:
            weight = self.__weights[key]
            val += weight
            if rand_val < val:
                self.__state = key
                return self.__state
        return None  # this should not be possible to happen

    def force_value(self, value: Any) -> bool:
        assert not self.is_collapsed, f"Forcing an already collapsed WaveFunction to {value}!"
        if type(value) in [type(key) for key in self.__weights.keys()]:
            self.__state = value
            return True
        return False

    def copy(self):
        wf = WaveFunction(self.__weights.copy(), self.__default_value)
        if self.is_collapsed:
            wf.force_value(self.__state)
        return wf

    def __str__(self):
        if self.is_collapsed:
            return f"WF ({self.__state})"
        else:
            text = f"WF (?"
            weight_sum = sum(self.__weights.values())
            for key in self.__weights:
                text += f"{str(key)} {(100 * self.__weights[key] / weight_sum):.0f}% | "
            text = text[:-2] + ")"
            return text
