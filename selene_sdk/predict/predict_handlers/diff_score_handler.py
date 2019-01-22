"""
Handles computing and outputting the difference scores
"""
from .handler import _create_warning_handler
from .handler import PredictionsHandler


class DiffScoreHandler(PredictionsHandler):
    """
    The "diff score" is the difference between `alt` and `ref`
    predictions.

    Parameters
    ----------
    features : list(str)
        List of sequence-level features, in the same order that the
        model will return its predictions.
    nonfeature_columns : list(str)
        Columns in the file that help to identify the input sequence to
        which the features data corresponds.
    output_path_prefix : str
        Path to the file to which Selene will write the diff scores.
        The path may contain a filename prefix. Selene will append
        `diffs` to the end of the prefix.
    output_format : {'tsv', 'hdf5'}
        Specify the desired output format. TSV can be specified if you
        would like the final file to be easily perused. However, saving
        to a TSV file is much slower than saving to an HDF5 file.

    Attributes
    ----------
    needs_base_pred : bool
        Whether the handler needs the base (reference) prediction as input
        to compute the final output

    """

    def __init__(self,
                 features,
                 nonfeature_columns,
                 output_path_prefix,
                 output_format):
        """
        Constructs a new `DiffScoreHandler` object.
        """
        super(DiffScoreHandler, self).__init__(
            features, nonfeature_columns, output_path_prefix, output_format)

        self.needs_base_pred = True
        self._results = []
        self._samples = []
        self._NA_samples = []

        self._features = features
        self._nonfeature_columns = nonfeature_columns
        self._output_path_prefix = output_path_prefix
        self._output_format = output_format

        self._create_write_handler("diffs")

        self._warn_handle = None

    def handle_NA(self, batch_ids):
        """
        TODO

        Parameters
        ----------
        batch_ids : # TODO
            # TODO

        """
        super().handle_NA(batch_ids)

    def handle_warning(self,
                       batch_predictions,
                       batch_ids,
                       baseline_predictions):
        if self._warn_handle is None:
            self._warn_handle = _create_warning_handler(
                self._features,
                self._nonfeature_columns,
                self._output_path_prefix,
                self._output_format,
                DiffScoreHandler)
        self._warn_handle.handle_batch_predictions(
            batch_predictions, batch_ids, baseline_predictions)

    def handle_batch_predictions(self,
                                 batch_predictions,
                                 batch_ids,
                                 baseline_predictions):
        """
        # TODO

        Parameters
        ----------
        batch_predictions : arraylike
            The predictions for a batch of sequences. This should have
            dimensions of :math:`B \\times N` (where :math:`B` is the
            size of the mini-batch and :math:`N` is the number of
            features).
        batch_ids : list(arraylike)
            Batch of sequence identifiers. Each element is `arraylike`
            because it may contain more than one column (written to
            file) that together make up a unique identifier for a
            sequence.
        base_predictions : arraylike
            The baseline prediction(s) used to compute the diff scores.
            Must either be a vector of dimension :math:`N` values or a
            matrix of dimensions :math:`B \\times N` (where :math:`B` is
            the size of the mini-batch, and :math:`N` is the number of
            features).

        """
        diffs = baseline_predictions - batch_predictions
        self._results.append(diffs)
        self._samples.append(batch_ids)
        if len(self._results) > 100000:
            self.write_to_file()

    def write_to_file(self, close=False):
        """
        TODO

        """
        super().write_to_file(close=close)
