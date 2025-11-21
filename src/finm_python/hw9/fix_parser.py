"""
FIX Message Parser

This module implements a parser for FIX (Financial Information eXchange) protocol messages.
FIX is a standard messaging protocol used in electronic trading.

The parser converts raw FIX strings into structured Python dictionaries and validates
that required fields are present.

Resources:
- FIX Parser Tool: https://fixparser.targetcompid.com/
- FIX Message Reference: https://ref.onixs.biz/fix-message.html

Common FIX Tags:
- 8: BeginString (FIX version)
- 35: MsgType (D=NewOrderSingle, 8=ExecutionReport, etc.)
- 55: Symbol
- 54: Side (1=Buy, 2=Sell)
- 38: OrderQty
- 40: OrdType (1=Market, 2=Limit)
- 44: Price
- 10: CheckSum
"""

from typing import Dict, List


class FixParser:
    """
    Parser for FIX protocol messages.

    The parser handles FIX messages in pipe-delimited format (e.g., "8=FIX.4.2|35=D|55=AAPL").
    It validates that required fields are present and returns a structured dictionary.

    Attributes:
        delimiter (str): Character used to separate FIX tag-value pairs (default: '|')
        required_tags (List[str]): List of FIX tags that must be present in valid messages
    """

    def __init__(self, delimiter: str = '|', required_tags: List[str] = None):
        """
        Initialize the FIX parser.

        Args:
            delimiter (str): Character separating FIX tag-value pairs (default: '|')
            required_tags (List[str]): Tags that must be present. If None, defaults to
                                       basic required tags like '55' (Symbol), '54' (Side),
                                       and '38' (OrderQty)

        TODO: Initialize the delimiter and required_tags attributes
        TODO: If required_tags is None, set default required tags
        """
        pass

    def parse(self, fix_message: str) -> Dict[str, str]:
        """
        Parse a FIX message string into a dictionary.

        Takes a pipe-delimited FIX message and converts it into a dictionary where
        keys are FIX tag numbers (as strings) and values are the corresponding values.

        Example:
            Input: "8=FIX.4.2|35=D|55=AAPL|54=1|38=100"
            Output: {'8': 'FIX.4.2', '35': 'D', '55': 'AAPL', '54': '1', '38': '100'}

        Args:
            fix_message (str): Raw FIX message in pipe-delimited format

        Returns:
            Dict[str, str]: Dictionary mapping FIX tag numbers to their values

        Raises:
            ValueError: If required tags are missing from the message
            ValueError: If the message format is invalid

        TODO: Implement the following steps:
        1. Split the message by the delimiter
        2. For each tag-value pair, split by '=' to separate tag from value
        3. Build a dictionary with tags as keys and values as values
        4. Validate that all required tags are present
        5. Raise ValueError with a descriptive message if validation fails
        """
        pass

    def validate_required_tags(self, parsed_message: Dict[str, str]) -> None:
        """
        Validate that all required tags are present in the parsed message.

        Args:
            parsed_message (Dict[str, str]): Dictionary of parsed FIX tags

        Raises:
            ValueError: If any required tag is missing

        TODO: Check if each required tag is in the parsed_message dictionary
        TODO: Raise ValueError listing all missing tags if any are not found
        """
        pass

    def get_message_type(self, parsed_message: Dict[str, str]) -> str:
        """
        Extract the message type from a parsed FIX message.

        Message type is stored in FIX tag 35. Common types:
        - 'D': New Order Single
        - '8': Execution Report
        - 'F': Order Cancel Request

        Args:
            parsed_message (Dict[str, str]): Dictionary of parsed FIX tags

        Returns:
            str: The message type value, or None if tag 35 is not present

        TODO: Return the value associated with tag '35', or None if not present
        """
        pass


def main():
    """
    Example usage of the FIX parser.

    TODO: Test the parser with different types of FIX messages:
    1. A valid order message
    2. A message missing required fields
    3. A quote message (if implementing quote support)
    """
    # Example FIX message: New Order Single for AAPL
    msg = "8=FIX.4.2|35=D|55=AAPL|54=1|38=100|40=2|44=150.00|10=128"

    parser = FixParser()

    print("Testing FIX Parser")
    print("-" * 50)
    print(f"Raw message: {msg}")
    print()

    # TODO: Parse the message and print the result
    # TODO: Handle any ValueError exceptions that might be raised
    # TODO: Print the parsed dictionary in a readable format

    # TODO: Test with an invalid message missing required fields
    # Example: "8=FIX.4.2|35=D|10=128"


if __name__ == "__main__":
    main()
