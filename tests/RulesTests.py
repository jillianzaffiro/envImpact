import unittest
from parameterized import parameterized
from RulesEngine.RulesEngine import RulesEngine, Fact, Rule


class FactsTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_can_create_unary_fact(self):
        # Arrange

        # Act
        f = Fact("bridge_width", 3)

        # Assert
        self.assertIsNotNone(f)

    def test_can_create_binary_fact(self):
        # Arrange

        # Act
        f = Fact("contains", "bridge", "concrete")

        # Assert
        self.assertIsNotNone(f)

    def test_can_add_facts_to_engine(self):
        # Arrange
        e = RulesEngine()
        f = Fact("has", "road", "length")

        # Act
        e.add_fact(f)

        # Assert
        self.assertEqual(1, e.fact_count())

    def test_can_get_fact_from_engine(self):
        # Arrange
        e = RulesEngine()
        f = Fact("has", "road", "length")
        e.add_fact(f)

        # Act - What does a road have?
        r = e.query('has', 'road')

        # Assert
        self.assertEqual(1, len(r))
        r1 = r[0]
        self.assertEqual("length", r1)

    def test_can_get_chained_fact_from_engine(self):
        # Arrange
        e = RulesEngine()
        e.add_fact(Fact("has", "road", "length"))
        e.add_fact(Fact("has", "city", "road"))

        # Act - What does a city have?
        r = e.query('has', 'city')

        # Assert
        self.assertEqual(2, len(r))
        self.assertEqual("road", r[0])
        self.assertEqual("length", r[1])

    def test_get_nothing_from_engine_if_no_fact(self):
        # Arrange
        e = RulesEngine()
        e.set_default_behavior("default_string")

        # Act
        r = e.query('has', 'house')

        # Assert
        self.assertEqual(0, len(r))

    def test_get_nothing_from_engine_if_mismatched_fact(self):
        # Arrange
        e = RulesEngine()
        f = Fact("has", "road", "length")
        e.add_fact(f)

        # Act
        r = e.query('has', 'house')

        # Assert
        self.assertEqual(0, len(r))

    @parameterized.expand([
        ("put None, don't default, get None", False, "size", "size", None),
        ("put None, default, get default", True, "size", "size", "large"),
    ])
    def test_can_get_default_if_set(self, name, none_default, name_to_put, name_to_get, expected_value):
        # Arrange
        e = RulesEngine()
        e.set_default_behavior("large", replace_none_with_default=none_default)
        e.add_fact(Fact("has_value", name_to_put, None))

        # Act
        r = e.query('has_value', name_to_get)

        # Assert
        self.assertEqual(1, len(r))
        self.assertEqual(expected_value, r[0])

    @parameterized.expand([
        ("put None, don't default but ask for size2, get nothing", False),
        ("put None, default but ask for size2, still get nothing", True),
    ])
    def test_can_get_none_when_default_set(self, name, none_default):
        # Arrange
        e = RulesEngine()
        e.set_default_behavior("large", replace_none_with_default=none_default)
        e.add_fact(Fact("has_value", "road", None))

        # Act
        r = e.query('has_value', "house")

        # Assert
        self.assertEqual(0, len(r))

    def test_can_infer_simple_relation(self):
        # Arrange
        e = RulesEngine()
        e.add_fact(Fact("is_bigger", "B", "A"))

        # Act "What is bigger than A?"
        res = e.query_post("is_bigger", "A")

        # Assert
        self.assertEqual(1, len(res))
        self.assertEqual("B", res[0])

    def test_can_infer_chained_relation(self):
        # Arrange
        e = RulesEngine()
        e.add_fact(Fact("is_bigger", "B", "A"))
        e.add_fact(Fact("is_bigger", "C", "B"))

        # Act "What is better than A?"
        res = e.query_post("is_bigger", "A")

        # Assert
        self.assertEqual(2, len(res))
        self.assertEqual("B", res[0])
        self.assertEqual("C", res[1])


class RulesTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_can_add_rules_to_engine(self):
        # Arrange
        e = RulesEngine()
        r = Rule("width = lanes * lane_width")

        # Act
        e.add_rule(r)

        # Assert
        self.assertEqual(1, e.rule_count())

    def test_can_calculate_if_default(self):
        # Arrange
        e = RulesEngine()
        e.add_fact(Fact("has_value", "lanes", 4))
        e.add_fact(Fact("has_value", "lane_width", 10))
        e.add_rule(Rule("width = lanes * lane_width"))

        # Act
        res = e.query("has_value", "width")

        # Assert
        self.assertEqual(1, len(res))
        self.assertEqual(40, res[0])

    def test_can_calculate_chained(self):
        # Arrange
        e = RulesEngine()
        e.add_fact(Fact("has_value", "lanes", 4))
        e.add_fact(Fact("has_value", "lane_width", 10))
        e.add_fact(Fact("has_value", "depth", 0.5))
        e.add_rule(Rule("width = lanes * lane_width"))
        e.add_rule(Rule("volume = width * depth"))

        # Act
        res = e.query("has_value", "volume")

        # Assert
        self.assertEqual(1, len(res))
        self.assertEqual(20.0, res[0])
