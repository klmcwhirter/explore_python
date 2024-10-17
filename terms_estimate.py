
import datetime
from pprint import pprint

THOUSAND = 1_000
MILLION = THOUSAND * THOUSAND
MAX_TERMS = 50 * THOUSAND  # MILLION


def timedelta_per_1000_terms(term_1000s: list[int]) -> list[datetime.timedelta]:
    td = 1
    tds = []
    for _ in term_1000s:
        tds.append(td)
        td += 4
    return tds


a = range(THOUSAND, MAX_TERMS + THOUSAND, THOUSAND)
tds = timedelta_per_1000_terms(a)

print(f'{len(tds)=:_}')
# pprint(tds)

time_sum = sum(tds)
print(f'{time_sum=:_}')

time_delta = datetime.timedelta(seconds=time_sum)
print(f'{str(time_delta)=}')
