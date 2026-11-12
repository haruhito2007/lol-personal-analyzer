import shutil
import subprocess
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
NODE_PATH = shutil.which("node")


@unittest.skipUnless(NODE_PATH, "Node.js is not available")
class FrontendJavaScriptTest(unittest.TestCase):
    def test_ui_state_transitions_with_mock_fetch(self):
        result = subprocess.run(
            [NODE_PATH, "--test", "tests/js_ui_test.js"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=f"{result.stdout}\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
