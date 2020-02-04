import model.errors as errors
import model.calculations as calculations

import utils

class Row():
    def __init__(self, inputValues, settings):
        self.inputValues = inputValues
        self.outputValues = [""]*9
        self.determineValidity(settings)
        self.processed = False
        self.validOutput = False

    def determineValidity(self, settings):
        self.validInput = True
        self.cellValid = []
        for i in settings.getPrimaryDataColumns():
            try:
                float(self.inputValues[i])
                self.cellValid.append(True)
            except:
                self.cellValid.append(False)
                self.validInput = False

    def getDisplayValues(self, settings):
        displayValues = [self.inputValues[i] for i in settings.getPrimaryDataColumns()]
        displayValues += self.outputValues
        return displayValues

    def process(self, settings):
        self.processed = True
        if not self.validInput or not self.processed:
            self.outputValues = [""]*9
            self.cellValid.extend([False]*9)
            return

        vs = self.inputValues

        self.rimAgeValue = float(vs[settings.getRimAgeColumn()])
        self.rimAgeRawError = float(vs[settings.getRimAgeErrorColumn()])
        self.rimAgeStDev = utils.convert_to_stddev(self.rimAgeValue, self.rimAgeRawError, settings.rimAgeErrorType, settings.rimAgeErrorSigmas)
        rimAge = errors.ufloat(self.rimAgeValue, self.rimAgeStDev)*10**6
    
        self.mixedUPbValue = float(vs[settings.getMixedPointUPbColumn()])
        self.mixedUPbRawError = float(vs[settings.getMixedPointUPbErrorColumn()])
        self.mixedUPbStDev = utils.convert_to_stddev(self.mixedUPbValue, self.mixedUPbRawError, settings.mixedPointErrorType, settings.mixedPointErrorSigmas)
        mixedUPb = errors.ufloat(self.mixedUPbValue, self.mixedUPbStDev)

        self.mixedPbPbValue = float(vs[settings.getMixedPointPbPbColumn()])
        self.mixedPbPbRawError = float(vs[settings.getMixedPointPbPbErrorColumn()])
        self.mixedPbPbStDev = utils.convert_to_stddev(self.mixedPbPbValue, self.mixedPbPbRawError, settings.mixedPointErrorType, settings.mixedPointErrorSigmas)
        mixedPbPb = errors.ufloat(self.mixedPbPbValue, self.mixedPbPbStDev)

        rimUPb = calculations.u238pb206_from_age(rimAge)
        rimPbPb = calculations.pb207pb206_from_age(rimAge)

        self.rimUPbValue = errors.value(rimUPb)
        self.rimUPbStDev = errors.stddev(rimUPb)
        self.rimUPbError = utils.convert_from_stddev_with_sigmas(self.rimUPbValue, self.rimUPbStDev, settings.outputErrorType, settings.outputErrorSigmas)
        self.rimPbPbValue = errors.value(rimPbPb)
        self.rimPbPbStDev = errors.stddev(rimPbPb)
        self.rimPbPbError = utils.convert_from_stddev_with_sigmas(self.rimPbPbValue, self.rimPbPbStDev, settings.outputErrorType, settings.outputErrorSigmas)

        self.reconstructedValues, self.minReconstructedValues, self.maxReconstructedValues = calculations.reconstruct_age(rimUPb, rimPbPb, mixedUPb, mixedPbPb, settings.outputErrorSigmas)

        self.outputValues = [""] * 9
        self.validOutput = True
        if self.reconstructedValues is None:
            self.validOutput = False
            return

        self.reconstructedAge = self.reconstructedValues[0]/(10**6)
        self.reconstructedUPb = self.reconstructedValues[1]
        self.reconstructedPbPb = self.reconstructedValues[2]
        self.outputValues[0] = self.reconstructedAge
        self.outputValues[3] = self.reconstructedUPb
        self.outputValues[6] = self.reconstructedPbPb

        if self.minReconstructedValues is None:
            self.validOutput = False
        else:
            self.minReconstructedAge = self.minReconstructedValues[0]/(10**6) 
            self.maxReconstructedUPb = self.minReconstructedValues[1]
            self.minReconstructedPbPb = self.minReconstructedValues[2]
            self.outputValues[1] = settings.getOutputError(self.reconstructedAge, self.reconstructedAge - self.minReconstructedAge)
            self.outputValues[5] = settings.getOutputError(self.reconstructedUPb, self.maxReconstructedUPb - self.reconstructedUPb)
            self.outputValues[7] = settings.getOutputError(self.reconstructedPbPb, self.reconstructedPbPb - self.minReconstructedPbPb)

        if self.maxReconstructedValues is None:
            self.validOutput = False
        else:
            self.maxReconstructedAge = self.maxReconstructedValues[0]/(10**6)
            self.minReconstructedUPb = self.maxReconstructedValues[1]
            self.maxReconstructedPbPb = self.maxReconstructedValues[2]
            self.outputValues[2] = settings.getOutputError(self.reconstructedAge, self.maxReconstructedAge - self.reconstructedAge)
            self.outputValues[4] = settings.getOutputError(self.reconstructedUPb, self.reconstructedUPb - self.minReconstructedUPb)
            self.outputValues[8] = settings.getOutputError(self.reconstructedPbPb, self.maxReconstructedPbPb - self.reconstructedPbPb)


    def extractValues():
        if not self.valid:
            return