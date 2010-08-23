import unittest

from merlin.tests.fixtures.testproject.forms import *
from merlin.wizards.utils import *


class UtilsTestCase(unittest.TestCase):
    def test_init_with_no_params(self):
        state = WizardState()

        self.assertIsNone(state.steps)
        self.assertIsNone(state.current_step)
        self.assertIsNone(state.form_data)

    def test_init_with_params(self):
        step1 = Step('step1', ContactDetailsForm)
        step2 = Step('step2', UserDetailsForm)

        state = WizardState(steps=[step1, step2], current_step=step1,
            form_data={})

        self.assertListEqual(state.steps, [step1, step2])
        self.assertEqual(state.current_step, step1)
        self.assertDictEqual(state.form_data, {})
