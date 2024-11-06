import logging
import pandas as pd

from . import base

# NOTE: transformers pass all kwargs to superclass to allow it to show the user-defined arguments when calling __repr__.

class split(base.Transformer):
    """Transformer subclass used to split cell values at defined separator and create nodes with
    their respective values as id."""

    def __init__(self, target, properties_of, edge=None, columns=None, **kwargs):
        """
        Initialize the split transformer.

        Args:
            target: The target node type.
            properties_of: Properties of the node.
            edge: The edge type (optional).
            columns: The columns to be processed.
            kwargs: Additional keyword arguments.
        """
        super().__init__(target, properties_of, edge, columns, **kwargs)

    def __call__(self, row, i):
        """
        Process a row and yield split items as node IDs.

        Args:
            row: The current row of the DataFrame.
            i: The index of the current row.

        Yields:
            str: Each split item from the cell value.
        """
        for key in self.columns:
            if self.valid(row[key]):
                assert(type(row[key]) == str)
                items = row[key].split(self.separator)
                for item in items:
                    yield str(item)
            else:
                logging.warning(f"Encountered invalid content when mapping column: `{key}`. Skipping cell value: `{row[key]}`")


class cat(base.Transformer):
    """Transformer subclass used to concatenate cell values of defined columns and create nodes with
    their respective values as id."""

    def __init__(self, target, properties_of, edge=None, columns=None, **kwargs):
        """
        Initialize the cat transformer.

        Args:
            target: The target node type.
            properties_of: Properties of the node.
            edge: The edge type (optional).
            columns: The columns to be processed.
            kwargs: Additional keyword arguments.
        """
        super().__init__(target, properties_of, edge, columns, **kwargs)

    def __call__(self, row, i):
        """
        Process a row and yield concatenated items as node IDs.

        Args:
            row: The current row of the DataFrame.
            i: The index of the current row.

        Yields:
            str: The concatenated string from the cell values.
        """
        formatted_items = ""

        for key in self.columns:
            if self.valid(row[key]):
                formatted_items += str(row[key])
            else:
                logging.warning(f"Encountered invalid content when mapping column: `{key}`. Skipping cell value: `{row[key]}`")

        yield str(formatted_items)


class cat_format(base.Transformer):
    """Transformer subclass used to concatenate cell values of defined columns and create nodes with
    their respective values as id."""

    def __init__(self, target, properties_of, edge=None, columns=None, **kwargs):
        """
        Initialize the cat_format transformer.

        Args:
            target: The target node type.
            properties_of: Properties of the node.
            edge: The edge type (optional).
            columns: The columns to be processed.
            kwargs: Additional keyword arguments.
        """
        super().__init__(target, properties_of, edge, columns, **kwargs)

    def __call__(self, row, i):
        """
        Process a row and yield a formatted string as node ID.

        Args:
            row: The current row of the DataFrame.
            i: The index of the current row.

        Yields:
            str: The formatted string from the cell values.

        Raises:
            Exception: If the format string is not defined or if invalid content is encountered.
        """
        if hasattr(self, "format_string"):
            for column_name in self.columns:
                column_value = row.get(column_name, '')
                if self.valid(column_value):
                    continue
                else:
                    raise Exception(
                        f"Encountered invalid content when mapping column: `{column_name}` in `format_cat` transformer. "
                        f"Try using another transformer type.")

            formatted_string = self.format_string.format_map(row)
            yield str(formatted_string)

        else:
            raise Exception(f"Format string not defined for `cat_format` transformer. Define a format string or use the `cat` transformer.")


class rowIndex(base.Transformer):
    """Transformer subclass used for the simple mapping of nodes with row index values as id."""

    def __init__(self, target, properties_of, edge=None, columns=None, **kwargs):
        """
        Initialize the rowIndex transformer.

        Args:
            target: The target node type.
            properties_of: Properties of the node.
            edge: The edge type (optional).
            columns: The columns to be processed.
            kwargs: Additional keyword arguments.
        """
        super().__init__(target, properties_of, edge, columns, **kwargs)

    def __call__(self, row, i):
        """
        Process a row and yield the row index as node ID.

        Args:
            row: The current row of the DataFrame.
            i: The index of the current row.

        Returns:
            int: The row index if valid.

        Raises:
            Warning: If the row index is invalid.
        """
        if self.valid(i):
            yield str(i)
        else:
            logging.warning(f"Error while mapping by row index. Invalid cell content: `{i}`")


class map(base.Transformer):
    """Transformer subclass used for the simple mapping of cell values of defined columns and creating
    nodes with their respective values as id."""

    def __init__(self, target, properties_of, edge=None, columns=None, **kwargs):
        """
        Initialize the map transformer.

        Args:
            target: The target node type.
            properties_of: Properties of the node.
            edge: The edge type (optional).
            columns: The columns to be processed.
            kwargs: Additional keyword arguments.
        """
        super().__init__(target, properties_of, edge, columns, **kwargs)

    def __call__(self, row, i):
        """
        Process a row and yield cell values as node IDs.

        Args:
            row: The current row of the DataFrame.
            i: The index of the current row.

        Yields:
            str: The cell value if valid.

        Raises:
            Warning: If the cell value is invalid.
        """
        if not self.columns:
            raise ValueError(f"No column declared for the {type(self).__name__} transformer, did you forgot to add a `columns` keyword?")

        for key in self.columns:
            if key not in row:
                msg = f"Column '{key}' not found in data"
                logging.error(msg)
                raise KeyError(msg)
            if self.valid(row[key]):
                yield str(row[key])
            else:
                logging.warning(
                     f"Encountered invalid content at row {i} when mapping column: `{key}`. Skipping cell value: `{row[key]}`")


class translate(base.Transformer):
    """Translate the targeted cell value using a tabular mapping and yield a node with using the translated ID."""

    # def __init__(self, target, properties_of, edge=None, columns=None, translations=None, translate_from=None, translate_to=None, **kwargs):
    # def __init__(self, target, properties_of, edge=None, columns=None, translations=None, translations_file=None, translate_from=None, translate_to=None, **kwargs):
    def __init__(self, target, properties_of, edge=None, columns=None, **kwargs):
        """
        Constructor.

        Args:
            target: The target node type.
            properties_of: Properties of the node.
            edge: The edge type (optional).
            columns: The columns to be processed.
            kwargs: Additional keyword arguments.
        """
        super().__init__(target, properties_of, edge, columns, **kwargs)
        self.map = map(target, properties_of, edge, columns)

        translations = kwargs.get("translations", None)
        translations_file = kwargs.get("translations_file", None)
        translate_from = kwargs.get("translate_from", None)
        translate_to = kwargs.get("translate_to", None)

        if translations and translations_file:
            raise RuntimeError(f"Cannot have both `translations` (=`{translations}`) and `translations_file` (=`{translations_file}`) defined in a {type(self).__name__} transformer.")

        if translations:
            self.translate = translations
            logging.debug(f"\t\t\tManual translations: `{self.translate}`")
        elif translations_file:
            logging.debug(f"\t\t\tGet translations from file: `{translations_file}`")
            if not translate_from:
                raise ValueError(f"No translation source column declared for the `{type(self).__name__}` transformer using translations_file=`{translations_file}`, did you forget to add a `translate_from` keyword?")
            if not translate_to:
                raise ValueError(f"No translation target column declared for the `{type(self).__name__}` transformer using translations_file=`{translations_file}`, did you forget to add a `translate_to` keyword?")
            else:
                self.translations_file = translations_file
                self.translate_from = translate_from
                self.translate_to = translate_to

                pd_read_csv_args =[ "sep", "delimiter", "header", "names", "index_col", "usecols", "dtype", "engine", "converters", "true_values", "false_values", "skipinitialspace", "skiprows", "skipfooter", "nrows", "na_values", "keep_default_na", "na_filter", "verbose", "skip_blank_lines", "parse_dates", "infer_datetime_format", "keep_date_col", "date_parser", "date_format", "dayfirst", "cache_dates", "iterator", "chunksize", "compression", "thousands", "decimal", "lineterminator", "quotechar", "quoting", "doublequote", "escapechar", "comment", "encoding", "encoding_errors", "dialect", "on_bad_lines", "delim_whitespace", "low_memory", "memory_map", "float_precision", "storage_options", "dtype_backend" ]
                pd_args = {k:v for k,v in kwargs.items() if k in pd_read_csv_args}

                if "sep" in pd_args and pd_args["sep"] == "TAB":
                    logging.debug(f"\t\t\tMapping asked for sep:TAB, enable Pandas' read_csv engine:python to avoid a warning.")
                    pd_args["sep"] = '\t'
                    pd_args["engine"] = "python"

                logging.debug(f"\t\t\tArguments passed to pandas.read_csv: `{pd_args}`")

                self.df = pd.read_csv(self.translations_file, **pd_args)

                if self.translate_from not in self.df.columns:
                    raise ValueError(f"Source column `{self.translate_from}` not found in {type(self).__name__} transformer’s translations file `{self.translations_file}`, available headers: `{','.join(self.df.columns)}`.")

                if self.translate_to not in self.df.columns:
                    raise ValueError(f"Target column `{self.translate_to}` not found in {type(self).__name__} transformer’s translations file `{self.translations_file}`, available headers: `{','.join(self.df.columns)}`.")

                self.translate = {}
                for i,row in self.df.iterrows():
                    if row[self.translate_from] and row[self.translate_to]:
                        self.translate[row[self.translate_from]] = row[self.translate_to]
                    else:
                        logging.warning(f"Cannot translate from `{self.translate_from}` to `{self.translate_to}`, invalid translations values at row {i} of file `{self.translations_file}`: `{row[self.translate_from]}` => `{row[self.translate_to]}`. I will ignore this translation.")

        else:
            raise RuntimeError(f"When using a {type(self).__name__} transformer, you must define either `translations` or `translations_file`.")


        if not self.translate:
            raise ValueError(f"No translation found, did you forget the `translations` keyword?")

    def __call__(self, row, i):
        """
        Process a row and yield cell values as node IDs.

        Args:
            row: The current row of the DataFrame.
            i: The index of the current row.

        Yields:
            str: The cell value if valid.

        Raises:
            Warning: If the cell value is invalid.
        """
        if not self.columns:
            raise ValueError(f"No column declared for the {type(self).__name__} transformer, did you forgot to add a `columns` keyword?")

        for key in self.columns:
            if key not in row:
                msg = f"Column '{key}' not found in data"
                logging.error(msg)
                raise KeyError(msg)
            cell = row[key]
            if cell in self.translate:
                row[key] = self.translate[cell]
            else:
                logging.warning(f"Row {i} does not contain something to be translated from `{self.translate_from}` to `{self.translate_to}` at column `{key}`.")

        for e in self.map(row, i):
            yield e

