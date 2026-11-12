import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from main import normalise, component_counts

class TransformTests(unittest.TestCase):
    def test_normalise_with_fields(self):
        item = {'odiNumber': 123, 'components': 'ELECTRICAL SYSTEM', 'summary': 'Test'}
        out = normalise(item, 'toyota', 'camry', 2018)
        self.assertEqual(out['odi_number'], '123')
        self.assertEqual(out['component'], 'ELECTRICAL SYSTEM')

    def test_missing_fields_do_not_break(self):
        out = normalise({}, 'toyota', 'camry', 2018)
        self.assertEqual(out['model_year'], '2018')
        self.assertEqual(out['summary'], '')

    def test_component_counts_sorted(self):
        rows = [{'component': 'ENGINE'}, {'component': 'BRAKES'}, {'component': 'ENGINE'}]
        counts = component_counts(rows)
        self.assertEqual(counts[0], {'component': 'ENGINE', 'report_count': 2})

if __name__ == '__main__':
    unittest.main()
