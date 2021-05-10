import logging
import re
import itertools

from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict


EQUAL = "="
ZERO = 0.00
IS_WORKED_HOUR_PAIR = re.compile(
    "(MO|TU|WE|TH|FR|SA|SU)([01]?[0-9]|2[0-3]):[0-5][0-9]-([01]?[0-9]|2[0-3]):[0-5][0-9]"
)

PAYMENT_TABLE: Dict[int, Any] = {
    1: {
        "hour_pairs": [0, 9.00],
        "payment_by_days": [["MO", "TU", "WE", "TH", "FR"], ["SA", "SU"]],
        "hour_value": [25.00, 30.00],
    },
    2: {
        "hour_pairs": [9.00, 18.00],
        "payment_by_days": [["MO", "TU", "WE", "TH", "FR"], ["SA", "SU"]],
        "hour_value": [15.00, 20.00],
    },
    3: {
        "hour_pairs": [18.00, 24.00],
        "payment_by_days": [["MO", "TU", "WE", "TH", "FR"], ["SA", "SU"]],
        "hour_value": [20.00, 25.00],
    },
}


class CalculatePayment:
    """Class used to calculate the employee payment"""

    employee_name: Optional[str] = ""

    def __init__(self, line: str, idx: int):
        self.line = line
        self.idx = idx

    def get_employee_name(self) -> Optional[str]:
        """Get the employee name, the string before equal if exists"""
        equal_found = self.line.count(EQUAL)

        if equal_found != 1:
            return None

        return self.line[: self.line.find(EQUAL)]

    def get_hours_worked(self) -> Optional[List[str]]:
        """Get the hours worked, the string after equal if exists"""
        equal_found = self.line.count(EQUAL)

        if equal_found != 1:
            return None

        return self.line[self.line.find(EQUAL) + 1 :].split(",")

    def check_hours_worked_format(self, hours_worked: List[str]) -> bool:
        """
        Check the hours worked using a regular expression
        the format each hour pair is: DDHH:MM-HH:MM
        """
        for hour_worked in hours_worked:
            check_match = IS_WORKED_HOUR_PAIR.search(hour_worked)
            if not check_match:
                return False
        return True

    def convert_hour_to_float(self, hour_str: str) -> float:
        """
        Convert hour format HH:MM to a float number
        if hour is equal to 00:00 the float number is 24.00
        """
        hour, minute = hour_str.split(":")
        if int(hour) == 0 and int(minute) == 0:
            return 24.00
        return int(hour) + int(minute) / 60.00

    def get_daily_hour_pairs_worked(
        self, hours_worked: list
    ) -> Dict[str, List[List[float]]]:
        """
        Get the daily hour pairs, in one day is possible to
        have one or more pairs
        """
        daily_hour_pairs_worked = defaultdict(list)
        for hour_worked in hours_worked:
            day = hour_worked[0:2]
            start_hour = self.convert_hour_to_float(hour_worked[2:7])
            end_hour = self.convert_hour_to_float(hour_worked[8:])

            if end_hour < start_hour:
                logging.error(
                    f"end hour {hour_worked[8:]} can not be less than start hour {hour_worked[2:7]} for the employee {self.employee_name} line {self.idx}"
                )
                daily_hour_pairs_worked[day].append([ZERO, ZERO])
            else:
                daily_hour_pairs_worked[day].append([start_hour, end_hour])

        return daily_hour_pairs_worked

    def check_daily_hour_pairs_worked_overlap(
        self,
        daily_hour_pairs_worked: Dict[str, List[List[float]]],
    ) -> Dict[str, List[List[float]]]:
        """
        Check if in one day there is an overlap with the hour
        pairs, eg: 10:00-12:00 and 11:00-13:00, there is an
        overlap, in this case is not possible calculate the
        hours worked in this day
        """
        for day, hour_pairs in daily_hour_pairs_worked.items():
            hour_pairs_sorted = sorted(hour_pairs, key=lambda x: x[0])
            overlap = any(
                hour_pairs_sorted[idx + 1][0] < hour_pairs_sorted[idx][1]
                for idx in range(len(hour_pairs_sorted) - 1)
            )
            if overlap:
                logging.error(
                    f"there are overlapped hours in day {day} for employee {self.employee_name} line {self.idx}"
                )
                daily_hour_pairs_worked[day] = [[ZERO, ZERO]]

        return daily_hour_pairs_worked

    def get_amount_to_pay(
        self, daily_hours_pairs_worked: Dict[str, List[List[float]]]
    ) -> float:
        """
        Get the value to pay, for this the hour pairs by day is reviewed
        with payment table, then is possible obatin the value to pay when
        an employee worked between two or more ranges
        """
        value_to_paid = ZERO

        for (day, hour_pairs), idx1 in itertools.product(
            daily_hours_pairs_worked.items(), PAYMENT_TABLE
        ):
            start_hour2, end_hour2 = PAYMENT_TABLE[idx1]["hour_pairs"]
            for start_hour1, end_hour1 in hour_pairs:
                if end_hour1 >= start_hour2 and end_hour2 >= start_hour1:
                    total_hours = min(end_hour1, end_hour2) - max(
                        start_hour1, start_hour2
                    )

                    value_to_paid += total_hours * self.get_hour_value_day(
                        day=day, idx=idx1
                    )

        return value_to_paid

    def get_hour_value_day(self, day: str, idx: int) -> float:
        """get hour value for a specfic day in a schedule"""
        hour_value = ZERO
        for idx2, days in enumerate(PAYMENT_TABLE[idx]["payment_by_days"]):
            if day in days:
                hour_value = PAYMENT_TABLE[idx]["hour_value"][idx2]
                break
        return hour_value

    def get_employee_payment(self) -> Tuple[Optional[str], Optional[float]]:
        """
        Get the employee payment, before to calculate the value to pay
        the information is validated using the methods defined
        """
        self.employee_name = self.get_employee_name()
        if not self.employee_name:
            logging.error(f"the employee name can't identify, line {self.idx}")
            return None, None

        hours_worked = self.get_hours_worked()

        if not hours_worked:
            logging.error(
                f"there are not hours detail for employee {self.employee_name} line {self.idx}"
            )
            return self.employee_name, ZERO

        if not self.check_hours_worked_format(hours_worked):
            logging.error(
                f"there are an error in format of hour pairs worked for employee {self.employee_name} line {self.idx}"
            )
            return self.employee_name, ZERO

        daily_hour_pairs_worked = self.get_daily_hour_pairs_worked(
            hours_worked=hours_worked
        )

        daily_hour_pairs_worked = self.check_daily_hour_pairs_worked_overlap(
            daily_hour_pairs_worked=daily_hour_pairs_worked,
        )
        amount_to_pay = self.get_amount_to_pay(
            daily_hours_pairs_worked=daily_hour_pairs_worked
        )
        return self.employee_name, amount_to_pay
