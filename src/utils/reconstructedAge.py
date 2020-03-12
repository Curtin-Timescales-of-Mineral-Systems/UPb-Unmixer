
class ReconstructedAge():
    def __init__(self, values, minValues, maxValues):
        self.values = list(values)

        if minValues and maxValues:
            self.minValues = list(minValues)
            self.maxValues = list(maxValues)

            # Swap uPb values as they may be inverted
            t1 = self.minValues[1]
            t2 = self.maxValues[1]
            self.minValues[1] = min(t1, t2)
            self.maxValues[1] = max(t1, t2)
        else:
            self.minValues = minValues
            self.maxValues = maxValues

    def hasValue(self):
        return self.values is not None

    def hasMinValue(self):
        return self.minValues is not None and self.maxValues is not None

    def hasMaxValue(self):
        return self.minValues is not None and self.maxValues is not None

    def getAge(self):
        return self._getValuesAndError(0)

    def getUPb(self):
        return self._getValuesAndError(1)

    def getPbPb(self):
        return self._getValuesAndError(2)

    def _getValuesAndError(self, i):
        scale = (10 ** -6) if i == 0 else 1

        value = self.values[i]*scale
        minValue = value - scale*self.minValues[i] if self.hasMinValue() else None
        maxValue = scale*self.maxValues[i] - value if self.hasMaxValue() else None
        return value, minValue, maxValue