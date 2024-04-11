
import inspect
import types


def test_funcs_can_call_inner() -> None:
    def inner_func() -> bool:
        return True

    assert inner_func()


def func_to_shadow() -> int:
    return 43


def test_funcs_inner_shadows_outer() -> None:
    def func_to_shadow() -> int:
        return 42

    assert 42 == func_to_shadow()


def test_funcs_dir_does_not_include_inner() -> None:
    # print(f'{type(test_funcs_inner_shadows_outer)=}')

    d = dir(test_funcs_inner_shadows_outer)
    # print(d)

    assert 'func_to_shadow' not in d


def test_funcs_inspect_source_of_outer_func_to_shadow() -> None:
    '''inspect source of an outer function that will replace the outer function'''
    source, line_no = inspect.getsourcelines(func_to_shadow)
    print(f'\n{line_no=}')
    for line in source:
        print(line, end='')
    assert any('def func_to_shadow' in line for line in source)
    assert any('return 43' in line for line in source)

    # not inner impl
    assert all('return 42' not in line for line in source)


def test_funcs_inspect_source_of_outer_contains_inner() -> None:
    '''inspect source of an inner function referencing the outer function'''
    source, line_no = inspect.getsourcelines(test_funcs_inner_shadows_outer)
    print(f'\n{line_no=}')
    for line in source:
        print(line, end='')
    assert any('def func_to_shadow' in line for line in source)
    assert any('return 42' in line for line in source)

    # not outer impl
    assert all('return 43' not in line for line in source)


def test_funcs_code_contains_inner() -> None:
    print()
    # print(f'{type(test_funcs_inner_shadows_outer.__code__)=}')
    test_funcs_inner_shadows_outer_code: types.CodeType = test_funcs_inner_shadows_outer.__code__
    print(f'{test_funcs_inner_shadows_outer_code.co_consts[2]}=')

    assert 'func_to_shadow' in str(test_funcs_inner_shadows_outer_code.co_consts[2])


def test_funcs_inspect_source_from_outer_code_consts_is_inner() -> None:
    '''inspect source of an inner function referencing the outer function _code__.co_consts - note assumes function structure'''
    source, line_no = inspect.getsourcelines(test_funcs_inner_shadows_outer.__code__.co_consts[2])
    print(f'\n{line_no=}')
    for line in source:
        print(line, end='')
    assert any('def func_to_shadow' in line for line in source)
    assert any('return 42' in line for line in source)

    # not outer impl
    assert all('return 43' not in line for line in source)


# region test_funcs_can_patch_inner_func_by_replacing_co_const

def monkey_patch_fn(original_fn: types.FunctionType, name: str, new_fn: types.FunctionType):
    ''' Returns a copy of original_fn with its internal function called name replaced with new_fn

        from https://stackoverflow.com/a/11912076 - note that is for Python 2.5.1 - adapted here for 3.12
    '''

    def fix_consts(x):
        '''Little helper function for use with map to pick out the correct constant'''
        if x == None:
            return None
        if hasattr(x, 'co_name') and x.co_name == name:
            return new_fn.__code__
        if x == 42:
            return 43  # align with outer func_to_shadow impl
        return x

    original_code = original_fn.__code__
    new_consts = tuple(map(fix_consts, original_code.co_consts))

    code_type_args = [
        # see help(types.CodeType)
        "co_argcount",
        'co_posonlyargcount',  # 3.12
        'co_kwonlyargcount',  # 3.12
        "co_nlocals",
        "co_stacksize",
        "co_flags",
        "co_code",
        "co_consts",
        "co_names",
        "co_varnames",
        "co_filename",
        "co_name",
        'co_qualname',  # 3.12
        "co_firstlineno",
        # "co_lnotab",  # 2.5.1 not 3.12
        'co_linetable',  # 3.12
        'co_exceptiontable',  # 3.12
        "co_freevars",
        "co_cellvars"
    ]

    new_code = types.CodeType(
        *[
            (getattr(original_code, x) if x != "co_consts" else new_consts)
            for x in code_type_args
        ]
    )
    return types.FunctionType(new_code, {})


def test_funcs_can_patch_inner_func_by_replacing_co_const() -> None:
    _code = test_funcs_inner_shadows_outer.__code__
    print(dir(_code))
    print(f'{len(_code.co_consts)=}')
    print(f'{_code.co_consts=}')

    # one line of code to patch inner func with fake
    fake_test_func: types.FunctionType = monkey_patch_fn(test_funcs_inner_shadows_outer, 'func_to_shadow', func_to_shadow)

    # inspect the fake
    print(f'{fake_test_func.__code__.co_consts=}')

    assert 'func_to_shadow' in str(fake_test_func.__code__.co_consts[2])
    assert func_to_shadow.__code__ == fake_test_func.__code__.co_consts[2]

    source, line_no = inspect.getsourcelines(fake_test_func.__code__.co_consts[2])
    print(f'\n{line_no=}')
    for line in source:
        print(line, end='')

    # ACT
    fake_test_func()  # should not throw assert 42 != 43

    print('\n> Patching inner func is possible, but not practicle. Use sparingly!\n')

# endregion test_funcs_can_patch_inner_func_by_replacing_co_const
