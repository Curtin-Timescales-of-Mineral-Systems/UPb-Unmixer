
class ReconstructedAge():
    def __init__(self, values, minValues, maxValues):
        self.values = list(values)
        self.minValues = list(minValues)
        self.maxValues = list(maxValues)

        t1 = self.minValues[1]
        t2 = self.maxValues[1]

        self.minValues[1] = min(t1, t2)
        self.maxValues[1] = max(t1, t2)

    def hasValue(self):
        return self.values is not None

    def hasMinValue(self):
        return self.minValues is not None and self.maxValues is not None

    def hasMaxValue(self):
        return self.minValues is not None and self.maxValues is not None