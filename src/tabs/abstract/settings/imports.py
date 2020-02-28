class AbstractImportSettings:

    def __init__(self, importColumnSpecs):
        self.delimiter = ","
        self.hasHeaders = True
        self._columnRefs = {spec.type: i for i, spec in enumerate(importColumnSpecs)}

    def getDisplayColumns(self):
        numbers = [(col, self._column_letter_to_number(colRef)) for col, colRef in self._columnRefs.items()]
        numbers.sort(key=lambda v: v[0].value)
        return numbers

    def getDisplayColumnsAsStrings(self):
        return {typ: self._column_number_to_letter(ref) for typ, ref in self._columnRefs.items()}

    def _column_number_to_letter(self, number):
        if isinstance(number, str):
            return number
        return chr(number + 65)

    def _column_letter_to_number(self, letter):
        if isinstance(letter, int):
            return letter
        return ord(letter.lower()) - 97
