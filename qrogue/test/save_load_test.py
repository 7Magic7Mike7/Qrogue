import sys

from qrogue.management import SaveData
from qrogue.test import test_util
from qrogue.util import achievements

user_data_path = sys.argv[1]
test_util.init_singletons(include_config=True, custom_user_path=user_data_path)
sv = SaveData()
print(sv.achievement_manager.to_string())

sv.achievement_manager.finished_level("l1v1")
sv.achievement_manager.add_to_achievement(achievements.CompletedExpedition, 1)
sv.achievement_manager.progressed_in_story(achievements.FinishedTutorial)
print(sv.achievement_manager.to_string())

sv.save()
