from util.calculate_payment import CalculatePayment


def test_get_invalid_employee_name():
    """ test if in one line of the file there is an incorrect employee name """
    calculate_payment = CalculatePayment(line="test", idx=0)
    assert calculate_payment.get_employee_name() is None


def test_get_invalid_hours_worked():
    """ test if in one line of the file there is an incorrect hours worked detail """
    calculate_payment = CalculatePayment(line="test", idx=0)
    assert calculate_payment.get_hours_worked() is None


def test_hours_worked_format():
    """ test if in one line the hours worked detail the format is incorrect """
    calculate_payment = CalculatePayment(line="ANA=JA08:00-09:00", idx=0)
    hours_worked = calculate_payment.get_hours_worked()
    assert calculate_payment.check_hours_worked_format(hours_worked) == False


def test_daily_hour_pairs_worked_overlap():
    """ test if in one day with two or more hour pairs there is an overlap """
    calculate_payment = CalculatePayment(line="ANA=MO08:00-10:00,MO09:00-12:00", idx=0)
    hours_worked = calculate_payment.get_hours_worked()
    daily_hour_pairs_worked = calculate_payment.get_daily_hour_pairs_worked(
        hours_worked=hours_worked
    )
    assert calculate_payment.check_daily_hour_pairs_worked_overlap(
        daily_hour_pairs_worked=daily_hour_pairs_worked
    ) == {"MO": [[0.0, 0.0]]}


def test_daily_hour_pairs_are_incorrect():
    """ test if in one day a hour pairs are incorrect (end hour is less than start hour) """
    calculate_payment = CalculatePayment(line="ANA=MO16:00-12:00", idx=0)
    hours_worked = calculate_payment.get_hours_worked()

    assert calculate_payment.get_daily_hour_pairs_worked(hours_worked=hours_worked) == {
        "MO": [[0.0, 0.0]]
    }


def test_amount_to_pay():
    """
    the amout to pay must be:

    08:00-09:00 = 01:00 * 25 = 25
    09:00-17:00 = 08:00 * 15 = 120
    19:00-00:00 = 05:00 * 20 = 100

    amount_to_pay = 25 + 120 + 100 = 245
    """
    calculate_payment = CalculatePayment(line="ANA=MO08:00-17:00,MO19:00-00:00", idx=0)
    hours_worked = calculate_payment.get_hours_worked()
    daily_hour_pairs_worked = calculate_payment.get_daily_hour_pairs_worked(
        hours_worked=hours_worked
    )
    assert (
        calculate_payment.get_amount_to_pay(
            daily_hours_pairs_worked=daily_hour_pairs_worked
        )
        == 245.0
    )
