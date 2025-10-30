# Deprecated / Original Test Files

This directory contains the original versions of media entertainment test files before the modularization refactoring, plus deprecated tests.

## Original Files (Pre-Refactoring)

- `test_spotify_original.py` - Original Spotify test (230 lines)
- `test_tmdb_original.py` - Original TMDb test (206 lines)
- `test_youtube_original.py` - Original YouTube test (249 lines)
- `test_openlibrary_original.py` - Original Open Library test (204 lines)

## Deprecated Tests

- `test_openlibrary.py` - **DEPRECATED** Open Library test (refactored version, moved here)
  - Reason: Open Library API removed from framework (see GEMINI.md)
  - No longer actively maintained or run
  - Kept for historical reference only

## Purpose

These files are preserved for:
- Reference during debugging
- Comparison with refactored versions
- Historical context
- Rollback if needed

## Refactoring Summary

The refactoring (completed 2025-10-30) introduced:

1. **`test_configs/` folder**: Centralized test configurations
   - Easy to add new test cases without touching code
   - Clean separation of data and logic

2. **`media_utils.py`**: Shared utility functions
   - Environment & authentication management
   - Config management
   - Result building helpers
   - Display functions
   - Test execution patterns

3. **Refactored test files**: Cleaner, more maintainable code
   - Reduced code duplication by 20-30%
   - Consistent patterns across all test files
   - New test cases added (理芽, Leonardo DiCaprio, Mori Calliope, Arthur C. Clarke)

## Do Not Use

These files should **not** be used for running tests. They are kept only for reference.

Use the refactored versions in the parent directory instead.
