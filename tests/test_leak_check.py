"""Tests for scripts/leak_check.py. Run: python3 -m unittest discover tests"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import leak_check  # noqa: E402


def rules(*terms):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n".join(terms))
    os.environ["ROBO_DENYLIST"] = f.name
    return leak_check.load_denylist()


class DenylistTests(unittest.TestCase):
    def test_whole_word_and_case_insensitive(self):
        deny = rules("Zorblat", "re:\\bproject-?x\\b")
        self.assertTrue(leak_check.scan_text("f", "met zorblat today", deny))
        self.assertTrue(leak_check.scan_text("f", "about Project-X", deny))
        self.assertFalse(leak_check.scan_text("f", "zorblatter is a different word", deny))

    def test_output_does_not_echo_private_term(self):
        deny = rules("Zorblat")
        findings = leak_check.scan_text("f", "Zorblat", deny)
        self.assertNotIn("Zorblat", " ".join(findings))

    def test_missing_denylist_fails_closed(self):
        os.environ["ROBO_DENYLIST"] = "/nonexistent/denylist.txt"
        with self.assertRaises(SystemExit) as ctx:
            leak_check.load_denylist()
        self.assertEqual(ctx.exception.code, 2)


class BuiltinPatternTests(unittest.TestCase):
    def setUp(self):
        self.deny = rules("placeholder-term-unused")

    def flagged(self, text):
        return bool(leak_check.scan_text("f", text, self.deny))

    def test_blocks_real_looking_secrets(self):
        self.assertTrue(self.flagged("key = AKIA" + "Q" * 16))
        self.assertTrue(self.flagged("-----BEGIN " + "PRIVATE KEY-----"))
        self.assertTrue(self.flagged("token eyJhbGciOiJIUzI1" + ".eyJzdWIiOiIxMjM0.sig"))
        self.assertTrue(self.flagged("account 4" + "8" * 11))
        self.assertTrue(self.flagged("mail me at someone@" + "gmail.com"))
        self.assertTrue(self.flagged("server at 54.12." + "3.4"))

    def test_allows_documentation_placeholders(self):
        self.assertFalse(self.flagged("key = AKIAIOSFODNN7EXAMPLE"))
        self.assertFalse(self.flagged("account 123456789012"))
        self.assertFalse(self.flagged("robo@example.com"))
        self.assertFalse(self.flagged("listen on 127.0.0.1 or 192.0.2.10"))


class RepoIsCleanTest(unittest.TestCase):
    def test_whole_repo_passes_with_real_denylist(self):
        real = Path.home() / ".config/robo-pizza-qiaowei/denylist.txt"
        if not real.exists():
            self.skipTest("no local denylist on this machine")
        env = dict(os.environ, ROBO_DENYLIST=str(real))
        result = subprocess.run([sys.executable, "scripts/leak_check.py", "--all"],
                                cwd=ROOT, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
