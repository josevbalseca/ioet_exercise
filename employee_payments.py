import sys
import logging
import re

from argparse import ArgumentParser
from typing import Dict, List
from util.calculate_payment import CalculatePayment


def get_argument_parser() -> ArgumentParser:
    """Params definition"""
    parser = ArgumentParser()

    parser.add_argument(
        "--input_file_name", help="input file name with employees worked hours"
    )

    return parser


def get_amount_to_pay_by_employee(input_file_name: str) -> Dict:
    """Get the salary by employee for each line in the file"""
    amount_to_pay_by_employee: Dict = {}
    try:
        with open(input_file_name, "r") as reader:

            # Read each line and process it to avoid use a lot of resources
            for idx, line in enumerate(reader, start=1):
                # Calculate the amount_to_pay for each employee
                # according to the hours worked
                calculate_payment = CalculatePayment(line=line, idx=idx)
                employee, amount_to_pay = calculate_payment.get_employee_payment()
                if employee:
                    amount_to_pay_by_employee[employee] = amount_to_pay
    except IOError:
        logging.error("there is an error to read input file, check name and path")
    except Exception:
        logging.error("there is an error while processing employee hours worked file")

    return amount_to_pay_by_employee


def main(args=None):
    """Process input file to obtain the amount to pay by employee"""
    parser = get_argument_parser()
    args = parser.parse_args()

    if args.input_file_name:
        """Execute the processing when input file is given"""
        # Calculate the amount_to_pay for each employee
        # according to the hours worked
        amount_to_pay_by_employee = get_amount_to_pay_by_employee(
            input_file_name=args.input_file_name
        )
        # Print the result
        if amount_to_pay_by_employee:
            for employee, amount_to_pay in amount_to_pay_by_employee.items():
                print(f"The amount to pay {employee} is: {amount_to_pay:.2f} USD")
        else:
            print("Nothing to print.")
            return 2

        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
