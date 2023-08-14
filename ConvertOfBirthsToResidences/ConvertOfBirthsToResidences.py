from gramps.gen.db import DbTxn
from gramps.gen.lib import EventType, Place, PlaceName
from gramps.gui.plug import tool

class ConvertOfBirthsToResidencesOptions(tool.ToolOptions):
    def __init__(self, name):
        tool.ToolOptions.__init__(self, name)
        self.options_dict = {}
        self.options_help = {}

class ConvertOfBirthsToResidences(tool.Tool):
    def __init__(self, dbstate, user, options_class, name, callback=None):
        tool.Tool.__init__(self, dbstate, options_class, name)
        self.db = dbstate.get_database()
        self.convert_events()

    def convert_events(self):
        for place in self.db.iter_places():
            if place.get_name().value.startswith("of "):
                self.convert_events_at(place)

    def convert_events_at(self, of_place):
        with DbTxn("Convert events", self.db) as txn:
            canonical_place = self.without_of(of_place, txn)
            for handle_tuple in self.db.find_backlink_handles(
                                    of_place.get_handle()):
                event = self.db.get_event_from_handle(handle_tuple[1])
                event.set_type(EventType.RESIDENCE)
                event.set_place_handle(canonical_place.get_handle())
                self.db.commit_event(event, txn)
            self.db.remove_place(of_place.get_handle(), txn)

    def without_of(self, of_place, txn):
        name_without_of = of_place.get_name().value[3:]
        existing_place = next(
            filter(lambda existing_place:
		       existing_place.get_title() == name_without_of,
                   self.db.iter_places()),
            None)
        if existing_place:
            return existing_place
        new_place = Place()
        new_place.set_name(PlaceName(value=name_without_of))
        new_place.set_title(name_without_of)
        self.db.add_place(new_place, txn)
        return new_place
