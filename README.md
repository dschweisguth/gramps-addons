# gramps-addons

## Requirements

- Gramps 5.1
- The version of Python bundled with the above version of Gramps, currently 3.11.4

## Installation

On MacOS,

    $ cp -r plugins/* ~/Library/Application\ Support/gramps/gramps51/plugins

On other OSes, copy the contents of this repo's plugins directory to the Gramps plugins directory, wherever that is on your OS.

## Usage

On MacOS,

    /Applications/Gramps.app/Contents/MacOS/Gramps -O "the name of your database" -a tool -p name=toolid

On other OSes, see [the Command Line section of the Gramps manual](https://gramps-project.org/wiki/index.php/Gramps_5.1_Wiki_Manual_-_Command_Line).

## Tools

### ConvertPersonNotesToCitations

This tool's ID is convert_person_notes_to_citations.

This tool does the one-time job of converting Person Notes containing citations (which is how I cited facts in the genealogical program I used previously) into Sources and Citations. It converts notes in either of the following two formats:

    Personal knowledge: (facts)

    (source title), (source ID) (date): (facts)

In the latter format,

- The source ID matches the regular expression `D?S\d+`. This ID refers to a real-world source in the researcher's possession (a physical document, prefixed with S, or a digital file, prefixed with DS), not to a GEDCOM or other database ID.
- The source title and date are optional.

The tool converts each note into

- a Source, titled "Personal knowledge" or "(source ID), (source title), (date)". It creates a single source for "Personal knowledge" and each source ID.
- a Citation, associated with the Person to whom the Note was attached and to the new Source, whose Volume/Page is the facts from the Person Note

It deletes each successfully converted Person Note.

### ConvertOfBirthsToResidences

This tool's ID is convert_of_births_to_residences.

This tool does the one-time job of converting Birth events in places with names beginning with "of " (which is how the genealogical program I used previously exported the fact that the place of origin given for a person is their residence, not their birthplace) to Residence events in places with unprefixed names.

It creates an unprefixed place for each "of " place if one doesn't already exist, and always deletes the "of " place.
