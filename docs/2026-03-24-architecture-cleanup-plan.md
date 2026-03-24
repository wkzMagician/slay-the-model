# Architecture Cleanup Execution Notes

Date: 2026-03-25
Branch: architecture-cleanup-task1

## Final Status
- Task 1: completed
- Task 2: completed
- Task 3: completed
- Task 4: completed
- Task 5: completed
- Task 6: completed
- Task 7: completed
- Task 8: completed after two follow-up fixes
- Task 9: completed after one follow-up fix
- Task 10: completed

## Notable Deviations
- Task 6 required one minimal adjacent production fix outside the original file list:
  - `actions/misc.py`
  - reason: route The Courier restock through shared shop-state helpers instead of duplicating logic.
- Task 8 required two support files not listed in the original slice:
  - `actions/base.py`
  - `actions/display.py`
  - reason: establish explicit runtime-event flush points outside domain action bodies.
- Task 9 added one support test not listed in the original slice:
  - `tests/test_run_game_test.py`
  - reason: lock the repaired standalone runner behavior.
- Task 10 required two production fixes discovered only during final verification:
  - `rooms/shop.py` compatibility export for `ShopItem`
  - non-interactive `--no-tui` fallback path in `__main__.py` / `engine/runtime_context.py`

## Final Verification
- Targeted verification suite:
  - `pytest -q tests/test_room_queue_cleanup.py tests/test_message_contracts.py tests/test_runtime_guardrails.py tests/test_shop_modules.py tests/test_runtime_output_decoupling.py`
  - result: `31 passed`
- Full repository:
  - `pytest -q`
  - result: `770 passed, 2 skipped`
- Runtime smoke:
  - `python __main__.py --no-tui`
  - result: exit code `0`, no `Game error`, no `EOF`

## End State Summary
- Room-local action queues removed.
- Message dispatch moved to explicit contracts and class-level subscriptions.
- Silent runtime compatibility fallbacks removed or made explicit.
- `actions/combat.py` and `actions/card.py` split by responsibility.
- Shop logic split into focused modules.
- `GameState` runtime responsibilities narrowed behind `RuntimeContext`.
- Runtime output emission decoupled from rendering via queued runtime events and explicit presenter flush.
- Implementation-bound tests shifted toward behavior assertions.
