from adapters.eventbrite import EventbriteAdapter
from adapters.library_vic import VicLibraryAdapter


def test_eventbrite_interface():
    a = EventbriteAdapter()
    assert a.name == "eventbrite"


def test_library_interface():
    a = VicLibraryAdapter()
    assert a.name == "vic_library"

