import sys

try:
    import relics
    print("Import relics: OK")
    
    from relics.character.ironclad import BurningBlood
    print("Import BurningBlood: OK")
    
    print(f"BurningBlood class: {BurningBlood}")
    
    from utils.registry import get_registered
    relic_class = get_registered("relic", "BurningBlood")
    print(f"Registry lookup: {relic_class}")
    
    if relic_class:
        print(f"Registry class name: {relic_class.__name__}")
    else:
        print("Relic not found in registry!")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)