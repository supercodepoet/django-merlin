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

    def test_step_object_methods(self):
        step1 = Step('step1', ContactDetailsForm)
        step1_copy = Step('step1', UserDetailsForm)
        step2 = Step('step2', UserDetailsForm)

        self.assertRaises(ValueError, Step, 'step1', Step)

        self.assertTrue(step1 == step1_copy)
        self.assertFalse(step1 == step2)
        self.assertFalse(step1 == 'step1')
        self.assertTrue(step1 != step2)
        self.assertFalse(step1 != step1_copy)

        self.assertEquals(str(step1), 'step1')
        self.assertEquals(unicode(step1), u'step1')

        self.assertEquals('Step: %s' % repr(step1), 'Step: step1')

    def test_wizard_expansion(self):
        state = WizardState()

        if not hasattr(state, 'test_param'):
            state.test_param = 'Test'

        self.assertEquals(state.test_param, 'Test')            

        state.test_param = 'Test 2'

        self.assertEquals(state.test_param, 'Test 2')

        state = WizardState()
        state.another_param = 'Another Test'

        if not hasattr(state, 'another_param'):
            self.fail('We should have the param')

        else:
            self.assertEquals(state.another_param, 'Another Test')
