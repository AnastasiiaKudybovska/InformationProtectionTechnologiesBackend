import unittest
import coverage

if __name__ == '__main__':
    cov = coverage.Coverage()

    cov.start()

    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)

    cov.stop()
    cov.report()
