"""Command-line entry point for building the deck."""

from .build import build_deck


def main() -> None:
    build_deck()
