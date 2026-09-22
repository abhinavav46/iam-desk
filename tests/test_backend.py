"""Unit tests that need no local model running: retriever, tools, and the Flask API's
tool/knowledge-base paths. Run with:  python -m pytest tests -q  (or python -m unittest)
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import tools
from backend.retriever import Retriever
from backend import config


class TestRetriever(unittest.TestCase):
    def setUp(self):
        self.r = Retriever(config.KNOWLEDGE_DIR)

    def test_loads_chunks(self):
        stats = self.r.stats()
        self.assertGreater(stats["documents"], 0)
        self.assertGreater(stats["chunks"], 0)

    def test_finds_saml_oidc(self):
        hits = self.r.search("difference between SAML and OIDC", k=3)
        self.assertTrue(hits)
        joined = " ".join(h.chunk.text.lower() for h in hits)
        self.assertIn("saml", joined)

    def test_alias_expansion_jml(self):
        hits = self.r.search("explain JML process", k=3)
        self.assertTrue(hits)

    def test_irrelevant_query_returns_little_or_nothing(self):
        hits = self.r.search("best pizza toppings in naples", k=3)
        for h in hits:
            self.assertGreaterEqual(h.relevance, 0.35)


class TestJwtTool(unittest.TestCase):
    def test_rejects_malformed(self):
        out = tools.decode_jwt("not.a.jwt.token")
        self.assertIn("does not look like a JWT", out)

    def test_decodes_valid_looking_token(self):
        # header {"alg":"HS256","typ":"JWT"} / payload {"sub":"1","exp":9999999999}
        token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxIiwiZXhwIjo5OTk5OTk5OTk5fQ."
            "sig"
        )
        out = tools.decode_jwt(token)
        self.assertIn("HS256", out)
        self.assertIn("Expires", out)

    def test_flags_alg_none(self):
        import base64, json

        def b64(d):
            return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")

        token = b64({"alg": "none"}) + "." + b64({"sub": "x"}) + "."
        out = tools.decode_jwt(token)
        self.assertIn("Critical", out)

    def test_find_jwt_in_sentence(self):
        text = "here is my token eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.abc ok?"
        self.assertIsNotNone(tools.find_jwt(text))


class TestSodTool(unittest.TestCase):
    def test_detects_vendor_payment_conflict(self):
        out = tools.sod_check("Create Vendor, Approve Payment")
        self.assertIn("conflict", out.lower())

    def test_no_conflict_for_unrelated_list(self):
        out = tools.sod_check("Read Reports, View Dashboard")
        self.assertIn("No conflicts", out)

    def test_empty_input(self):
        out = tools.sod_check("   ")
        self.assertIn("Give me a list", out)


class TestCommandDispatch(unittest.TestCase):
    def test_help(self):
        self.assertIn("Commands", tools.run_command("/help"))

    def test_non_command_returns_none(self):
        self.assertIsNone(tools.run_command("what is SAML?"))

    def test_unknown_command(self):
        out = tools.run_command("/frobnicate")
        self.assertIn("don't know the command", out)


if __name__ == "__main__":
    unittest.main()
