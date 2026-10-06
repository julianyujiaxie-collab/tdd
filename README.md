# tdd

## Environment and tests

`environment.yml` is a portable export of the `swe4s` environment. It pins
Python, the directly installed Conda packages, and all pip packages to their
installed versions. Local paths and macOS system-library builds are omitted
so the environment can also be created on Linux.

Create and activate the environment:

```bash
micromamba create -f environment.yml
micromamba activate swe4s
```

Run all tests from the repository root:

```bash
PYTHONPATH=src python -m unittest discover -s test/unit -p 'test_*.py' -v
```

```bash
status=0
for test_script in test/func/test_*.sh; do
    PYTHON=python bash "$test_script" || status=1
done
(exit "$status")
```

The functional tests download `ssshtest` when needed and clean up their
temporary data and images. GitHub Actions recreates `swe4s` from
`environment.yml` and runs both test suites on pushes and pull requests.

## Data

```
curl -L "https://docs.google.com/uc?export=download&id=1AsXP_OGs1O_TDeXiZjk3fYV1SrG4vwXF" -o data/Agrofood_co2_emission.csv
curl -L "https://docs.google.com/uc?export=download&id=19YEPysdnK7VCXuAe9Og9pwYkNT5CbQzr" -o data/IMF_GDP.csv
```
