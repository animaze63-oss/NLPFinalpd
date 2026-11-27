# pytest

Sources: https://docs.pytest.org/en/stable/how-to/parametrize.html, https://docs.pytest.org/en/stable/how-to/fixtures.html

## Parametrize
```python
@pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6),
                         pytest.param("6*9", 42, marks=pytest.mark.xfail)])
def test_eval(test_input, expected):
    assert eval(test_input) == expected

@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", [2, 3])      # stacked → all 4 combinations
def test_foo(x, y): ...
```
Discovery: files `test_*.py`. Flags: `-q` quiet, `-x` stop at first failure, `-k expr` select by name.

## Fixtures and scope
> "Possible values for scope are: function, class, module, package or session." Default is function.
> "Fixtures are created when first requested by a test, and are destroyed based on their scope… session: the fixture is destroyed at the end of the test session."

Put shared fixtures in `conftest.py` "so that tests from multiple test modules in the directory can access the fixture function."

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def nlp():
    import spacy
    return spacy.load("en_core_web_sm")      # load once per run

@pytest.fixture(scope="session")
def sia():
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    return SentimentIntensityAnalyzer()
```
Yield fixtures (recommended for teardown): code after `yield` runs at teardown, in reverse order. Use the built-in `tmp_path` for files written by the pipeline under test.
