#!/usr/bin/env python3
"""Tests for repository scope, filters, and recency ordering."""

import unittest
from unittest.mock import patch

import update_stack


def repo(name="project", **overrides):
    value = {
        "name": name,
        "owner": {"login": "yeraylois"},
        "fork": False,
        "archived": False,
        "disabled": False,
        "private": False,
        "description": "",
        "topics": [],
        "language": "Python",
        "pushed_at": "2026-07-18T12:00:00Z",
    }
    value.update(overrides)
    return value


class RepositoryFilterTests(unittest.TestCase):
    def test_only_active_owned_non_profile_repositories_are_eligible(self) -> None:
        self.assertTrue(update_stack.is_eligible_repo(repo()))
        self.assertFalse(update_stack.is_eligible_repo(repo("yeraylois")))
        self.assertFalse(update_stack.is_eligible_repo(repo(fork=True)))
        self.assertFalse(update_stack.is_eligible_repo(repo(archived=True)))
        self.assertFalse(update_stack.is_eligible_repo(repo(disabled=True)))
        self.assertFalse(
            update_stack.is_eligible_repo(repo(owner={"login": "someone-else"}))
        )

    def test_private_token_uses_authenticated_owner_endpoint(self) -> None:
        public = repo("public-project", id=1)
        private = repo("private-project", id=2, private=True)
        fork = repo("fork", id=3, fork=True)

        def response(url, token=""):
            if url.startswith("https://api.github.com/user/repos?"):
                return [private, public]
            return [public, fork]

        with (
            patch.object(update_stack, "STACK_TOKEN", "private-token"),
            patch.object(update_stack, "api_request", side_effect=response) as request,
        ):
            repositories = update_stack.fetch_all_repos()

        calls = request.call_args_list
        self.assertEqual(2, len(calls))
        private_url, private_token = calls[1].args
        self.assertTrue(private_url.startswith("https://api.github.com/user/repos?"))
        self.assertIn("visibility=all", private_url)
        self.assertIn("affiliation=owner", private_url)
        self.assertEqual("private-token", private_token)
        self.assertEqual(
            ["public-project", "private-project"],
            [item["name"] for item in repositories],
        )

    def test_missing_private_token_uses_public_owner_endpoint(self) -> None:
        with (
            patch.object(update_stack, "STACK_TOKEN", ""),
            patch.object(update_stack, "api_request", return_value=[]) as request,
        ):
            update_stack.fetch_all_repos()

        url, token = request.call_args.args
        self.assertTrue(url.startswith("https://api.github.com/users/yeraylois/repos?"))
        self.assertIn("type=owner", url)
        self.assertEqual("", token)


class DetectionTests(unittest.TestCase):
    def test_newer_language_is_not_displaced_by_an_older_framework(self) -> None:
        repositories = [
            repo("new", language="Python", pushed_at="2026-07-18T12:00:00Z"),
            repo(
                "old-docker",
                description="Docker container",
                language="C",
                pushed_at="2026-06-01T12:00:00Z",
            ),
        ]
        stack = update_stack.get_recent_stack(repositories, limit=3)
        self.assertEqual("Python", stack[0][0])

    def test_git_and_arch_do_not_match_inside_unrelated_words(self) -> None:
        detected = update_stack.detect_frameworks(
            repo(name="profile", description="GitHub architectures showcase")
        )
        self.assertNotIn("Git", detected)
        self.assertNotIn("Arch", detected)


if __name__ == "__main__":
    unittest.main()
