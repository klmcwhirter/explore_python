
import logging
from math import floor, log10

import cached_factorial as cf


def reset_decorators(decorator=cf.cached_factorial):
    if hasattr(decorator, 'cache'):
        cf.print_flush(f'before reset: {decorator.cache[:10]=}')
        decorator.cache_reset()

    if hasattr(decorator, 'counter'):
        cf.print_flush(f'before reset: {decorator.counter()=}')
        decorator.counter_reset()

    if hasattr(decorator, 'counter'):
        cf.print_flush(f'{decorator.counter()=}')

    if hasattr(decorator, 'cache'):
        cf.print_flush(f'{len(decorator.cache)=}')
        # cf.print_flush print(f'{decorator.cache=}')

        cf.print_flush(f'{decorator.cache[:10]=}')
        # cf.print_flush print(f'{decorator.cache_initial=}')


if __name__ == '__main__':
    cf.config['CACHE_SIZE'] = 400
    cf.config['PROGRESS_FREQ'] = 100

    N = cf.config['CACHE_SIZE']

    import cached_factorial as cf1
    cf.print_flush(f'{cf1.config=}')

    logging.basicConfig(level=logging.INFO, format='{asctime} - {module} - {funcName} - {levelname} - {message}', style='{')
    logging.info(f'{cf1.config=}')

    # import sys
    # sys.set_int_max_str_digits(500_000)

    reset_decorators(cf.cached_factorial)

    logging.info('begin')

    rc = -1
    first = cf.cached_factorial(N)
    logging.info(f'{floor(log10(first))=}')

    rc = cf.cached_factorial(floor(N/2))
    logging.info(f'{floor(log10(rc))=}')
    # cf.print_flush(first)

    reset_decorators(cf.cached_factorial)
