import pytest
from systemd import *


# def pytest_addoption(parser):
#     parser.addoption(
#         "-E",
#         action="store",
#         metavar="NAME",
#         help="only run tests matching the environment NAME.",
#     )

# def pytest_configure(config):
#     config.addinivalue_line(
#         "markers", "env(name): mark test to run only on named environment"
#     )


# def pytest_runtest_setup(item):
#     envnames = [mark.args[0] for mark in item.iter_markers(name="env")]
#     if envnames:
#         if item.config.getoption("-E") not in envnames:
#             pytest.skip("test requires env in {!r}".format(envnames))


# available markers
#skip - always skip a test function
#skipif - skip a test function if a certain condition is met
#xfail - produce an “expected failure” outcome if a certain condition is met
#parametrize to perform multiple calls to the same test function.
#@pytest.fixture(scope="module")
#@pytest.fixture(scope="session")
#@pytest.fixture(scope="package")
#@pytest.fixture
#def sd():
#    s = Systemd()
#    return s

#@pytest.mark.skip
#def test_skipped():
#    assert 0
#
# pytest will create tmpdir for us
# def test_needsfiles(tmpdir, tmp_path, capsys, sd):
#     print(tmpdir)
#     print(tmp_path)
#     print(capsys)
#     print(sd)
#     captured=capsys.readouterr()
#     print("capsys.out:"+captured.out)
#     #with capsys.disabled():
#     #    print("output not captured, going directly to sys.stdout")
#     assert True

# @pytest.mark.env("stage1")
# def test_another():
#     pass


# class TestClass:
#     def test_method(self):
#         pass

# def f():
#     raise SystemExit(1)

# def test_mytest():
#     with pytest.raises(SystemExit):
#         f()



# def test_zero_division():
#     with pytest.raises(ZeroDivisionError):
#         1 / 0


# def test_recursion_depth():
#     with pytest.raises(RuntimeError) as excinfo:

#         def f():
#             f()

#         f()
#     assert "maximum recursion" in str(excinfo.value)


# def myfunc():
#     raise ValueError("Exception 123 raised")


# def test_match():
#     with pytest.raises(ValueError, match=r".* 123 .*"):
#         myfunc()

#pytest.raises(ExpectedException, func, *args, **kwargs)

# @pytest.mark.xfail(raises=IndexError)
# def test_f():
#     f()


# import warnings
# import pytest


# def test_warning():
#     with pytest.warns(UserWarning):
#         warnings.warn("my warning", UserWarning)
# The test will fail if the warning in question is not raised. The keyword argument match to assert that the exception matches a text or regex:

# >>> with warns(UserWarning, match='must be 0 or None'):
# ...     warnings.warn("value must be 0 or None", UserWarning)

# >>> with warns(UserWarning, match=r'must be \d+$'):
# ...     warnings.warn("value must be 42", UserWarning)

# >>> with warns(UserWarning, match=r'must be \d+$'):
# ...     warnings.warn("this is not here", UserWarning)
# Traceback (most recent call last):
#   ...
