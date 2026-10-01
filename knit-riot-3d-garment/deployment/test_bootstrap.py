"""Mocked preflight tests; these do not claim to deploy or render the application."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch

BOOTSTRAP=Path(__file__).with_name('render_bootstrap.py')
PIN='ab0a34b4b0d4d35359b2c681b3c38cb3a8785562'

class BootstrapGuards(unittest.TestCase):
    def execute(self,env,actual):
        with patch.dict(os.environ,env,clear=False),patch('subprocess.run') as commands,patch('subprocess.check_output',return_value=actual+'\n'),patch('runpy.run_path') as execute:
            exec(compile(BOOTSTRAP.read_text(),str(BOOTSTRAP),'exec'),{'__name__':'__main__'})
            return commands.call_args_list,execute.call_args_list

    def test_requires_full_pin_before_any_process(self):
        with patch.dict(os.environ,{'KR_PROJECT_COMMIT':'main'}),patch('subprocess.run') as command:
            with self.assertRaisesRegex(RuntimeError,'full pinned'):
                exec(compile(BOOTSTRAP.read_text(),str(BOOTSTRAP),'exec'),{})
            command.assert_not_called()

    def test_mismatched_checkout_never_executes_build(self):
        with patch.dict(os.environ,{'KR_PROJECT_COMMIT':PIN}),patch('subprocess.run'),patch('subprocess.check_output',return_value='0'*40+'\n'),patch('runpy.run_path') as command:
            with self.assertRaisesRegex(RuntimeError,'verification failed'):
                exec(compile(BOOTSTRAP.read_text(),str(BOOTSTRAP),'exec'),{})
            command.assert_not_called()

    def test_pinned_checkout_and_scoped_entrypoint(self):
        commands,execution=self.execute({'KR_PROJECT_COMMIT':PIN},PIN)
        self.assertEqual(len(commands),3)
        self.assertEqual(commands[1].args[0][-1],PIN)
        self.assertEqual(commands[2].args[0][-1],PIN)
        self.assertTrue(execution[0].args[0].endswith('/knit-riot-3d-garment/tools/render_build.py'))
        self.assertEqual(execution[0].kwargs['run_name'],'__main__')

if __name__=='__main__':
    unittest.main()
