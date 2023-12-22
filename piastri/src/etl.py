import fastf1 as ff1
import os


def get_years(start, end):
    """
    Get the list of years for which data exists.

    Parameters:
    start (int): The first year for which to retrieve data.
    end (int): The last year for which to retrieve data.

    Returns:
    list: A list of years.
    """

    years = list(range(start, end + 1))

    return years


def get_rounds(year):
    """
    Get the list of round numbers for a given year.

    Parameters:
    year (int): The year for which to retrieve round numbers.

    Returns:
    list: A list of round numbers.
    """

    schedule = ff1.get_event_schedule(1994)
    rounds = schedule.RoundNumber.to_list()

    return rounds


def main():
    year_start = os.environ["year_start"]
    year_end = os.environ["year_end"]

    list_years = get_years(year_start, year_end)

    for year in list_years:
        list_rounds = get_rounds(year)


if __name__ == "__main__":
    main()
