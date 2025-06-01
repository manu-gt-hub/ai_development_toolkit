# 🚀 Script Optimizer

Automatically optimizes Python scripts either **online** (via OpenAI API) or **offline** using local models. It refactors code for readability, structure, and performance, while generating unit tests for each function.

## Features
- Refactors Python code with rules:
1. Use proper Python docstrings (PEP 257) for every function.
2. Remove unused imports and dead code.
3. Replace redundant or repeated logic with reusable functions if appropriate.
4. Use meaningful and descriptive names for all variables and functions.
5. Add error handling with try/except blocks where needed.
6. Ensure that all pandas and numpy operations are optimized and vectorized.
7. Organize the logic into separate functions or classes as needed.
8. Ensure PEP 8 style compliance.
9. Ensure the script is fully self-contained, with all necessary imports and definitions.
- Adds meaningful comments and docstrings.
- Detects and removes unused code and imports.
- Suggests optimizations for loops and vectorized operations.
- Generates unit tests for each function.
- Supports online (LLM-based) and offline execution modes.