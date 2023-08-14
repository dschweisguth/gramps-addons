import re

from gramps.gen.db import DbTxn
from gramps.gen.lib import Citation, Note, NoteType, Source
from gramps.gui.plug import tool

class ConvertPersonNotesToCitationsOptions(tool.ToolOptions):
    def __init__(self, name):
        tool.ToolOptions.__init__(self, name)
        self.options_dict = {}
        self.options_help = {}

class ConvertPersonNotesToCitations(tool.Tool):
    def __init__(self, dbstate, user, options_class, name, callback=None):
        tool.Tool.__init__(self, dbstate, options_class, name)
        self.db = dbstate.get_database()
        self.convert_notes()

    def convert_notes(self):
        for person in self.db.iter_people():
            for note_handle in person.get_note_list():
                person_note = self.db.get_note_from_handle(note_handle)
                if self.convert_personal_knowledge_note(person, person_note):
                    pass
                elif self.convert_document_note(person, person_note):
                    pass

    def convert_personal_knowledge_note(self, person, person_note):
        source_title = "Personal knowledge"
        text = person_note.get()
        match = re.match(f"{source_title}:\\s*(.*)", text)
        if not match:
            return False
        citation_note_text = match.group(1)
        self.convert_note(person, person_note, source_title, source_title,
                          citation_note_text)
        return True

    def convert_document_note(self, person, person_note):
        text = person_note.get()
        match = re.match(r"(?:(.*?),\s*)?(D?S\d+)(?:\s*\((.*?)\))?:\s*(.*)",
                         text)
        if not match:
            return False
        [source_desc, source_id, date, citation_note_text] = match.groups()
        source_id = self.zero_filled(source_id)
        source_title_prefix = f"{source_id},"
        source_title = source_id
        if source_desc:
            source_title += ", " + source_desc
        if date:
            source_title += ", " + date
        self.convert_note(person, person_note, source_title_prefix,
                          source_title, citation_note_text)
        return True

    def zero_filled(self, source_id):
        match = re.match(r"(D?S)(\d+)", source_id)
        if not match:
            raise ValueError(f"Can't parse source ID '{source_id}'")
        [prefix, number] = match.groups()
        # S = "source", i.e. paper source, of which there are 200-some,
        # and of which there won't be many more as paper is used less and less
        # DS = "digital source", of which there are 2000-some
        zero_filled_length = 3 if prefix == 'S' else 4
        return f"{prefix}{number.zfill(zero_filled_length)}"
    
    def convert_note(self, person, person_note, source_title_prefix,
                     source_title, citation_note_text):
        with DbTxn("Convert note", self.db) as txn:
            source = self.source(source_title_prefix, source_title, txn)

            citation_note = Note(citation_note_text)
            citation_note.set_type(NoteType.CITATION)
            self.db.add_note(citation_note, txn)

            citation = Citation()
            citation.set_reference_handle(source.handle)
            citation.add_note(citation_note.handle)
            self.db.add_citation(citation, txn)

            person.add_citation(citation.handle)
            person.remove_note(person_note.handle)
            self.db.commit_person(person, txn)

            self.db.remove_note(person_note.handle, txn)
    
    def source(self, source_title_prefix, source_title, txn):
        source = next(
            filter(lambda source:
                       source.get_title().startswith(source_title_prefix),
                   self.db.iter_sources()),
            None)
        if not source:
          source = Source()
          source.set_title(source_title)
          self.db.add_source(source, txn)
        return source
