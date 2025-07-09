from typing import Any, Dict
from .base import BaseTool
from .._constants import CALCULATOR


class CalculatorTool(BaseTool):

    @property
    def name(self) -> str:
        return CALCULATOR

    @property
    def description(self) -> str:
        return "Provides results of basic math calculations"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "num1": {
                    "type": "number",
                    "description": "First operand"
                },
                "num2": {
                    "type": "number",
                    "description": "Second operand"
                },
                "operation": {
                    "type": "string",
                    "description": "Operation to perform",
                    "enum": ["add", "subtract", "multiply", "divide"]
                }
            },
            "required": ["num1", "num2", "operation"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """Execute calculator operation with proper argument extraction"""
        try:
            num1 = float(arguments["num1"])
            num2 = float(arguments["num2"])
            operation = arguments["operation"]

            if operation == "add":
                result = num1 + num2
            elif operation == "subtract":
                result = num1 - num2
            elif operation == "multiply":
                result = num1 * num2
            elif operation == "divide":
                if num2 == 0:
                    return "Error: Division by zero"
                result = num1 / num2
            else:
                return f"Error: Unknown operation '{operation}'"

            return f"Result: {result}"
        except KeyError as e:
            return f"Error: Missing required argument: {str(e)}"
        except ValueError as e:
            return f"Error: Invalid argument value: {str(e)}"
        except Exception as e:
            return f"Error processing calculation: {str(e)}"
