==================================
Project Sack design specifications
==================================

-----------
Preferences
-----------

* Object dragging:
  * Left button drag sets association, right button drag moves object (i.e., to shelf)
  * Right button drag sets association, left button drag moves object

  Default should be the second option: left button dragging is usually associated with moving
  something.

* Show hidden fields: yes or no, no by default.
  Probably leading underscore should not be shown; other color should be used instead.

* Color and fonts scheme:
  * Main text style
  * Hidden field names
  * Object title (text on object control)

----------------
Object structure
----------------

Object field names can contain only letters, numbers, underscores and hyphens.
Root field should be a dictionary. Field names should start either from underscore or a letter.
Field names starting from underscore are considered hidden (will be shown only when corresponding
setting is enabled).

Hidden fields, undeleteable:
  * ``_Title`` (string; taken from display class's ``TitleTemplate`` if empty)
  * ``_Tags`` (points to list)
  * ``_DisplayClass`` (points to display class object; can be None only for root object;
    by default the corresponding default class from root object is used)

Display class objects
---------------------

Display class objects define how objects are displayed. They have the following fields:
  * ``TitleTemplate``: string, defining how title is composed
  * ``FieldsOrder``: nested lists, defining the order of fields on main window view;
    other fields are shown alphabetically.

Builtins
--------

Database initially contains the single root object, whose _DisplayClass equals to None.
It is a root object and it serves as a starting point when accessing the database. Full specification:

* ``_Title``: None
* ``_Tags``: None
* ``_DisplayClass``: None
* ``DisplayClasses``:
  * ``DisplayClass``: points to built-in display class object
  * ``Tag``: points to built-in tag class
  * ``Default``: points to built-in default display class

Built-in display classes
------------------------

Each Display class's ``_DisplayClass`` field points to the metaclass with the following contents:

* ``_DisplayClass``: points to self
* ``Title``: "Display class for display classes"
* ``TitleTemplate``: "$Title"
* ``FieldsOrder``:
  - "Title"
  - "TitleTemplate"
  - "FieldsOrder"

Display class for tags:

* ``Title``: "Display class for tags"
* ``TitleTemplate``: "$Title"
* ``FieldsOrder``:
  - "Title"
  - "Description"

Default display class:

* ``Title``: "Default display class"
* ``TitleTemplate``: "$Title"
* ``FieldsOrder``:
  - "Title"
  - "Data"

Title template
--------------

A string, containing pointers to object's fields prefixed by dollar signs. The value of the field
is inserted in place of each reference during display. Reference to object is resolved as the title
of this object (objects are memoized, so cyclic references are avoided).

Example: "$Artist - $Album - $Title".

--------------
User Interface
--------------

Menu bar + window per each opened database.
Currently windows cannot interconnect (like moving objects from one DB to another).

**FUTURE**: allow DB windows interconnection.

Object control
--------------

Object is represented by a custom control (at least, a label with colored border).
On diagrams it is shown as ``/Object/``.

Label text is taken from object's ``_Title`` field.

Context menu items for each object control:
* Copy to clipboard as YAML
* Open in new tab
* Open in current tab
* Move to shelf
* Delete

Each object can be dragged with left or right key pressed.

DB window
---------

____________________________________
| Database name                    |
|-----------------------------------
| Tag panel | Main window | Shelf  |
|           |             |        |
|___________|_____________|________|

Tag panel and shelf are hideable.

Tag panel
---------

_________________
| [ ] /Tag1/  |A|
| [ ] /Tag2/  |#|
| [ ] /Tag3/  |#|
| [ ] /Tag4/  | |
|             | |
|             | |
|             | |
|_____________|V|

Panel is filled with all objects whose ``_DisplayClass`` points to tag class.
