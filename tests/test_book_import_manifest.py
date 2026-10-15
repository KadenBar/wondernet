import unittest

from scripts.validate_book_imports import validate


def book(**overrides):
    item = {
        "id": "new-book", "title": "New Book", "creator": "Example Author",
        "source_url": "https://example.org/edition",
        "rights": {"classification": "PD-US", "territory": "US", "license_url": "https://example.org/rights"},
        "gate": {k: "pending" for k in ("rights_review", "content_review", "accessibility_review", "package_review")},
        "import_status": "not-imported",
    }
    item.update(overrides)
    return item


class ManifestValidationTests(unittest.TestCase):
    def test_valid_staging_candidate(self):
        self.assertEqual(validate({"schema_version": 1, "items": [book()]}, []), [])

    def test_existing_book_rejected(self):
        result = validate({"schema_version": 1, "items": [book()]}, [{"title": "New Book", "creator": "Example Author"}])
        self.assertTrue(any("duplicate title" in error for error in result))

    def test_unreviewed_book_cannot_be_published(self):
        result = validate({"schema_version": 1, "items": [book(import_status="reviewed", sha256="a" * 64)]}, [])
        self.assertTrue(any("all gates approved" in error for error in result))

    def test_missing_checksum_rejected(self):
        result = validate({"schema_version": 1, "items": [book(import_status="staged")]}, [])
        self.assertTrue(any("SHA-256" in error for error in result))

    def test_fake_https_url_rejected(self):
        for source in ("https://", "https://example.org@/", "https://example.org\\n.evil.test"):
            result = validate({"schema_version": 1, "items": [book(source_url=source)]}, [])
            self.assertTrue(any("HTTPS" in error for error in result), source)

    def test_duplicate_within_batch_rejected(self):
        result = validate({"schema_version": 1, "items": [book(), book(id="another-book")]}, [])
        self.assertTrue(any("duplicate title" in error for error in result))

    def test_insecure_source_rejected(self):
        result = validate({"schema_version": 1, "items": [book(source_url="http://example.org")]}, [])
        self.assertTrue(any("HTTPS" in error for error in result))


if __name__ == "__main__":
    unittest.main()
