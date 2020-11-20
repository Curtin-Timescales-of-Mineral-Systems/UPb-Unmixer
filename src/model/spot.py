from typing import List, Optional, Dict

from model.cell import InputCell, OutputCell, Cell
from model.column import Column
from model.settings.imports import ImportSettings
from utils import calculations
from model.reconstructedAge import ReconstructedAge


class SpotInputData:

    @staticmethod
    def parse(values_by_column: Dict[Column, float], settings: ImportSettings):
        """
        Parses the raw list of strings representing a row read from the CSV file
        """

        rim_age_value = values_by_column[Column.RIM_AGE_VALUE]
        rim_age_raw_error = values_by_column[Column.RIM_AGE_ERROR]
        rim_age_st_dev = calculations.convert_to_stddev(
            rim_age_value,
            rim_age_raw_error,
            settings.rim_age_error_type,
            settings.rim_age_error_sigmas
        )

        mixed_u_pb_value = values_by_column[Column.MIXED_U_PB_VALUE]
        mixed_u_pb_raw_error = values_by_column[Column.MIXED_U_PB_ERROR]
        mixed_u_pb_st_dev = calculations.convert_to_stddev(
            mixed_u_pb_value,
            mixed_u_pb_raw_error,
            settings.mixed_uPb_error_type,
            settings.mixed_uPb_error_sigmas
        )

        mixed_pb_pb_value = values_by_column[Column.MIXED_PB_PB_VALUE]
        mixed_pb_pb_raw_error = values_by_column[Column.MIXED_PB_PB_ERROR]
        mixed_pb_pb_st_dev = calculations.convert_to_stddev(
            mixed_pb_pb_value,
            mixed_pb_pb_raw_error,
            settings.mixed_pbPb_error_type,
            settings.mixed_pbPb_error_sigmas
        )

        u_concentration_ppm = values_by_column[Column.U_CONCENTRATION]
        th_concentration_ppm = values_by_column[Column.TH_CONCENTRATION]

        return SpotInputData(
            rim_age_value,
            rim_age_st_dev,
            mixed_u_pb_value,
            mixed_u_pb_st_dev,
            mixed_pb_pb_value,
            mixed_pb_pb_st_dev,
            u_concentration_ppm,
            th_concentration_ppm
        )

    def __init__(self,
                 rim_age_value: float,
                 rim_age_st_dev: float,
                 mixed_u_pb_value: float,
                 mixed_u_pb_st_dev: float,
                 mixed_pb_pb_value: float,
                 mixed_pb_pb_st_dev: float,
                 u_concentration_ppm: float,
                 th_concentration_ppm: float):
        self.rim_age_value: float = rim_age_value
        self.rim_age_st_dev: float = rim_age_st_dev
        self.mixed_u_pb_value: float = mixed_u_pb_value
        self.mixed_u_pb_st_dev: float = mixed_u_pb_st_dev
        self.mixed_pb_pb_value: float = mixed_pb_pb_value
        self.mixed_pb_pb_st_dev: float = mixed_pb_pb_st_dev
        self.u_concentration_ppm: float = u_concentration_ppm
        self.th_concentration_ppm: float = th_concentration_ppm


class SpotOutputData:
    def __init__(self,
                 rim_u_pb_value: float,
                 rim_u_pb_st_dev: float,
                 rim_pb_pb_value: float,
                 rim_pb_pb_st_dev: float,
                 reconstructed_age: ReconstructedAge = None,
                 metamict_score: float = None,
                 rim_age_precision_score: float = None,
                 core_to_rim_score: float = None,
                 total_score: float = None,
                 rejected: bool = None):

        self.rim_u_pb_value = rim_u_pb_value
        self.rim_u_pb_st_dev = rim_u_pb_st_dev
        self.rim_pb_pb_value = rim_pb_pb_value
        self.rim_pb_pb_st_dev = rim_pb_pb_st_dev

        self.reconstructed_age: ReconstructedAge = reconstructed_age
        self.valid: bool = reconstructed_age is not None and reconstructed_age.valid

        self.metamict_score: float = metamict_score
        self.rim_age_precision_score: float = rim_age_precision_score
        self.core_to_rim_score: float = core_to_rim_score
        self.total_score: float = total_score
        self.rejected: bool = rejected

    def get_output_cells(self):
        if self.reconstructed_age is None:
            return [OutputCell(None) for _ in range(13)]

        t, t_min, t_max = self.reconstructed_age.get_age_ma()
        u, u_min, u_max = self.reconstructed_age.get_u_pb()
        p, p_min, p_max = self.reconstructed_age.get_pb_pb()

        cells = [
            OutputCell(t),
            OutputCell(t_min),
            OutputCell(t_max),

            OutputCell(u),
            OutputCell(u_min),
            OutputCell(u_max),

            OutputCell(p),
            OutputCell(p_min),
            OutputCell(p_max),

            OutputCell(self.metamict_score),
            OutputCell(self.rim_age_precision_score),
            OutputCell(self.core_to_rim_score),
            OutputCell(self.total_score),
        ]
        return cells

class Spot:
    """
    A class representing the model for a single spot, i.e. a row of data in the csv file/table.
    """

    @staticmethod
    def parse(imported_csv_row: List[str], settings: ImportSettings):
        input_columns_by_indices = settings.get_input_columns_by_indices()

        all_inputs_valid = True
        input_cells = []
        input_values_by_column = {}
        for column, index in input_columns_by_indices.items():
            cell = InputCell(imported_csv_row[index])
            input_values_by_column[column] = cell.value
            input_cells.append(cell)
            all_inputs_valid &= cell.is_valid()

        if all_inputs_valid:
            input_values = SpotInputData.parse(input_values_by_column, settings)
        else:
            input_values = None

        return Spot(input_cells, input_values)

    def __init__(self, input_cells: List[InputCell], inputs: Optional[SpotInputData]):
        self.input_cells: List[InputCell] = input_cells
        self.inputs: Optional[SpotInputData] = inputs

        self.output_cells: List[OutputCell] = []
        self.outputs: Optional[SpotOutputData] = None

    def has_invalid_inputs(self) -> bool:
        return self.inputs is None

    def has_invalid_outputs(self):
        return self.outputs is not None and not self.outputs.valid

    def has_rejected_outputs(self):
        return self.outputs is not None and self.outputs.valid and self.outputs.rejected

    def has_accepted_outputs(self):
        return self.outputs is not None and self.outputs.valid and not self.outputs.rejected

    def has_outputs(self) -> bool:
        return self.outputs is not None

    def clear_output(self) -> None:
        self.outputs = None

    def set_output(self, output_data: SpotOutputData) -> None:
        self.outputs = output_data
        self.output_cells = output_data.get_output_cells()

    def get_display_cells(self) -> List[Cell]:
        return self.input_cells + self.output_cells



