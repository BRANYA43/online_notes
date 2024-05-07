from time import time

from selenium_tests import FunctionalTestCase, wait


class FunctionalTestCaseTest(FunctionalTestCase):
    def test_wait_decorator_doesnt_raise_error_and_returns_result_of_passed_func(self):
        @wait()
        def foo():
            return 1

        self.assertEqual(foo(), 1)

    def test_wait_decorator_raises_error_through_5_sec_if_passed_func_raises_error(self):
        @wait()
        def foo():
            self.fail('Fail!')

        start = time()
        self.assertRaises(
            AssertionError,
            foo,
        )
        end = time()

        self.assertAlmostEqual(end - start, 5, delta=0.5)

    def test_wait_for_method_doesnt_raise_error_and_returns_result_of_passed_func(self):
        def foo():
            return 1

        result = self.wait_for(lambda: foo())
        self.assertEqual(result, 1)

    def test_wait_for_method_raises_error_through_5_sec_if_passed_func_raises_error(self):
        start = time()
        self.assertRaises(
            AssertionError,
            self.wait_for,
            lambda: self.fail('Fail!'),
        )
        end = time()

        self.assertAlmostEqual(end - start, 5, delta=0.5)

    def test_wait_for_method_returns_result_if_expected_value_is_equal_fn_result(self):
        def foo():
            return 1

        result = self.wait_for(foo, expected_value=1)
        self.assertEqual(result, 1)

    def test_wait_for_method_raises_error_if_expected_value_isnt_equal_fn_result(self):
        def foo():
            return 2

        self.assertRaises(
            AssertionError,
            self.wait_for,
            foo,
            expected_value=1,
        )

    def test_wait_for_method_returns_result_if_included_value_is_in_returned_result(self):
        def foo():
            return 'Hello World!'

        result = self.wait_for(foo, included_value='World')
        self.assertEqual(result, foo())

    def test_wait_for_method_raises_error_if_included_value_isnt_in_returned_result(self):
        def foo():
            return 'Hello World!'

        self.assertRaises(
            AssertionError,
            self.wait_for,
            foo,
            included_value='non existent value',
        )
