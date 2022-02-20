from aiogram.dispatcher.filters.state import State, StatesGroup


# ___
class CollectionCreation(StatesGroup):
    waiting_for_archive = State()
