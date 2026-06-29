import unittest

from src.application.log_generator import RandomHttpLogGenerator

class RandomHttpLogGeneratorTestCase(unittest.TestCase):
    def test_generated_line_has_four_parts(self)->None:
        generated=RandomHttpLogGenerator().generate()

        self.assertEqual(len(generated.line.split()), 4)


if __name__=="__main__":
    unittest.main()